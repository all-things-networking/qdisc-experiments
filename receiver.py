#!/usr/bin/env python3
import os
import sys
import signal
import json
import time
import threading

from scapy.all import IP, ICMP, TCP, UDP, sniff, Raw

raw_data = {} # holds throughput measurement for all flows
bytes_recv = [] # holds temporary measurement to calculate throughput
lock = threading.Lock() # lock for bytes_recv
stop_threads = False

def handle_packet(pkt):
    global bytes_recv, lock
    # all packets are UDP for now
    if UDP in pkt:
        # match the flow_id
        payload = pkt[Raw].load.decode("utf-8")
        if payload.startswith("flowid"):
            flow_id = int(payload.split("flowid")[1].split("end")[0])
            with lock:
                bytes_recv[flow_id] += len(pkt)

def do_stat(fout_path, N, measurement_interval):
    global bytes_recv, raw_data, lock, stop_threads

    while True:

        for i in range(N):        
            raw_data[str(i)].append(bytes_recv[i])

        # clear the temporary list
        with lock:
            bytes_recv = [0] * N

        # throughput measurement period - in secs
        time.sleep(measurement_interval)

        # dump data file and generate a diagram
        with open(fout_path, 'w') as outfp:
            json_obj =  json.dumps(raw_data, indent = 4)
            outfp.write(json_obj)
        
        if stop_threads: break
    
def do_sniff():
    sniff(iface="h2-eth0", prn = lambda x: handle_packet(x))  # store=0 to not store packets

def main(fout_path, measurement_interval):
    global bytes_recv, raw_data, lock, stop_threads

    # load hhf-config and set some variables
    hhf_config = {}
    with open('qdisc-config.json') as json_file:
        hhf_config = json.load(json_file)
    
    # assumes no error in this step
    T = int(hhf_config["hh_limit"]) # count
    W = int(hhf_config["non_hh_weight"]) # ratio
    E = int(hhf_config["evict_timeout"][:-2]) # ms
    H = int(hhf_config["admit_bytes"]) # bytes
    C = int(hhf_config["reset_timeout"][:-2]) # ms

    N = 3 * T # total flow number

    # initialize the data dictionary
    for i in range(N):
        raw_data[str(i)] = []
    bytes_recv = [0] * N


    sniff_thread = threading.Thread(target=do_sniff)
    print_dump_thread = threading.Thread(target=do_stat, args=(fout_path, N, measurement_interval))
    
    sniff_thread.start()
    print_dump_thread.start()

    # Wait for threads to finish (not necessary in this case as they run indefinitely)
    sniff_thread.join()
    stop_threads = True
    print_dump_thread.join()

    

if __name__ == '__main__':   
    fout_path = sys.argv[1]
    measurement_interval = int(sys.argv[2])
    main(fout_path, measurement_interval)
