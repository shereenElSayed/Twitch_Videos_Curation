from concurrent.futures import ProcessPoolExecutor
import datetime
import logging
import os
import subprocess
import time
from typing import Set
from venv import create

import pyshark

class tshark_dumps:
    def __init__(self, video):
        self.video = str(video)
        self.today_date = datetime.datetime.now().date()
        self.proc = None
        self.logPath = os.path.join("Results", "tw_" + video, "logs")
        self.logger = self.createLog()
        self.packetsPath = os.path.join("Results", "tw_" + video, "packets")
        self.allPacketsPath = os.path.join(self.packetsPath, "allPackets.cap")
        


    def createLog(self):
        logger = logging.getLogger("log")   # > set up a new name for a new logger

        logger.setLevel(logging.DEBUG)  # here is the missing line

        log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        filename = os.path.join(self.logPath, "tshark_log.log")
        if os.path.exists(filename):
            os.remove(filename)
        log_handler = logging.FileHandler(filename)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(log_format)

        logger.addHandler(log_handler)

        return logger

    def start_tshark_process(self):
        try:
            self.proc = subprocess.Popen(["tshark"] + ["-i 5","-w", self.allPacketsPath])
            self.logger.info("Tshark process started")
            time.sleep(2)
            if self.proc.poll() is None:
                self.logger.info("Tshark process running")

            else:
                self.logger.error("Tshark process stopped!")
        except Exception as e:
            self.logger.error(e)

    def end_tshark_process(self):
        self.logger.info("Terminating Tshark")
        self.proc.terminate()

    def is_twitch_server(self, server_name):
        tw_servers = ["cloudfront.net", "jtvnw.net", "twitch.tv"]

        for server in tw_servers:
            if server_name.endswith(server):
                return True
        
        return False


    def process_capture(self):
        try:
            self.logger.info("reading captured data to get IPs")
            capture = pyshark.FileCapture(self.allPacketsPath, display_filter='ssl.handshake.extension.type == "server_name"')

            IPs = set()

            for packet in capture:
                #Filter the QUIC
                if "TLS" in packet and hasattr(packet.tls, "handshake_extensions_server_name"):
                    server_name = str(packet.tls.handshake_extensions_server_name)
                    self.logger.info(f"Server name before check= {server_name}")
                    #check on the end of the server name:
                    if self.is_twitch_server(server_name):
                        self.logger.info(f"server name: {server_name}")
                        IPs.add((packet.ip.src, packet.ip.dst))   
            capture.close()
        except Exception as e:
            self.logger.error("Error reading all captured packets with handshake")
            self.logger.error(e)
        self.logger.info(f"IPs found:: {IPs}")
        #After getting the IPs, now filter them!
        for ipPair in IPs:
            try:
                display_filer = f"ip.src == {ipPair[0]} && ip.dst == {ipPair[1]} || \
                ip.src == {ipPair[1]} && ip.dst == {ipPair[0]}"
                #File name structure packets_<src>_<dest>.pcap
                #remove the file name of the path then add the dumping file name
                packet_path = os.path.join(self.packetsPath, f"packets_{ipPair[0]}_{ipPair[1]}.cap")
                capture = pyshark.FileCapture(self.allPacketsPath, display_filter=display_filer, output_file=packet_path)
                capture.load_packets()
                capture.close()
            except Exception as e:
                self.logger.error(f"Error filtering packets for pairs {ipPair}")
                self.logger.error(e)







    
    