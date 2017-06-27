import struct, socket
import ipaddress

def ipadd(ip, add):
    ip2int = lambda ipstr: struct.unpack('!I', socket.inet_aton(ipstr))[0]
    int2ip = lambda n: socket.inet_ntoa(struct.pack('!I', n))
    return int2ip(int(ipaddress.ip_address(ip2int(ip))+add))

def node_ips(pod, netw, shift):
    nodes = {}
    index = 1
    for srv in sorted(pod['nodes']):
        nodes[srv] = { 'ip': ipadd(netw, shift + index),
                       'shift': shift + index }
        index += 1
    return nodes

def job2nodes(pod):
    jobs = { 'controller': [],
             'compute': [],
             'storage': [],
             'network': [] }
    for srv in sorted(pod['nodes']):
        for job in pod['nodes'][srv]:
            jobs[job].append(srv)
    return jobs

class FilterModule(object):
    '''
    Functions linked to node network interfaces
    '''

    def filters(self):
        return {
            'ipadd': ipadd,
            'node_ips': node_ips,
            'job2nodes': job2nodes,
        }
