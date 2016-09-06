from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI

from auto_pox import POX

class SingleSwitchTopo(Topo):
        # single swtich connected to n hosts
        def build(self, n=2):
                switch = self.addSwitch('s1')
                for h in range(n):
                        host = self.addHost('h{0}'.format(h+1))
                        self.addLink(host, switch)

def simpleTest():
        # create and test a simple network
        topo = SingleSwitchTopo(n=2)
        #net = Mininet(topo, controller=POX)
        net = Mininet(topo, switch=OVSSwitch, controller=RemoteController('c0', ip='127.0.0.1', port=6633))
	net.start()
        print "Dumping host connections"
        dumpNodeConnections(net.hosts)
        print "Testing network connectivity"
        net.pingAll()

        # pre-configure hosts and switches
        h1 = net.get('h1')
        h1.cmd('ifconfig h1-eth0 mtu 65535')
	h1.cmd('sysctl net.ipv6.conf.all.disable_ipv6=1')

	s1 = net.get('s1')
	s1.cmd('ifconfig s1-eth1 mtu 65535')
	s1.cmd('sysctl net.ipv6.conf.s1-eth1.disable_ipv6=1')
	
	CLI(net)
	net.stop()

if __name__ == "__main__":
        setLogLevel('debug')
        simpleTest()

