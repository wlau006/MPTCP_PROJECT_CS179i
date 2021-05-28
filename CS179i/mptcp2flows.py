#!/usr/bin/env python

import os
import time
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.net import Mininet

numflows = 2

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
        self.addLink( leftHost, leftSwitch, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch2, bw = 10, delay='5ms', loss=1)
        self.addLink( leftSwitch, rightSwitch)
        self.addLink( leftSwitch2, rightSwitch2)
        self.addLink( rightSwitch, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch2, rightHost, bw = 10, delay='5ms', loss=1)
topos = { 'mytopo': ( lambda: MyTopo() ) }

def main():
    print('\n### TESTING MPTCP ###')
    os.system('modprobe mptcp_balia; modprobe mptcp_wvegas; modprobe mptcp_olia; modprobe mptcp_coupled')
    os.system('sysctl -w net.mptcp.mptcp_enabled=1')
    os.system('sysctl -w net.mptcp.mptcp_path_manager=fullmesh')
    os.system('sysctl -w net.mptcp.mptcp_scheduler=default')
    topo = MyTopo()
    net = Mininet(topo = topo, link=TCLink)
    topo.setup_routing(net)
    net.start()
    time.sleep(1)
    #CLI(net)
    dst = net.get('h2')
    #dst.cmd('iperf3 -s -V > mptcp_server_output_flows_' + numflows + '.txt &')
    dst.cmd('iperf -s > mptcp_server_output.txt &')
    for cc in ['lia', 'olia', 'balia', 'wvegas','cubic','reno','pcc']:
        print('\nTesting bandwidth for {}'.format(cc))

        # set congestion control algoritm
        os.system('sysctl -w net.ipv4.tcp_congestion_control={}'.format(cc))

        # test bandwidth between the two hosts
        src = net.get('h1')        
        for i in range(1, 21):
            #src.cmd('iperf3 -c 10.0.0.2 -V -C ' + cc + ' -t 5 -i 0.2 > ./' + cc + '/mptcp_' + cc +'_client_' + str(i) +'_flows_' + str(numflows) + '.txt')    
            src.cmd('iperf -c 10.0.0.2 -t 10 -i 1 > ./' + cc + '/mptcp_' + cc +'_client_' + str(i) +'_flows_' + str(numflows) + '.txt')
    net.stop()


if __name__ == '__main__':
    try:
        main()
    except:
        print("-"*80)
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf iperf3; mn -c")

    



