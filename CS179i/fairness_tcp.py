#!/usr/bin/env python

import os
import time
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.net import Mininet

numflows = 2
numclients = 2
numservers = 2


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
        leftHost2 = self.addHost( 'h3' )
        rightHost2 = self.addHost( 'h4' )
        leftSwitch = self.addSwitch( 's1' )
        leftSwitch2 = self.addSwitch( 's2' )
        rightSwitch = self.addSwitch( 's3' )        
        rightSwitch2 = self.addSwitch( 's4' )

        # Add links
        self.addLink( leftHost, leftSwitch, bw = 10)
        self.addLink( leftHost, leftSwitch2, bw = 10)
        self.addLink( leftHost2, leftSwitch, bw = 10)
        self.addLink( leftHost2, leftSwitch2, bw = 10)
        self.addLink( leftSwitch, rightSwitch, bw = 10)
        self.addLink( leftSwitch2, rightSwitch2, bw = 10)
        self.addLink( rightSwitch, rightHost, bw = 10)
        self.addLink( rightSwitch2, rightHost, bw = 10)
        self.addLink( rightSwitch, rightHost2, bw = 10)
        self.addLink( rightSwitch2, rightHost2, bw = 10)
topos = { 'mytopo': ( lambda: MyTopo() ) }

def main():
    print('\n### TESTING SPTCP ###')
    os.system('modprobe mptcp_balia; modprobe mptcp_wvegas; modprobe mptcp_olia; modprobe mptcp_coupled')
    os.system('sysctl -w net.mptcp.mptcp_enabled=0')
    for cc in ['cubic','reno','pcc']:
        topo = MyTopo()
        net = Mininet(topo = topo, link=TCLink)
        topo.setup_routing(net)
        net.start()
        time.sleep(1)
        #CLI(net)
        src = net.get('h1') 
        dst = net.get('h2')
        src2 = net.get('h3')
        dst2 = net.get('h4')
        dst.cmd('iperf -s &')
        dst2.cmd('iperf -s &')
        print('\nTesting bandwidth for {}'.format(cc))

        # set congestion control algoritm
        os.system('sysctl -w net.ipv4.tcp_congestion_control={}'.format(cc))

        src.cmd('iperf -c ' + dst.IP() + ' -t 10 -i 0.2 > ./twohost/' + cc + '/host_1_tcp_' + str(numclients) +'_client_' + str(numservers) + '_server_' + str(numflows) + '_flows.txt &')
        time.sleep(5)
        src2.cmd('iperf -c ' + dst2.IP() + ' -t 10')
        src.cmd('iperf -c ' + dst.IP() + ' -t 10 &')
        time.sleep(5)
        src2.cmd('iperf -c ' + dst2.IP() + ' -t 10 -i 0.2 > ./twohost/' + cc + '/host_2_tcp_' + str(numclients) +'_client_' + str(numservers) + '_server_' + str(numflows) + '_flows.txt')
        net.stop()


if __name__ == '__main__':
    try:
        main()
    except:
        print("-"*80)
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf iperf3; mn -c")

    



