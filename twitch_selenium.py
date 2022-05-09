import json
import time
from regex import B
from selenium import webdriver
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.chrome.options import Options

def hover(browser, xpath):
    element_to_hover_over = browser.find_element_by_xpath(xpath)
    hover = ActionChains(browser).move_to_element(element_to_hover_over)
    hover.perform()

def hover_over_video(driver):
    element_to_hover_over = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[2]')
    hover = ActionChains(driver).move_to_element(element_to_hover_over)
    hover.perform()

    

MAX_TRIALS = 40
MAX_FAILURES = 35 # max  no of trying if stat enabling fails
MAX_SNAPSHOTS = 20

output_dic = {
    'static_data': {
        'backend_version': "",
        'serving_ID': "", 
        'codecs': "", 
        'playsession_ID': "",
        'protocol': ""
        },
    'qoe': []}
#TODO: 
#Add handling if we cannot click on any of the steps to enable the stats
    # Keep trying to enable it for 5 times... if didn't succeed! then quit()
#Extract video title 
#loop with trials count check, reset counter in case video resumed

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

def select_settings(driver):
    logging.info("select settings")
    for i in range (MAX_FAILURES):
        try :
            hover_over_video(driver)
            time.sleep(1)
            e = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[6]/div/div[2]/div[2]/div[1]/div[2]/div/button')
            e.click()
            logging.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logging.warning(f"settings element not found in trial {i}")

            if i == MAX_FAILURES -1:
                logging.error("FAILED :(")
                driver.quit()

def select_advanced(driver):
    logging.info("Selecting advanced")
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try :
            advanced = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[6]/div/div[2]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div[5]/button/div/div[1]')
            # advanced = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[6]/div/div[2]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div[5]/button')
            advanced.click() 
            logging.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logging.warning(f"advanced element not found in trial {i}")
            if i == MAX_FAILURES -1:
                logging.error("FAILED :(")
                driver.quit()


def select_video_stat(driver):
    logging.info("Selecting video stats")
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try:
            stat_enabled = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[6]/div/div[2]/div[2]/div[1]/div[1]/div/div/div/div/div/div/div[4]/div/div')
            stat_enabled.click()
            logging.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logging.warning(f"enable stat element not found in trial {i}")
            if i == MAX_FAILURES -1:
                logging.error("FAILED :(")
                driver.quit()
            

def select_stat(driver):
    logging.info("Selecting stats")
    #Click on the stats window
    for i in range (MAX_FAILURES):
        time.sleep(2)
        try:
            stat_window = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/thead/tr/th[2]/div/p')
            stat_window.click()
            logging.info("Succeeded")
            break
        except (selenium.common.exceptions.NoSuchElementException) :
            logging.warning(f"stat window not found in trial {i}")
            if i == MAX_FAILURES -1:
                logging.error("FAILED :(")
                driver.quit() 
        

def collect_data(driver):
    global output_dic
    first_time = True
    trials_counter = 0
    snapshots_counter = 0
    while snapshots_counter < MAX_SNAPSHOTS and trials_counter<MAX_TRIALS:

        #Extract data
        try:
            hover_over_video(driver)
            time_in_video = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[7]/div/div[1]/div/div[2]/p[1]').text
            v_resolution = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[1]/td[2]/p').text
            d_resolution = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[2]/td[2]/p').text
            fps = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[3]/td[2]/p').text
            skipped_frames = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[4]/td[2]/p').text
            buffer_size = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[5]/td[2]/p').text
            playback_bitrate = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[6]/td[2]/p').text
            #static
            if(first_time):
                backend_version = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[7]/td[2]/p').text
                serving_ID = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[8]/td[2]/p').text
                codecs = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[9]/td[2]/p').text
                playsession_ID = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[10]/td[2]/p').text
                protocol = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div/div[4]/div/div[3]/div/div/table/tbody/tr[11]/td[2]/p').text
        

        except (selenium.common.exceptions.NoSuchElementException) :
            logging.error("can't extract data")
            time.sleep(5)
            trials_counter += 1
            continue

        snapshot_data = {
                'time' : time_in_video,
                'v_resolution' : v_resolution,
                'd_resolution': d_resolution, 
                'fps': fps,
                'skipped_frames':skipped_frames,
                'buffer_size':buffer_size, 
                'playback_bitrate':playback_bitrate
                
                }
        if first_time:
            logging.info("First time data stored")
            output_dic['static_data']['backend_version'] = backend_version
            output_dic['static_data']['serving_ID'] = serving_ID
            output_dic['static_data']['codecs'] = codecs
            output_dic['static_data']['playsession_ID'] = playsession_ID
            output_dic['static_data']['protocol'] = protocol

            output_dic['qoe'].append(snapshot_data)
            first_time = False
            
            snapshots_counter +=1
            continue
        
        #compare with previous, if the same, it is an ad or network error
        if  output_dic['qoe'][-1]["time"] == time_in_video and \
            output_dic['qoe'][-1]["v_resolution"] == v_resolution and \
            output_dic['qoe'][-1]["d_resolution"] == d_resolution and \
            output_dic['qoe'][-1]["fps"] == fps and \
            output_dic['qoe'][-1]["skipped_frames"] == skipped_frames and \
            output_dic['qoe'][-1]["buffer_size"] == buffer_size and \
            output_dic['qoe'][-1]["playback_bitrate"] == playback_bitrate:
            logging.warning("No change in data! Ads or buffering")
            logging.warning(f"Trials counter {trials_counter}")
            time.sleep(5)
            trials_counter += 1
            continue
        else:
            logging.info("Storing data in json object")
            output_dic['qoe'].append(snapshot_data)
            trials_counter = 0
            snapshots_counter +=1

        time.sleep(1)



if __name__ == "__main__":
    logging.basicConfig(filename='twitch_selenium.log', filemode='w', format='%(funcName)s:%(lineno)s - %(levelname)s - %(message)s')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  #
    driver = webdriver.Chrome("U:\programs\chromedriver_win32\chromedriver.exe", chrome_options=options)
    video_link = 'https://www.twitch.tv/videos/1466332523/'
    file_name = ""
    tokens = video_link.split('/')
    print(tokens)
    file_name = tokens[-2] + ".json"
    
    
    driver.get('https://www.twitch.tv/videos/1466332523/')
    time.sleep(10)

    select_settings(driver)
    select_advanced(driver)
    select_video_stat(driver)
    select_stat(driver)
    collect_data(driver)
    output_file = open(file_name, 'w')
    json.dump(output_dic, output_file, indent=4)

    driver.quit()