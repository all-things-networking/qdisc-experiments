from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink
import re
import json
import time

class TwoHostTopo(Topo):
    # Create a topology with 2 hosts
    def __init__(self):
        Topo.__init__(self)
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, h2)

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
    # result1 = h1.cmd('python3 sender.py {} {}'.format(h1_if_mac, h2_if_mac))
    result1 = h1.cmd('python3 sender.py {} {}'.format(h1_if_mac, h2_if_mac))
    print("h1 returned: ", result1)
    print("h2 returned: ", result2)

    # time.sleep(10)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()
