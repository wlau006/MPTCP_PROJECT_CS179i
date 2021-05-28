#!/usr/bin/env python

import os
import time
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.net import Mininet

numflows = 2
loss_percent = 10

class MPTopo(Topo):
    HOST_IP = '10.0.{0}.{1}'
    HOST_MAC = '00:00:00:00:{0:02x}:{1:02x}'

    def _setup_routing_per_host(self, host):
        # Manually set the ip addresses of the interfaces
        host_id = int(host.name[1:])

        for i, intf_name in enumerate(host.intfNames()):
            ip = self.HOST_IP.format(i, host_id)
            gateway = self.HOST_IP.format(i, 0)
            mac = self.HOST_MAC.format(i, host_id)

            # set IP and MAC of host
            host.intf(intf_name).config(ip='{}/24'.format(ip), mac=mac)
    def setup_routing(self, net):
        for host in self.hosts():
            self._setup_routing_per_host(net.get(host))



class MyTopo( MPTopo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        leftSwitch = self.addSwitch( 's1' )
        leftSwitch2 = self.addSwitch( 's2' )
        rightSwitch = self.addSwitch( 's3' )        
        rightSwitch2 = self.addSwitch( 's4' )

        # Add links
        self.addLink( leftHost, leftSwitch, bw = 10, delay='5ms', loss=loss_percent)
        self.addLink( leftHost, leftSwitch2, bw = 10, delay='5ms', loss=loss_percent)
        self.addLink( leftSwitch, rightSwitch)
        self.addLink( leftSwitch2, rightSwitch2)
        self.addLink( rightSwitch, rightHost, bw = 10, delay='5ms', loss=loss_percent)
        self.addLink( rightSwitch2, rightHost, bw = 10, delay='5ms', loss=loss_percent)
topos = { 'mytopo': ( lambda: MyTopo() ) }

def main():
    print('\n### TESTING SPTCP ###')
    cc = 'cubic'
    os.system('modprobe mptcp_balia; modprobe mptcp_wvegas; modprobe mptcp_olia; modprobe mptcp_coupled')
    os.system('sysctl -w net.mptcp.mptcp_enabled=0')
    os.system('sysctl -w net.ipv4.tcp_congestion_control={}'.format(cc))
    print('\nTesting bandwidth for {} with loss % {}'.format(cc,loss_percent))
    topo = MyTopo()
    net = Mininet(topo = topo, link=TCLink)
    topo.setup_routing(net)
    net.start()
    time.sleep(1)
    #CLI(net)
    dst = net.get('h2')
    dst.cmd('iperf -s > tcp_server_output.txt &')
    # test bandwidth between the two hosts
    src = net.get('h1')
    for j in range(1,6):
        src.cmd('iperf -c 10.0.0.2 -t 10 -i 1 > ./loss/tcp_loss_' + str(loss_percent) + '_client_' + str(j) + '.txt')
    net.stop()


if __name__ == '__main__':
    try:
        main()
    except:
        print("-"*80)
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf iperf3; mn -c")

    



