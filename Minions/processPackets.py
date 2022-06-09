from http import server
import os
import pyshark


def is_twitch_server(server_name):
    tw_servers = ["cloudfront.net", "jtvnw.net", "twitch.tv"]

    for server in tw_servers:
        if server_name.endswith(server):
            return True
    
    return False


allPacketsPath = os.path.join("tw_1313281798", "packets")
captured = os.path.join(allPacketsPath, "allPackets.pcap")
try:
    capture = pyshark.FileCapture("U:\Classes\\293N-Networking\Project\data.cap", display_filter='ssl.handshake.extension.type == "server_name"')

    IPs = []

    for packet in capture:
        #Filter the QUIC
        if "TLS" in packet and hasattr(packet.tls, "handshake_extensions_server_name"):
            server_name = str(packet.tls.handshake_extensions_server_name)
            print(server_name)
            #check on the end of the server name:
            if is_twitch_server(server_name):
                IPs.append((packet.ip.src, packet.ip.dst))   
    capture.close()
    print(IPs)
except Exception as e:
    # self.logger.error("Error reading all captured packets with handshake")
    print(e)

#After getting the IPs, now filter them!
for ipPair in IPs:
    try:
        display_filer = f"ip.src == {ipPair[0]} && ip.dst == {ipPair[1]} || \
        ip.src == {ipPair[1]} && ip.dst == {ipPair[0]}"
        #File name structure packets_<src>_<dest>.pcap
        #remove the file name of the path then add the dumping file name
        packets_path = os.path.join("U:\Classes\\293N-Networking\Project\packets", f"packets_{ipPair[0]}_{ipPair[1]}")
        capture = pyshark.FileCapture("U:\Classes\\293N-Networking\Project\data.cap", display_filter=display_filer, output_file=packets_path)
        capture.load_packets()
        capture.close()
    except Exception as e:
        print(e)


