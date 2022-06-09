import os
import sys
from twitch_selenium import *

from os import listdir
from os.path import isfile, join
import shutil


#Create directories
today_date = datetime.datetime.now().date()
logging.basicConfig(filename=f'twitch_Ctrl_{today_date.strftime("%Y_%M_%d")}.log', filemode='w', format='%(funcName)s:%(lineno)s - %(levelname)s - %(message)s')
 
packets_path = ""
qoe_path = ""
logs_path = ""

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


def create_directory(video):
    global packets_path, qoe_path, logs_path
    logging.info("Creating Directories")
    #/tw_date/packets ./tw_date/qoe ./tw_logs
    packets_path = os.path.join(".", "Results", f"tw_{video}", "packets")
    qoe_path = os.path.join(".", "Results", f"tw_{video}", "qoe")
    logs_path = os.path.join(".", "Results", f"tw_{video}", "logs")

    if os.path.exists(packets_path):
        shutil.rmtree(packets_path)
    os.makedirs(packets_path)

    if os.path.exists(qoe_path):
        shutil.rmtree(qoe_path)
    os.makedirs(qoe_path)

    if os.path.exists(logs_path):
        shutil.rmtree(logs_path)
    os.makedirs(logs_path)

    # qoe_path = os.path.join(".", "Results", f"tw_{video}_normal", "qoe")
    # logs_path = os.path.join(".", "Results", f"tw_{video}_normal", "logs")

    # if os.path.exists(qoe_path):
    #     shutil.rmtree(qoe_path)
    # os.makedirs(qoe_path)

    # if os.path.exists(logs_path):
    #     shutil.rmtree(logs_path)
    # os.makedirs(logs_path)



if __name__ == "__main__":
    arguments = sys.argv
    videos = arguments[1:]
    for video in videos:
        create_directory(video)
    
        #start collecting the qoe
        startRetrivingData(video)

        #copy files to server
        #logs:
        # proc = subprocess.Popen(['curl'] + ["-T", f"/root/twitch/tw_{video}/logs/selenium_log.log", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/logs/selenium_log.log"])
        # proc = subprocess.Popen(['curl'] + ["-T", f"./tw_{video}/logs/tshark_log.log", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/logs/tshark_log.log"])

        # #QoE
        # proc = subprocess.Popen(['curl'] + ["-T", f"./tw_{video}/qoe/{video}.json", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/qoe/{video}.json"])

        # #Packets
        # packetsFiles = [f for f in os.listdir(f"./tw_{video}/packets") if isfile(join(f"./tw_{video}/packets", f))]
        # for packetFile in packetsFiles:
        #     proc = subprocess.Popen(['curl'] + ["-T", f"./tw_{video}/packets/{packetFile}", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/packets/{packetFile}"])


