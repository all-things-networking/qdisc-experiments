#!/usr/bin/env python3
import sys
import time
from scapy.all import *
import socket
import threading

# Ensure the correct network interface is used
recv_iface = "enp130s0"  # Update if necessary
recv_port = [3000, 8890]  # Match dst_port from sender
start_time = time.time()

lockudp = threading.Lock()
locktcp = threading.Lock()
flowudp_bytes = 0
flowtcp_bytes = 0
port1 = 3000
port2 = 8890
# pkt_size = 1024 # assumption from tcpdump

def packet_callback(pkt):
    global flowudp_bytes, flowtcp_bytes

    if UDP in pkt and pkt[UDP].dport in recv_port:
        with lockudp:  
            # flowudp_bytes += pkt_size
            flowudp_bytes += len(pkt)

    elif TCP in pkt and pkt[TCP].dport in recv_port:
        with locktcp:  
            # flowtcp_bytes += pkt_size
            flowtcp_bytes += len(pkt)

        # try:
        #     payload = pkt[Raw].load.decode("utf-8")
        # except:
        #     print("payload not found")
        # print(f"Received {len(packet)} bytes from {packet[IP].src}")
        # print(packet.summary())  # Show a brief packet summary
        # port = packet[UDP].dport
        # packet_counts[port] += len(packet)
        # elapsed_time = time.time() - start_time
        # rate_kbps = (packet_counts[port] * 8) / (elapsed_time * 1000)
        # print(f"Port {port}: {rate_kbps:.2f} kbit/s")

# every five seconds
def print_throughput():
    """Periodically prints throughput every x seconds."""
    global flowudp_bytes, flowtcp_bytes
    while True:
        sleep_period = 1
        time.sleep(sleep_period)
        elapsed_time = time.time() - start_time

        with lockudp:
            rateudp_kbps = (flowudp_bytes * 8) / (sleep_period * 1000)  # Convert to kbps
            flowudp_bytes = 0  # Reset counter after reporting

        with locktcp:
            ratetcp_kbps = (flowtcp_bytes * 8) / (sleep_period * 1000)
            flowtcp_bytes = 0 
        
        print(f"Throughput (last {sleep_period} sec) - UDP: {rateudp_kbps:.2f} kbit/s, TCP: {ratetcp_kbps:.2f} kbit/s")
    

# Start the throughput calculation in a separate thread
threading.Thread(target=print_throughput, daemon=True).start()

print(f"Listening on {recv_iface} for TCP and UDP packets...")
sniff(iface="enp130s0", prn=packet_callback)
