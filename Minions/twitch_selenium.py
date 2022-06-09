import datetime
import json
import os
import time
from selenium import webdriver
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

logger = ""


def hover(browser, xpath):
    """
    Hover over an element by xpath
    """
    element_to_hover_over = browser.find_element_by_xpath(xpath)
    hover = ActionChains(browser).move_to_element(element_to_hover_over)
    hover.perform()

def hover_over_video(driver):
    """
    Hover a video in twitch
    """
    element_to_hover_over = driver.find_element(by=By.XPATH, \
        #FIREFOX:: value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]')
        value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[2]')
    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()
   

MAX_TRIALS = 40
MAX_FAILURES = 35 # max  no of trying if stat enabling fails
MAX_SNAPSHOTS = 180 # 1 per second -- 3 min

driver_state = False

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
    """
    Get driver status --> Function untested!
    """
    if driver:
        if not driver.window_handles:
            return True
        else:
            return False

def select_settings(driver):
    """
    Select settings button on the video
    """
    global logger
    global driver_state

    if driver.session_id == None or not driver_state:
        return
    logger.info("select settings")
    succeeded = False
    for i in range (MAX_FAILURES):
        try :
            hover_over_video(driver)
            time.sleep(1)
            
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
        driver_state = False

def select_advanced(driver):
    """
    Select Advanced button 
    """
    global logger
    global driver_state

    logger.info("Selecting advanced")
    if driver.session_id == None or not driver_state:
        return
    for i in range (MAX_FAILURES):
        time.sleep(1)
        try :
            advanced = driver.find_element(by=By.XPATH, value="//button[@data-a-target='player-settings-menu-item-advanced']")
            logger.info(f"advanced--> type {type(advanced)} {advanced}")

            advanced.click()
            logger.info("Succeeded")
            break
        except Exception as e :
            logger.warning(f"advanced element not found in trial {i}")
            logger.error(e)
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit()
                driver_state = False


def select_video_stat(driver):
    """
    Select Video stat toggle button to enable video stats
    """
    global logger
    global driver_state

    logger.info("Selecting video stats")
    if driver.session_id == None or not driver_state:
        return
    for i in range (MAX_FAILURES):
        time.sleep(1)
        try:
            stats = driver.find_element(by=By.XPATH, value="//div[@data-a-target='player-settings-submenu-advanced-video-stats']")
            stats.click()
            logger.info("Succeeded")
            break
        except Exception as e :
            logger.error(f"enable stat element not found in trial {i}")
            logger.error(e)
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit()
                driver_state = False
            
def select_stat(driver):
    """
    click on the stats list so that the advanced menu disappears
    """
    global logger
    global driver_state

    if driver.session_id == None or not driver_state:
        return
    logger.info("Selecting stats")
    #Click on the stats window
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try:
            select_stats = driver.find_element(by=By.XPATH, value="//tbody[@class='tw-table-body']")
            select_stats.click()
            logger.info("Succeeded")
            break
        except Exception as e :
            logger.error(f"stat window not found in trial {i}")
            logger.error(e)
            if i == MAX_FAILURES -1:
                logger.error("FAILED :(")
                driver.quit()
                driver_state = False 
            

def collect_data(driver):
    """
    Let's collect the data every minuite
    """
    global logger
    global output_dic
    global driver_state

    if driver.session_id == None or not driver_state:
        return
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
            
            #Time is commented for live videos but it is 100% working for recorded videos
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
                if i < 6: # Get QoE that change every min.
                    snapshot_data[cols[0].find("p").text] = cols[1].find("p").text
                else:
                    if first_time: # Get QoE that are fixed all over the video
                        static_data[cols[0].find("p").text] = cols[1].find("p").text
            
            # Uncomment to add time to the QoE
            # snapshot_data["time"] = video_time

        except Exception as e :
            logger.error(f"can't extract data in trial {trials_counter}")
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
    global driver_state


    #Create logger
    logFile = os.path.join("tw_"+str(video), "logs")
    logger = createLog(logFile)


    #Start tshark
    tsharkObj = tshark_dumps(video)
    tsharkObj.start_tshark_process()
    time.sleep(5)

    #link for recorded videos
    video_link = f'https://www.twitch.tv/videos/{video}/'

    #link for live videos
    # video_link = "https://www.twitch.tv/sypherpk"

    file_name = os.path.join("tw_"+str(video), "qoe", f"{video}.json")
    
    driver.get(video_link)
    driver.maximize_window()
    # 10 min to be sure the page is loaded and 30 min for ads
    # it is 98% 30 sec ads in the beginning :(
    time.sleep(40)
    driver_state = True
    

    select_settings(driver)
    select_advanced(driver)
    select_video_stat(driver)
    select_stat(driver)
    collect_data(driver)

    #Write down the qoe data
    output_dic["video_id"] = video
    output_file = open(file_name, 'w')
    json.dump(output_dic, output_file, indent=4)

    #Stop tshark
    tsharkObj.end_tshark_process()
    tsharkObj.process_capture()


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
    """
    The starting point for this file, it only takes the video ID from the control file
    """
    print(f"Starting retriving for {video}")

    # Display size is random popular screen size
    display = Display(visible=False, size=(1920, 1080))
    display.start()

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu') 
    options.add_argument('--no-sandbox')
    # driver = webdriver.Firefox()
    # driver = webdriver.Chrome("U:\programs\chromedriver_win32\chromedriver.exe", chrome_options=options)
    options.BinaryLocation = "/usr/bin/chromium-browser"

    driver = webdriver.Chrome(service=Service(),options=options)    
    process_video(driver, video)

    driver.quit()