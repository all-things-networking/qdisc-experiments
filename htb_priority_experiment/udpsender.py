#!/usr/bin/env python3
import os
import sys
from scapy.all import *
import time

# sender - blue15
src_ip = "10.30.0.15"
src_port = 8899
src_iface = "enp130s0"
src_hwaddr = "f4:52:14:26:8d:60"

# receiver - yellow01
dst_ip = "10.30.0.1"
dst_port = 3000
dst_iface = "enp130s0"
dst_hwaddr = "f4:52:14:48:92:30"
# dst_hwaddr = "f4:52:14:26:8a:a0"

# Create a 1KB packet to simulate a file transfer
# payload = "X" * 1024  # 1KB payload
payload = "X" * 1400 #tried larger payload

pkt =  Ether(src=src_hwaddr, dst=dst_hwaddr)
pkt = pkt / IP(dst=dst_ip, src=src_ip) / UDP(dport=dst_port, sport=src_port) / Raw(load=payload)
print(pkt.show())

packet_size_bits = len(bytes(pkt)) * 8 # size in bits

print(pkt.sprintf("%Ether.src% > %Ether.dst%; %IP.src% > %IP.dst%"))

rate = 100  # kb/s
period = 10 # seconds
# time.sleep(10) # initial 10 sec, rate = 0

def send_loop(rate_kbps):
    total_bits_per_sec = rate_kbps * 1000
    num_packets = total_bits_per_sec // packet_size_bits
    print(f"Sending {num_packets} packets at {rate_kbps} kbps")

    #maintain send rate per sec
    for _ in range(10):
        start_time = time.time()
        for _ in range(int(num_packets)):
            sendp(pkt, iface=src_iface, verbose=False)
        elapsed = time.time() - start_time
        if elapsed < 1:
            time.sleep(1 - elapsed)


#approach 2 multiple senders
send_loop(100)
for i in range(8):
    send_loop(200)
send_loop(100)

# done