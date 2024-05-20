from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink
import re
import json
import time
# import test_reset_timeout
import subprocess
import math
import os
import getGraph

class HostSend():
    def __init__(self, node, name ):
        self.host = node
        self.name = name
        # un-initialized variables
        self.recv_addr = ''
        self.src_addr = ''
        self.src_port = 10000
        self.iface = ""
        self.if_hwaddr = ""
        self.recv_hwaddr = ""
    
    def cmd(self, cmd_string):
        return self.host.cmd(cmd_string)
    
    def clear_qdisc(self, qdisc_type):
        return self.host.cmd( 'tc qdisc del dev %s-eth0 root %s' %(self.name, qdisc_type) )
    
    def set_qdisc(self, qdisc_type, config_dict):
        config_string = ' '.join( "%s %s" %(key, value) for key, value in config_dict.items() )
        return self.host.cmd( 'tc qdisc add dev %s-eth0 root %s %s' %(self.name, qdisc_type, config_string) )

    def start_run(self, hh_count, T, W, E, H, C, logfname):
        # create a dictionary and save it to json, used by the sender
        sender_parameters = {
            "hh_count": hh_count,
            "T": T,
            "W": W, 
            "E": E,
            "H": H,
            "C": C,
            "recv_addr": self.recv_addr,
            "src_addr": self.src_addr,
            "src_port": self.src_port,
            "iface": self.iface,
            "if_hwaddr": self.if_hwaddr,
            "recv_hwaddr": self.recv_hwaddr,
        }
        outfname = "sender_parameter.json"
        with open(outfname, 'w') as outfp:
            json_obj = json.dumps(sender_parameters, indent = 4)
            outfp.write(json_obj)
        
        # execute the sender program
        result = self.host.cmd('python3 sender.py {} {}'.format(outfname, logfname))
        return result

class HostRecv():
    def __init__(self, node, name):
        self.host = node
        self.name = name

    def cmd(self, cmd_string):
        return self.host.cmd(cmd_string)
    
    def start_run(self, logfname):
        result = self.host.cmd('python3 receiver.py {} &'.format(logfname))
        return result


class TwoHostTopo(Topo):
    # Create a topology with 2 hosts
    def __init__(self):
        Topo.__init__(self)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, h2)

class NetController():
    def __init__(self):
        topo = TwoHostTopo()
        # TODO: link rate limit investigation
        # net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
        self.net = Mininet(topo=topo)
        self.net.start()
    
    # returns two host objects
    def init_two_hosts(self):
        # get two hosts
        h_send = HostSend( self.net.get('h1'), 'h1' )
        h_recv = HostRecv( self.net.get('h2'), 'h2' )
        h_send.cmd('kill %python3')
        h_recv.cmd('kill %python3')
        # record info used by sender
        # set ports, addrs, etc
        h_send.recv_addr = '10.0.0.2' #  h1 -> h2
        h_send.src_addr = '10.0.0.1'
        h_send.src_port = 12000
        h_send.iface = "h1-eth0"
        # find mac ports
        h_send_if = h_send.cmd('ifconfig')
        h_recv_if = h_recv.cmd('ifconfig')
        pattern = r'ether\s[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+'
        h_send.if_hwaddr = re.search(pattern, h_send_if).group(0).split()[1] # MAC addr sender
        h_send.recv_hwaddr = re.search(pattern, h_recv_if).group(0).split()[1] # MAC addr receiver
        return h_send, h_recv
    
    def terminate(self):
        self.net.stop()

    

# should create a helper file and only load once
# returns a command line argument used to setup an hhf qdisc
def get_hhf_config():
    hhf_config = {}
    with open('qdisc-config.json') as json_file:
        hhf_config = json.load(json_file)
    
    return ' '.join( "%s %s" %(key, value) for key, value in hhf_config.items() )



def simpleTest():
    # Create the network
    topo = TwoHostTopo()
    # net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net = Mininet(topo=topo)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')
    print( h1.cmd('kill %python3') )
    print( h2.cmd('kill %python3') )

    # find mac ports
    h1_if = h1.cmd('ifconfig')
    h2_if = h2.cmd('ifconfig')

    pattern = r'ether\s[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+\:[0-9A-Fa-f]+'
    h1_if_mac = re.search(pattern, h1_if).group(0).split()[1]
    h2_if_mac = re.search(pattern, h2_if).group(0).split()[1]
    # print("h1_if_mac: ", h1_if_mac)
    # print("h2_if_mac: ", h2_if_mac)

    # set hhf qdisc for h1
    result1 = h1.cmd( 'tc qdisc add dev h1-eth0 root hhf %s' %get_hhf_config() )
    print("set qdisc ", 'tc qdisc add dev h1-eth0 root hhf %s' %get_hhf_config())
    print("h1 returned after adding qdisc: ", result1)

    # execute sender and receiver
    result2 = h2.cmd('python3 receiver.py log-receiver.json &')
    result1 = h1.cmd('python3 sender.py {} {}'.format(h1_if_mac, h2_if_mac))
    # result1 = h1.cmd('python3 sender.py {} {}'.format(h1_if_mac, h2_if_mac))
    print("h1 returned: ", result1)
    print("h2 returned: ", result2)

    # time.sleep(10)
    net.stop()


# this is the main function for the experiment that measures the relationship between
# variable: number of heavy hitter flows
# dependent: throughput at both sender/receiver
def main(config_path):
    # load hhf-config and set some variables
    hhf_config = {}
    with open(config_path) as json_file:
        hhf_config = json.load(json_file)
    
    # assumes no error in this step
    T = int(hhf_config["hh_limit"]) # count
    W = int(hhf_config["non_hh_weight"]) # ratio
    E = int(hhf_config["evict_timeout"][:-2]) # ms
    H = int(hhf_config["admit_bytes"]) # bytes
    C = int(hhf_config["reset_timeout"][:-2]) # ms

    # initialize the net
    net_ctrl = NetController()
    h_send, h_recv = net_ctrl.init_two_hosts()

    # outer loop, continue the runs until 2*T flows run at 1.5*C*H
    # run_0: Have T/2 heavy hitters
    # run_i: Have (T/2 + i x T/4) heavy hitters
    hh_count = math.ceil(T/2) 
    while hh_count <= 2*T:
        h_send.set_qdisc('hhf', hhf_config)
        # run_i
        log_recv_path = h_recv.start_run("log-receiver.json")
        log_send_path = h_send.start_run(hh_count, T, W, E, H, C, "log-sender.json")
        # generate graph 
        # subprocess.run(
            # "python3 getGraph.py {} {}_plot.json 10".format("log-receiver.json", str(hh_count)), 
        #     shell = True, 
        #     executable="/bin/bash"
        #     )
        # os.system("python3 getGraph.py {} {}_plot.json 10".format("log-receiver.json", str(hh_count)))
        # os.system("python3 trial.py")
        getGraph.generate_graph("log-receiver.json", "{}_r_plot.jpg".format(str(hh_count)), 10)
        getGraph.generate_graph("log-sender.json", "{}_s_plot.jpg".format(str(hh_count)), 10)

        # reset qdisc
        h_send.clear_qdisc('hhf')        
        hh_count += T/4
    
    # get two parallel graphs for a run
    # get_graph(log_send_path, log_recv_path)
    # subprocess.run(
    #     "python3 getGraph.py {} {}_plot.json 10".format("log-receiver.json", str(hh_count)), 
    #     shell = True, 
    #     executable="/bin/bash")

    # clean up
    net_ctrl.terminate()




    
if __name__ == '__main__':
    main('qdisc-config.json')

