#!/usr/bin/env python3
import random
import socket
import sys
import time
import json

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
        # assume no over-sized packet (for now)
        # TODO: add handling for oversized packets
        message = "flowid" + str(flow_id) + "end"
        final_message = message + "x"*int(size - len(message))
        # print(len(final_message))

        # default: UDP
        pkt =  Ether(src= self.if_hwaddr, dst= self.recv_hwaddr)
        pkt = pkt /IP(dst= self.recv_addr, src= self.src_addr) / UDP(dport=1234, sport= self.src_port) / Raw(load=final_message)
        sendp(pkt, iface= self.iface, verbose=False)

        # fout.write(pkt.summary() + "\n")           

# TODO: theortical rate in this function
# might want to also add measurement here?
def main():
    # set ports, addrs, etc
    recv_addr = '10.0.0.2' #  h1 -> h2
    src_addr = '10.0.0.1'
    src_port = 12000
    iface = "h1-eth0"
    print("sending on interface %s to %s" % (iface, str(recv_addr)))
    if_hwaddr = sys.argv[1] # MAC addr sender
    recv_hwaddr = sys.argv[2] # MAC addr receiver

    sender = Sender(src_addr, recv_addr, src_port, iface, if_hwaddr, recv_hwaddr)

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
    hh_rate_limit = H/1000000 / C * 1000 # Mbps

    # run_0: Have T/2 flows send at 1.5 x C x H, the rest of the flows send at 0.5 x C x H.
    # run_i: Have (T/2 + i x T/4) send at 1.5 x C x H, the rest of the flows send at 0.5 x C x H.
    hh_count = T/2
    non_hh_count = N - hh_count

    hh_rate = 1.5*H/C*1000 # bytes/s
    non_hh_rate = 0.5*H/C*1000 # bytes/s

    # outer loop, continue the runs until 2*T flows run at 1.5*C*H
    while hh_count <= 2*T:

        # idx i of b_list: total amount of bytes fi has sent
        # idx i of t_list: last time fi sent traffic
        b_list = [0] * N 
        t_initial = time.time() # time in second. Needs conversion
        t_list = [t_initial] * N
        
        # exit condition (for now): run for 10 minutes
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
                        
        print("switch flow")
        hh_count += T/4
        non_hh_count = N - hh_count


if __name__ == '__main__':
    main()