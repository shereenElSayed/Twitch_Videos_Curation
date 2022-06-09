import os
import sys
from twitch_selenium import *

from os import listdir
from os.path import isfile, join
import shutil
"""
This is the starting script on the minion side.
"""

#Create directories
today_date = datetime.datetime.now().date()
logging.basicConfig(filename=f'twitch_Ctrl_{today_date.strftime("%Y_%M_%d")}.log', filemode='w', format='%(funcName)s:%(lineno)s - %(levelname)s - %(message)s')
 
packets_path = ""
qoe_path = ""
logs_path = ""


def create_directory(video):
    """
    It creates 3 directories under tw_<video>: packets, logs and qoe
    If directories are there, overwite
    """
    global packets_path, qoe_path, logs_path
    logging.info("Creating Directories")
    #/tw_date/packets ./tw_date/qoe ./tw_logs
    packets_path = f"./tw_{video}/packets"
    qoe_path = f"./tw_{video}/qoe"
    logs_path = f"./tw_{video}/logs"

    if os.path.exists(packets_path):
        shutil.rmtree(packets_path)
    os.makedirs(packets_path)

    if os.path.exists(qoe_path):
        shutil.rmtree(qoe_path)
    os.makedirs(qoe_path)

    if os.path.exists(logs_path):
        shutil.rmtree(logs_path)
    os.makedirs(logs_path)


if __name__ == "__main__":
    """
    Program starts by taking list of videos as arguments
    """
    arguments = sys.argv
    videos = arguments[1:]
    for video in videos:
        #create necessary directories for the video
        create_directory(video)
    
        #start collecting the qoe
        startRetrivingData(video)

        #copy files to server
        #logs:
        proc = subprocess.Popen(['curl'] + ["-T", f"/root/twitch/tw_{video}/logs/selenium_log.log", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/logs/selenium_log.log"])
        proc = subprocess.Popen(['curl'] + ["-T", f"./tw_{video}/logs/tshark_log.log", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/logs/tshark_log.log"])

        #QoE
        proc = subprocess.Popen(['curl'] + ["-T", f"./tw_{video}/qoe/{video}.json", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/qoe/{video}.json"])

        #Packets
        packetsFiles = [f for f in os.listdir(f"./tw_{video}/packets") if isfile(join(f"./tw_{video}/packets", f))]
        for packetFile in packetsFiles:
            proc = subprocess.Popen(['curl'] + ["-T", f"./tw_{video}/packets/{packetFile}", f"http://snl-server-3.cs.ucsb.edu/upload/s_elsayed/twitch/tw_{video}/packets/{packetFile}"])


