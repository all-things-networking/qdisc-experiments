#!/usr/bin/env python3
import random
import socket
import sys
import time
import json
import math

from scapy.all import IP, UDP, TCP, Ether, sendp, Raw

class Sender():
    def __init__(self, src_addr, recv_addr, src_port, iface, if_hwaddr, recv_hwaddr):
        # basic address info h1->h2
        self.src_addr = src_addr
        self.recv_addr = recv_addr
        self.src_port = src_port
        self.iface = iface
        # MAC addr
        self.if_hwaddr = if_hwaddr
        self.recv_hwaddr = recv_hwaddr
        # fout = open("./log-sender.txt", "w")

    
    def send_packets(self, flow_id, size):
        # CASE2: sread large packets into multiple 
        # this maxsize doesn't change the overall shape much
        # so to decrease the pkt count, use 1000
        pkt_maxsize = 1000
        # pkt_maxsize = 512

        # outfp = open("temp.txt", "a")
        # outfp.write("send packets" + str(size) +"\n")

        while (size > 0):
            # TODO: add handling for oversized packets
            message = "flowid" + str(flow_id) + "end"
            if len(message) + size > pkt_maxsize:
                final_message = message + "x"*int(pkt_maxsize - len(message))
            else:
                final_message = message + "x"*int( max(0, size - len(message)) )
            size = size - len(final_message)
            # print(len(final_message))
            
            # outfp.write(message + ": " + str(size) +"\n")

            # default: UDP
            pkt =  Ether(src= self.if_hwaddr, dst= self.recv_hwaddr)
            pkt = pkt /IP(dst= self.recv_addr, src= self.src_addr) / UDP(dport=1234, sport= self.src_port) / Raw(load=final_message)
            sendp(pkt, iface= self.iface, verbose=False)

        # outfp.close()

# T = int(hhf_config["hh_limit"]) # count
# W = int(hhf_config["non_hh_weight"]) # ratio
# E = int(hhf_config["evict_timeout"][:-2]) # ms
# H = int(hhf_config["admit_bytes"]) # bytes
# C = int(hhf_config["reset_timeout"][:-2]) # ms
def run_experiment(sender, hh_count, T, W, E, H, C):
    N = 3 * T # total flow number
    hh_rate_limit = H/1000000 / C * 1000 # Mbps

    # # run_0: Have T/2 flows send at 1.5 x C x H, the rest of the flows send at 0.5 x C x H.
    # # run_i: Have (T/2 + i x T/4) send at 1.5 x C x H, the rest of the flows send at 0.5 x C x H.
    # hh_count = math.ceil(T/2) 
    # non_hh_count = N - hh_count

    hh_rate = 1.5*H/C*1000 # bytes/s
    non_hh_rate = 0.5*H/C*1000 # bytes/s

    # idx i of b_list: total amount of bytes fi has sent
    # idx i of t_list: last time fi sent traffic
    b_list = [0] * N 
    t_initial = time.time() # time in second. Needs conversion
    t_list = [t_initial] * N
    
    # exit condition (for now): run for 30 sec
    time_limit = 1*30
    # continuously run from flow f_1 to f_N until exit condition satisfied
    while t_list[-1] - t_initial < time_limit :
        for i in range(N):

            # calculate number of bytes allowed to send
            # total amount of bytes should be send by now: rate * delta_t
            # num-bytes-to-send-this-time = total-should-send - already-sent
            t = time.time()
            delta_t = t - t_initial
            rate = hh_rate if i < hh_count else non_hh_rate # bytes/s
            a_i = delta_t * rate - b_list[i]
            # print("i ", i, ", delta ", delta_t, ", rate ", rate, " bytes ", b_list[i])

            # send bytes 
            if b_list[i] == 0:
                # first time sending packets
                # send max(a_i, H/N) - TODO: ask reason for this
                a_i = max(a_i, H/N)
            # print("a_i", a_i)
            sender.send_packets(i, a_i)

            # do updates
            b_list[i] += a_i
            t_list[i] = t  


# For this function, one needs to open this json config
def main():
    parameter_path = sys.argv[1]
    with open(parameter_path, 'r') as json_file:
        para_dict = json.load(json_file)

    # assumes the format is correct
    sender = Sender(
        para_dict["src_addr"], 
        para_dict["recv_addr"], 
        para_dict["src_port"], 
        para_dict["iface"], 
        para_dict["if_hwaddr"], 
        para_dict["recv_hwaddr"]
        )

    run_experiment(
        sender, 
        para_dict["hh_count"],
        para_dict["T"], 
        para_dict["W"], 
        para_dict["E"], 
        para_dict["H"], 
        para_dict["C"]
        )


if __name__ == '__main__':
    main()