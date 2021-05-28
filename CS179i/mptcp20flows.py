#!/usr/bin/env python

import os
import time
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.net import Mininet

numflows = 20

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
        leftSwitch2 = self.addSwitch( 's2' )
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's3' )        
        rightSwitch2 = self.addSwitch( 's4' )
        leftSwitch3 = self.addSwitch( 's5' )
        rightSwitch3 = self.addSwitch( 's6' )
        leftSwitch4 = self.addSwitch( 's7' )
        rightSwitch4 = self.addSwitch( 's8' )

        leftSwitch5 = self.addSwitch( 's9' )
        rightSwitch5 = self.addSwitch( 's10' )
        
        leftSwitch6 = self.addSwitch( 's11' )
        rightSwitch6 = self.addSwitch( 's12' )

        leftSwitch7 = self.addSwitch( 's13' )
        rightSwitch7 = self.addSwitch( 's14' )

        leftSwitch8 = self.addSwitch( 's15' )
        rightSwitch8 = self.addSwitch( 's16' )

        leftSwitch9 = self.addSwitch( 's17' )
        rightSwitch9 = self.addSwitch( 's18' )

        leftSwitch10 = self.addSwitch( 's19' )
        rightSwitch10 = self.addSwitch( 's20' )

        leftSwitch11 = self.addSwitch( 's21' )
        rightSwitch11 = self.addSwitch( 's22' )

        leftSwitch12 = self.addSwitch( 's23' )
        rightSwitch12 = self.addSwitch( 's24' )

        leftSwitch13 = self.addSwitch( 's25' )
        rightSwitch13 = self.addSwitch( 's26' )

        leftSwitch14 = self.addSwitch( 's27' )
        rightSwitch14 = self.addSwitch( 's28' )

        leftSwitch15 = self.addSwitch( 's29' )
        rightSwitch15 = self.addSwitch( 's30' )

        leftSwitch16 = self.addSwitch( 's31' )
        rightSwitch16 = self.addSwitch( 's32' )

        leftSwitch17 = self.addSwitch( 's33' )
        rightSwitch17 = self.addSwitch( 's34' )
        
        leftSwitch18 = self.addSwitch( 's35' )
        rightSwitch18 = self.addSwitch( 's36' )

        leftSwitch19 = self.addSwitch( 's37' )
        rightSwitch19 = self.addSwitch( 's38' )

        leftSwitch20 = self.addSwitch( 's39' )
        rightSwitch20 = self.addSwitch( 's40' )

        # Add links
        self.addLink( leftHost, leftSwitch, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch2, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch3, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch4, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch5, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch6, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch7, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch8, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch9, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch10, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch11, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch12, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch13, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch14, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch15, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch16, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch17, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch18, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch19, bw = 10, delay='5ms', loss=1)
        self.addLink( leftHost, leftSwitch20, bw = 10, delay='5ms', loss=1)
        self.addLink( leftSwitch, rightSwitch)
        self.addLink( leftSwitch2, rightSwitch2)
        self.addLink( leftSwitch3, rightSwitch3)
        self.addLink( leftSwitch4, rightSwitch4)
        self.addLink( leftSwitch5, rightSwitch5)
        self.addLink( leftSwitch6, rightSwitch6)
        self.addLink( leftSwitch7, rightSwitch7)
        self.addLink( leftSwitch8, rightSwitch8)
        self.addLink( leftSwitch9, rightSwitch9)
        self.addLink( leftSwitch10, rightSwitch10)
        self.addLink( leftSwitch11, rightSwitch11)
        self.addLink( leftSwitch12, rightSwitch12)
        self.addLink( leftSwitch13, rightSwitch13)
        self.addLink( leftSwitch14, rightSwitch14)
        self.addLink( leftSwitch15, rightSwitch15)
        self.addLink( leftSwitch16, rightSwitch16)
        self.addLink( leftSwitch17, rightSwitch17)
        self.addLink( leftSwitch18, rightSwitch18)
        self.addLink( leftSwitch19, rightSwitch19)
        self.addLink( leftSwitch20, rightSwitch20)
        self.addLink( rightSwitch, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch2, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch3, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch4, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch5, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch6, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch7, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch8, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch9, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch10, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch11, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch12, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch13, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch14, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch15, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch16, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch17, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch18, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch19, rightHost, bw = 10, delay='5ms', loss=1)
        self.addLink( rightSwitch20, rightHost, bw = 10, delay='5ms', loss=1)

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
    for cc in ['pcc']:
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

    



