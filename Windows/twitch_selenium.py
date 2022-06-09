import datetime
import json
import os
import sys
import time
from click import argument
from selenium import webdriver
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from pyvirtualdisplay import Display
from tshark_dumps import *
import logging

from selenium.webdriver.remote.command import Command

today_date = datetime.datetime.now().date()
logger = ""


def hover(browser, xpath):
    element_to_hover_over = browser.find_element_by_xpath(xpath)
    hover = ActionChains(browser).move_to_element(element_to_hover_over)
    hover.perform()

def hover_over_video(driver):
    element_to_hover_over = driver.find_element(by=By.XPATH, \
        #FIREFOX:: value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]')
        value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[2]')
    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()
   

MAX_TRIALS = 40
MAX_FAILURES = 35 # max  no of trying if stat enabling fails
MAX_SNAPSHOTS = 180 # 1 per second -- 3 min

output_dic = {
    'static_data': {
        'backend_version': "",
        'serving_ID': "", 
        'codecs': "", 
        'playsession_ID': "",
        'protocol': ""
        },
    'qoe': []}
'''
Json structure:
{
    'static_data': {
        'backend_version':
        'serving_ID':
        'codecs':
        'playsession_ID':
        'protocol':
    }
    'qoe': []


}
'''

def get_status(driver):
    if driver:
        if not driver.window_handles:
            return True
        else:
            return False

def select_settings(driver):
    global logger
    if driver.session_id == None:
        return
    logger.info("select settings")
    succeeded = False
    for i in range (MAX_FAILURES):
        try :
            hover_over_video(driver)
            time.sleep(1)
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Settings']"))).click()
            # html = driver.page_source
            # soup = BeautifulSoup(html, "html.parser")
            # with open("html.html", "w", encoding="utf-8") as f:
            #     f.write(str(soup.prettify()))
            # setting_buttons = driver.find_element(by=By.XPATH, value='//div[@data-test-selector="settings-menu-button__animate-wrapper"')
            setting_buttons = driver.find_elements(by=By.XPATH, value='//button[@aria-label="Settings"]\
            //div[@class="ButtonIconFigure-sc-1ttmz5m-0 fbCCvx"]//div[@class="ScIconLayout-sc-1bgeryd-0 cXxJjc"]//div[@class="ScAspectRatio-sc-1sw3lwy-1 kPofwJ tw-aspect"]/*[name()="svg"]//*[name()="g"]/*[name()="path" and @d="M10 8a2 2 0 100 4 2 2 0 000-4z"]')
            logger.info(f"setting buttons -->type {type(setting_buttons)} len --> {len(setting_buttons)} {setting_buttons}")
            if len(setting_buttons) == 1:
                setting_buttons[0].click()
            elif len(setting_buttons) == 2:
                setting_buttons[1].click()
            succeeded = True
            break
        except Exception as e :
            logger.error(f"settings element not found in trial {i}")
            logger.error(e)

            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit()
    if not succeeded:
        logger.error("FAILED :(")
        driver.quit()

def select_advanced(driver):
    global logger

    logger.info("Selecting advanced")
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try :
            advanced = driver.find_element(by=By.XPATH, value="//button[@data-a-target='player-settings-menu-item-advanced']")
            logger.info(f"advanced--> type {type(advanced)} {advanced}")
            # if len(advanced) == 2:
            #     advanced[0].click()
            # else:
            advanced.click()
            logger.info("Succeeded")
            break
        except Exception as e :
            logger.warning(f"advanced element not found in trial {i}")
            logger.error(e)
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit()


def select_video_stat(driver):
    global logger
   
    logger.info("Selecting video stats")
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try:
            stats = driver.find_element(by=By.XPATH, value="//div[@data-a-target='player-settings-submenu-advanced-video-stats']")
            stats.click()
            logger.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logger.warning(f"enable stat element not found in trial {i}")
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit()

def select_latency(driver):
    global logger
   
    logger.info("Disable low latency")
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try:
            stats = driver.find_element(by=By.XPATH, value="//div[@data-test-selector='low-latency-toggle']")
            stats.click()
            logger.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logger.warning(f"enable stat element not found in trial {i}")
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit() 

def select_stat(driver):
    global logger
    # if not get_status(driver):
    #     return
    logger.info("Selecting stats")
    #Click on the stats window
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try:
            select_stats = driver.find_element(by=By.XPATH, value="//tbody[@class='tw-table-body']")
            select_stats.click()
            logger.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logger.warning(f"stat window not found in trial {i}")
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit() 
            

def collect_data(driver):
    global logger
    global output_dic

    output_dic = {
    'static_data': {
        'backend_version': "",
        'serving_ID': "", 
        'codecs': "", 
        'playsession_ID': "",
        'protocol': ""
        },
    'qoe': []}
    first_time = True
    trials_counter = 0
    snapshots_counter = 0
    # static_data = {}
    while snapshots_counter < MAX_SNAPSHOTS and trials_counter<MAX_TRIALS:

        #Extract data
        try:
            hover_over_video(driver)
            
            # html = driver.page_source
            # soup = BeautifulSoup(html, "html.parser")
            # with open("html.html", "w", encoding="utf-8") as f:
            #     f.write(str(soup.prettify()))
            # video_time = driver.find_element(by=By.XPATH, value="//div[@class='Layout-sc-nxg1ff-0 jQvkYY']//div[@class='Layout-sc-nxg1ff-0 dHrscT vod-seekbar-time-labels']//p[@data-a-target='player-seekbar-current-time']").text
            select_stats = driver.find_element(by=By.XPATH, value="//tbody[@class='tw-table-body']")
            table_html = select_stats.get_attribute("innerHTML")
            soup = BeautifulSoup(table_html, 'lxml')
            rows = soup.select('tr')
            snapshot_data = {}
            static_data = {}
            logger.info(f"size of rows {len(rows)}")
            for i, row in enumerate(rows):
                cols = row.find_all('td')
                if i < len(rows)-5:
                    snapshot_data[cols[0].find("p").text] = cols[1].find("p").text
                else:
                    if first_time:
                        # logger.info(f'{cols[0].find("p").text} is added to static ')
                        static_data[cols[0].find("p").text] = cols[1].find("p").text
            
            # snapshot_data["time"] = video_time

        except Exception as e :
            logger.error("can't extract data")
            logger.error(e)
            time.sleep(5)
            trials_counter += 1
            continue

        
        if first_time:
            logger.info("First time data stored")
            output_dic['static_data'] = static_data
            output_dic['qoe'].append(snapshot_data)
            first_time = False
            
            snapshots_counter +=1
            time.sleep(1)
            continue
        
        #compare with previous, if the same, it is an ad or network error
        logger.info(f"output_dic['qoe'][-1] :: {output_dic['qoe'][-1]}")
        logger.info(f"snapshot_data :: {snapshot_data}")
        if str(output_dic['qoe'][-1]) == str(snapshot_data):
            logger.warning("No change in data! Ads or buffering")
            logger.warning(f"Trials counter {trials_counter}")
            time.sleep(5)
            trials_counter += 1
            continue
        else:
            logger.info("Storing data in json object")
            output_dic['qoe'].append(snapshot_data)
            trials_counter = 0
            snapshots_counter +=1

        time.sleep(1)

def open_new_tab_close_old(driver, url):
    # close the tab
    driver.close()
    driver.execute_script(f"window.open('{url}');")
    # driver.switch_to.window(driver.window_handles[0])

def process_video(driver, video):
    global logger
    global output_dic

    # for i in range(2):
    #     #Create logger
    #     if i == 0:
    #         logFile = os.path.join(".", "Results", f"tw_{video}_low", "logs")
            
    #     else:
    #         logFile = os.path.join(".", "Results", f"tw_{video}_normal", "logs")

    logFile = os.path.join(".", "Results", f"tw_{video}", "logs")

    logger = createLog(logFile)

        #Start tshark
        # tsharkObj = tshark_dumps(video)
        # tsharkObj.start_tshark_process()
        # time.sleep(5)

    video_link = f'https://www.twitch.tv/videos/{video}/'
    # video_link = f"https://www.twitch.tv/{video}"
    file_name = os.path.join(".", "Results", f"tw_{video}", "qoe", f"{video}.json")

    # if i == 0:
    #     file_name = os.path.join(".", "Results", f"tw_{video}_low", "qoe", f"{video}.json")
    # else:
    #     file_name = os.path.join(".", "Results", f"tw_{video}_normal", "qoe", f"{video}.json")

    driver.get(video_link)
    driver.maximize_window()
    time.sleep(40)

    select_settings(driver)
    select_advanced(driver)
    # if i == 1:
    #     select_latency(driver)
    select_video_stat(driver)
    select_stat(driver)
    collect_data(driver)

    #Write down the qoe data
    output_dic["video_id"] = video
    output_file = open(file_name, 'w')
    json.dump(output_dic, output_file, indent=4)

    #Stop tshark
    # tsharkObj.end_tshark_process()
    # tsharkObj.process_capture()


def createLog(path):
    global logger
    logger = logging.getLogger("Sellog")   # > set up a new name for a new logger

    logger.setLevel(logging.DEBUG)  # here is the missing line

    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    filename = os.path.join(path, "selenium_log.log")
    if os.path.exists(filename):
        os.remove(filename)
    log_handler = logging.FileHandler(filename)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(log_format)

    logger.addHandler(log_handler)

    return logger

def startRetrivingData(video):
    print(f"Starting retriving for {video}")

    # Display size is random popular screen size
    # display = Display(visible=False, size=(1920, 1080))
    # display.start()

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu') 
    options.add_argument('--no-sandbox')
    # driver = webdriver.Firefox()
    driver = webdriver.Chrome("U:\programs\chromedriver_win32\chromedriver.exe", chrome_options=options)
    # options.BinaryLocation = "/usr/bin/chromium-browser"

    # driver = webdriver.Chrome(service=Service(),options=options)    
    process_video(driver, video)

    driver.quit()