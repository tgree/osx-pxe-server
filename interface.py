#!/usr/bin/env python
'''
Module to wrap an Ethernet interface and a few ip address helpers.
'''
import struct
import socket
import fcntl


# ioctl values on Mac OS
SIOCGIFADDR    = 0xC0206921
SIOCGIFNETMASK = 0xC0206925


def ipv4_to_int(ipv4):
    '''Convert a dotted IPv4 string into a 32-bit integer.'''
    words = ipv4.split('.')
    assert len(words) == 4
    return ((int(words[0], 10) << 24) |
            (int(words[1], 10) << 16) |
            (int(words[2], 10) <<  8) |
            (int(words[3], 10) <<  0))


def int_to_ipv4(val):
    '''Convert a 32-bit integer into a dotted IPv4 string.'''
    return '%u.%u.%u.%u' % ((val >> 24) & 0xFF,
                            (val >> 16) & 0xFF,
                            (val >>  8) & 0xFF,
                            (val >>  0) & 0xFF)


class Interface(object):
    '''Class to wrap an Ethernet interface.'''
    def __init__(self, ifname):
        bifname = struct.pack('256s', ifname[:15])
        s       = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip      = fcntl.ioctl(s.fileno(), SIOCGIFADDR, bifname)
        netmask = fcntl.ioctl(s.fileno(), SIOCGIFNETMASK, bifname)

        self.ifname       = ifname
        self.ip           = socket.inet_ntoa(ip[20:24])
        self.ip_int       = ipv4_to_int(self.ip)
        self.net_mask     = socket.inet_ntoa(netmask[20:24])
        self.net_mask_int = ipv4_to_int(self.net_mask)
        self.net_addr_int = self.ip_int & self.net_mask_int
        self.net_addr     = int_to_ipv4(self.net_addr_int)

    def is_link_local(self, ip):
        '''Returns true if the specified ip is on the local subnet.'''
        return (ipv4_to_int(ip) & self.net_mask_int) == self.net_addr_int


def from_ifname(ifname):
    '''Instantiate an Interface given the interface's kernel name.'''
    return Interface(ifname)
