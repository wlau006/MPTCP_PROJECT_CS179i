#!/usr/bin/python
"""Custom topology example
Two directly connected switches plus a host for each switch:
   host --- switch --- switch --- host
Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

import sys
from subprocess import Popen, PIPE
from time import sleep
import argparse
import os
import itertools
import random
import getopt

from mininet.net import Mininet
from mininet.link import Link, TCLink
from mininet.util import *
from mininet.node import *
from mininet.topo import Topo
from mininet.cli  import *

if 'PYTHONPATH' in os.environ:
    sys.path = os.environ[ 'PYTHONPATH' ].split( ':' ) + sys.path

CONTROLLERS = { 'ref': Controller,
                'ovsc': OVSController,
                'nox': NOX,
                'remote': RemoteController,
                'none': lambda name: None }

def usage():
    print "./mptcp.py [--cc congestion_control] [--verbose]"
    print "--cc specify the congestion control - default: coupled"
    print "--verbose verbose output, sending it to the filesystem"

global wmem_min
global wmem_max
global rmem_min
global rmem_max
global capa_min
global capa_max
global del_min
global del_max
global loss_min
global loss_max
global mlat_min
global mlat_max
global jitter_min
global jitter_max

global tests
global setloss
global istcp
global rbuf
global cwnd

istcp = False
setloss = False
rbuf = False
cwnd = False


class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self , test='' ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'client' )
        rightHost = self.addHost( 'server' )
        leftSwitch1 = self.addSwitch( 's11' )
        rightSwitch1 = self.addSwitch( 's12' )
        leftSwitch2 = self.addSwitch( 's21' )
        rightSwitch2 = self.addSwitch( 's22' )

        # Add links
        self.addLink( leftHost, leftSwitch1 )
        self.addLink( leftSwitch1, rightSwitch1 )
        self.addLink( rightSwitch1, rightHost )

        self.addLink( leftHost, leftSwitch2 )
        self.addLink( leftSwitch2, rightSwitch2 )
        self.addLink( rightSwitch2, rightHost )

        if test.find("back") != -1:
            back1host = self.addHost( 'back1' )
            self.addLink ( back1host, leftSwitch1 )
            back2host = self.addHost( 'back2' )
            self.addLink ( back2host, leftSwitch2 )

topos = { 'mytopo': ( lambda: MyTopo() ) }


def parseIperf( iperfOutput ):
    """Parse iperf output and return bandwidth.
        iperfOutput: string
        returns: result string"""
    r = r'([\d\.]+ \w+/sec)'
    m = re.findall( r, iperfOutput )
    if m:
        return m[-1]
    else:
        # was: raise Exception(...)
        error( 'could not parse iperf output: ' + iperfOutput )
        return ''

def iperfserver(s, c):
    s.sendCmd( 'iperf -s', printPid=True )
    servout = ''
    while s.lastPid is None:
        servout += s.monitor()

    while 'Connected' not in c.cmd('sh -c "echo A | telnet -e A %s 5001"' % s.IP()):
        sleep(.5)

    return servout

def iperfclient(c, ip, sleeper=-1, time=600):
    if sleeper == -1:
        sleeper = round(random.random()*5,1)
    print "Sleeping for "+str(sleeper)+" seconds"
    #c.sendCmd( 'sleep '+str(sleeper)+' ; iperf -c '+ip+' -t 60 -i 20')
    c.sendCmd( 'sleep '+str(sleeper)+' ; iperf -c '+ip+' -t '+str(time))

def iperf(net):
    b1 = net.get('back1')
    c1 = net.get('client')
    s1 = net.get('server')

    iperfclient(c1, s1.IP(), 0)
    iperfclient(b1, s1.IP(), 5)

    co1 = c1.waitOutput()
    bo1 = b1.waitOutput()

    s1.sendInt()
    so1 = s1.waitOutput()

    result = [ parseIperf(co1), parseIperf(bo1) ]

    return result

def setIPs(net, ip, host, itfidx):
    cli = net.get(host)
    itf = cli.intf(host+'-eth'+itfidx)
    cli.setIP(ip, prefixLen=16, intf=itf)

def blockCross(net, prefix1, prefix2, host1, host2):
    h1 = net.get(host1)
    h2 = net.get(host2)

    h1.cmd('iptables -A OUTPUT -s '+prefix1+' -d '+prefix2+' -j DROP')
    h1.cmd('iptables -A OUTPUT -s '+prefix2+' -d '+prefix1+' -j DROP')

def limit_link(net, path, bw, delay, jitter, loss, max_latency, verbose=False, mtu=1500):
    s1 = net.get('s'+ path + '1')
    s2 = net.get('s'+ path + '2')

    itf1 = s1.intf(s1.name+'-eth2')
    itf2 = s2.intf(s2.name+'-eth1')

    max_queue_size = int(float(delay) * bw * 1024 * 1024 / (mtu * 8 * 1000))
    max_queue_size += int(float(max_latency) * bw * 1024 * 1024 / (mtu * 8 * 1000))
    if max_queue_size <= 10:
        max_queue_size = 10

    itf1.config(bw=bw, delay=str(delay/2)+'ms', jitter=str(jitter/2)+'ms', loss=loss, max_queue_size=max_queue_size, use_tbf=False)
    os.system("tc qdisc show dev "+s1.name+'-eth2')
    os.system("tc class show dev "+s1.name+'-eth2')

    itf2.config(bw=bw, delay=str(delay/2)+'ms', jitter=str(jitter/2)+'ms', loss=loss, max_queue_size=max_queue_size, use_tbf=False)
    os.system("tc qdisc show dev "+s2.name+'-eth1')
    os.system("tc class show dev "+s2.name+'-eth1')

def do_exp(setup, verbose=False):
    print setup

    f = setup['f']
    net = setup['net']
    wmem = str(setup['wmem'])
    rmem = str(setup['rmem'])
    bw1 = setup['bw1']
    bw2 = setup['bw2']
    d1 = setup['d1']
    d2 = setup['d2']
    m1 = setup['m1']
    m2 = setup['m2']
    j1 = setup['j1']
    j2 = setup['j2']
    l1 = setup['l1']
    l2 = setup['l2']
    test = setup['test']
    cong = setup['cong']

    h1 = net.get('client')
    h2 = net.get('server')

    os.system('sysctl -w net.ipv4.tcp_wmem="4096    16384 '+wmem+'"')
    os.system('sysctl -w net.ipv4.tcp_rmem="10240   87380 '+rmem+'"')

    limit_link(net, '1', bw=bw1, delay=d1, jitter=j1, loss=l1, max_latency=m1, verbose=verbose)
    limit_link(net, '2', bw=bw2, delay=d2, jitter=j2, loss=l2, max_latency=m2, verbose=verbose)

    os.system('sysctl -w net.ipv4.tcp_congestion_control='+cong)
    os.system('sysctl -w net.mptcp.mptcp_ndiffports=0')

    print h1.cmd("ping -c 2 10.0.0.2")
    print h1.cmd("ping -c 2 10.1.0.2")

    if verbose:
        folder = '/tmp/'+wmem+'_'+rmem+'_'+str(bw1)+'_'+str(bw2)+'_'+str(d1)+'_'+str(d2)+'_'+str(m1)+'_'+str(m2)+'_'+str(j1)+'_'+str(j2)+'_'+str(l1)+'_'+str(l2)+'_'+cong+'_'+test
        os.system('rm -Rf '+folder)
        os.system('mkdir '+folder)
        h1.cmd('nstat')
        h2.cmd('nstat')

    if test == 'iperf20':
        if verbose:
            s1 = net.get('s11')
            s2 = net.get('s21')

            os.system('tcpdump -i '+s1.name+'-eth2 -n -s 150 -w '+folder+'/dump1.dump port 5001 &')
            os.system('tcpdump -i '+s2.name+'-eth2 -n -s 150 -w '+folder+'/dump2.dump port 5001 &')
            time.sleep(3)

        if rbuf or cwnd:
            os.system('sudo dmesg -c')
        res = net.iperf(args='-t 60 -i 30')
        if rbuf or cwnd:
           time.sleep(5)
           buf = os.system('sudo dmesg -c > /tmp/dmesg')
           bfile = open('/tmp/dmesg')
           if rbuf:
               l = bfile.readline()
               while l.find("events") != -1:
                   l = bfile.readline()
               l = bfile.readline()
               while l.find("events") != -1:
                   l = bfile.readline()
               f.write(str(setup)+' res:'+str(res[1])+' rbuf:'+l.split(' ')[-1].rstrip('\n')+'\n')
           else:
               l1 = bfile.readline()
               while l1.find("events") != -1:
                   l1 = bfile.readline()
               l2 = bfile.readline()
               while l2.find("events") != -1:
                   l2 = bfile.readline()
               f.write(str(setup)+' res:'+str(res[1])+' cwnd1:'+l1.split(' ')[-1].rstrip('\n')+' cwnd2:'+l2.split(' ')[-1].rstrip('\n')+'\n')
           bfile.close()
        else:
           f.write(str(setup)+' res:'+str(res[1])+'\n')
        f.flush()

        if verbose:
            os.system('killall tcpdump')
            time.sleep(1)
            h1.cmd('nstat > '+folder+'/client_nstat')
            h2.cmd('nstat > '+folder+'/server_nstat')

            nf = open(folder+'/iperf_res', 'w')
            nf.write(str(setup)+' '+folder+' res:'+str(res[1])+'\n')
            nf.flush()
            nf.close()
    elif test.find("backiperf") != -1:
        os.system('killall -9 iperf')
        ind = test.find("backiperf")+len("backiperf")
        num = test[ind:ind+1]
        os.system('sysctl -w net.mptcp.mptcp_ndiffports='+num)

        iperfserver(h2, h1)

        res = iperf(net)
        f.write(str(setup)+' res:'+str(res)+'\n')
        f.flush()
    elif test.find("backnetp") != -1:
        b1 = net.get('back1')
        b2 = net.get('back2')
        ind = test.find("backnetp")+len("backnetp")
        size = test[ind:len(test)]
        
        os.system('killall -9 iperf')
        iperfserver(h2, h1)

        iperfclient(b1, h2.IP(), sleeper=0, time=70)
        iperfclient(b2, '10.1.0.2', sleeper=0, time=70)

        time.sleep(5)

        p1 = h1.popen(['netperf', '-j -H '+h2.IP()+' -P 0 -t omni -l 60  -- -c -D -r '+size+',1K -o /root/output'], shell = True)
        r2 = h1.cmd('netperf -j -H 10.1.0.2 -P 0 -t omni -l 60  -- -c -D -r '+size+',1K -o /root/output')
        r2 = r2.rstrip('\n')

        r1, e1 = p1.communicate()
        p1.wait()
        r1 = r1.rstrip('\n')

        bo1 = b1.waitOutput()
        bo2 = b2.waitOutput()

        h2.sendInt()
        h2.waitOutput()

        print bo1
        print bo2
        print r1
        print r2

        result = [ parseIperf(bo1), parseIperf(bo2) ]

        f.write(str(setup)+ ' netp1:'+r1+' netp2:'+r2+' iperf:'+str(result)+'\n')
        f.flush()

        if verbose:
            h1.cmd('nstat > '+folder+'/client_nstat')
            h2.cmd('nstat > '+folder+'/server_nstat')
    else:
        print "Undefined TEST!!! : "+test

#
# Creates the dictionary that describes a setup
#
def get_setup(f, net, test, wmem, rmem, bw1, bw2, del1, del2, mlat1, mlat2, loss1, loss2, jitter1, jitter2, cc):
    tup = (f, net, test, wmem, rmem, bw1, bw2, del1, del2, mlat1, mlat2, loss1, loss2, jitter1, jitter2, cc)

    setup = dict(zip(('f', 'net', 'test', 'wmem', 'rmem', 'bw1', 'bw2', 'd1', 'd2', 'm1', 'm2', 'l1', 'l2', 'j1', 'j2', 'cong'), tup))

    return setup

def myrangei(mini, maxi, weight):
    if mini == maxi:
        return [mini]
    mid = (maxi + mini)/2.0
    return [max(int(mid - (mid - mini)*weight), mini), min(int(mid+(mid-mini)*weight), maxi)]

def myrangef(mini, maxi, weight):
    if mini == maxi:
        return [mini]
    mid = (maxi + mini)/2.0
    return [max(round((mid - (mid - mini)*weight), 1), mini), min(round((mid+(mid-mini)*weight), 1), maxi)]

#
# Uniform random distribution plan generator
#
def rand(f, net, test, cc, numexps=100000, w=1, expfile=None):
    i = numexps

    seed = time.time()
    print "!!!! RANDOM NUMBER GENERATOR-SEED: "+str(seed)
    random.seed(seed)
    while i != 0:
        i -= 1

        wmem = random.randint(wmem_min, wmem_max)
        rmem = random.randint(rmem_min, rmem_max)
        bw1 = round(random.uniform(capa_min, capa_max), 1)
        bw2 = round(random.uniform(capa_min, capa_max), 1)
        del1 = round(random.uniform(del_min, del_max), 1)
        del2 = round(random.uniform(del_min, del_max), 1)
        loss1 = round(random.uniform(loss_min, loss_max), 1)
        loss2 = round(random.uniform(loss_min, loss_max), 1)
        mlat1 = round(random.uniform(mlat_min, mlat_max), 1)
        mlat2 = round(random.uniform(mlat_min, mlat_max), 1)
        jitter1 = round(random.uniform(jitter_min, jitter_max), 1)
        jitter2 = round(random.uniform(jitter_min, jitter_max), 1)

        yield get_setup(f, net, test, wmem, rmem, bw1, bw2, del1, del2, mlat1, mlat2, loss1, loss2, jitter1, jitter2, cc)

def get_value(l, pattern):
    search = "'"+pattern+"': "
    start = l.find(search)+len(search)

    end = l.find(',', start)
    if end == -1 or end - start > 14:
        # It is the last element of the list - it ends with }
        end = l.find('}', start)

    if end == -1:
        print "end is -1!!!"
        print l
        print pattern
        sys.exit(1)

    if l[start:end] == "None":
        return 0
    return round(float(l[start:end]), 1)

def get_value_string(l, pattern):
    search = "'"+pattern+"': '"
    start = l.find(search)+len(search)

    end = l.find("'", start)
    if end == -1:
        # It is the last element of the list - it ends with }
        end = l.find('}', start)

    if end == -1:
        print "end is -1!!!"
        print l
        print pattern
        sys.exit(1)

    return l[start:end]

def file(f, net, test, cc, numexps=100000, w=1.0, expfile=None):
    sets = open(expfile)

    for l in sets:
        wmem = int(get_value(l, "wmem"))
        rmem = int(get_value(l, "rmem"))
        bw1 = get_value(l, "bw1")
        bw2 = get_value(l, "bw2")
        del1 = get_value(l, "d1")
        del2 = get_value(l, "d2")
        loss1 = get_value(l, "l1")
        loss2 = get_value(l, "l2")
        mlat1 = get_value(l, "m1")
        mlat2 = get_value(l, "m2")
        jitter1 = get_value(l, "j1")
        jitter2 = get_value(l, "j2")

        cong = get_value_string(l, "cong")
        test = get_value_string(l, "test")

        yield get_setup(f, net, test, wmem, rmem, bw1, bw2, del1, del2, mlat1, mlat2, loss1, loss2, jitter1, jitter2, cong)

def get_float(v, mini, maxi):
    return round(float(mini) + (maxi - mini) * float(v), 1)

def rfile(f, net, test, cc, numexps=10000, w=1.0, expfile=None):
    sets = open(expfile)

    for l in sets:
        l = l.rstrip("\n")
        s = l.split(' ')

        wmem = wmem_min
        rmem = rmem_min

        # In this case, we have a 3/4-dimensional plan
        if test == "backiperf2":
            bw1 = get_float(s[0], capa_min, capa_max)
            d1 = get_float(s[1], del_min, del_max)
            m1 = get_float(s[2], mlat_min, mlat_max)
            if len(s) > 3 and setloss == True:
                l1 = get_float(s[4], loss_min, loss_max)
            else:
                l1 = loss_min
            j1 = jitter_min
            bw2 = 10
            d2 = 0
            m2 = 0
            l2 = 0
            j2 = jitter_min
        else:
            bw1 = get_float(s[0], capa_min, capa_max)
            bw2 = get_float(s[1], capa_min, capa_max)
            d1 = get_float(s[2], del_min, del_max)
            d2 = get_float(s[3], del_min, del_max)
            m1 = get_float(s[4], mlat_min, mlat_max)
            m2 = get_float(s[5], mlat_min, mlat_max)
            if len(s) > 6 and setloss == True:
                l1 = get_float(s[6], loss_min, loss_max)
                l2 = get_float(s[7], loss_min, loss_max)
            else:
                l1 = loss_min
                l2 = loss_min
            j1 = jitter_min
            j2 = jitter_min


        yield get_setup(f, net, test, wmem, rmem, bw1, bw2, d1, d2, m1, m2, l1, l2, j1, j2, cc) 
    
def do_exps(f, net, test, cc, verbose, plan, numexps=100000, w=1.0, expfile=None):

    dicts = plan(f, net, test, cc, numexps=numexps, w=w, expfile=expfile)

    for dic in dicts:
        do_exp(dic, verbose)

# !!!! When changing wmem_min here, we also have to change it in twokfactor and compositecenter - the generator only takes a single value for wmem
wmem_min = int(8 * 1024 * 1024)
# !!!! When changing wmem_min here, we also have to change it in twokfactor - the generator only takes a single value for wmem
wmem_max = int(8 * 1024 * 1024)

rmem_min = int(8 * 1024 * 1024)
rmem_max = int(8 * 1024 * 1024)

capa_min = 0.1
capa_max = 100

del_min = 0
del_max = 400

loss_min = 0
loss_max = 2.5

mlat_min = 0
mlat_max = 2000

jitter_min = 0
jitter_max = 0

tests = vars()

def main(argv):
    global setloss
    global istcp
    global del_max
    global mlat_max
    global rbuf
    global cwnd
    
    try:
        optlist, fname = getopt.getopt(sys.argv[1:], '', ['cc=', 'verbose', 'plan=', 'numexps=', 'w=', 'expfile=', 'loss', 'test=', 'tcp', 'lowbdp', 'rbuf', 'cwnd'])
    except  getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    cc = 'coupled'
    verbose = False
    plan = tests['random']
    test = 'iperf20'

    num_exps = 1000000
    w = 1.0
    exp_file = None

    for o, a in optlist:
        if o == "--cc":
            cc = a
        if o == "--verbose":
            verbose = True
        if o == "--plan":
            plan = tests[a]
        if o == "--numexps":
            num_exps = int(a)
        if o == "--w":
            w = float(a)
        if o == "--expfile":
            exp_file = a
        if o == "--loss":
            setloss = True
        if o == "--tcp":
            istcp = True
        if o == "--test":
            test = a
        if o == "--lowbdp":
            del_max = 50.0
            mlat_max = 100.0
        if o == "--rbuf":
            rbuf = True
        if o == "--cwnd":
            cwnd = True

    "Create and run experiment"
    topo = MyTopo(test=test)

    net = Mininet(topo=topo, link=TCLink)

    net.start()
    
    setIPs(net, '10.0.0.1', 'client', '0')
    setIPs(net, '10.0.0.2', 'server', '0')
    setIPs(net, '10.1.0.1', 'client', '1')
    setIPs(net, '10.1.0.2', 'server', '1')
    if test.find("back") != -1:
        setIPs(net, '10.0.0.3', 'back1', '0')
        setIPs(net, '10.1.0.3', 'back2', '0')
    blockCross(net, '10.0.0.0/16', '10.1.0.0/16', 'client', 'server')

    f = open('/tmp/'+fname[0], 'a')
    os.system('sysctl -w net.ipv4.tcp_no_metrics_save=1')

    if istcp:
        net.get('client').cmd("sysctl -w net.mptcp.mptcp_enabled=0")

    if test.find("back") != -1:
        net.get('back1').cmd("sysctl -w net.mptcp.mptcp_enabled=0")
        net.get('back2').cmd("sysctl -w net.mptcp.mptcp_enabled=0")

    if test.find("netp") != -1:
        os.system('killall -9 netserver')
        print net.get('server').pexec('netserver -N')

    do_exps(f=f, net=net, test=test, cc=cc, verbose=verbose, plan=plan, numexps=num_exps, w=w, expfile=exp_file)

    f.close()

    net.stop()

if __name__ == '__main__':
    main(sys.argv)