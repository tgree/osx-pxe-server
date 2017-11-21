#!/usr/bin/python
'''
Module to control the dhcp functionality in the Mac OS X bootpd launchctl
daemon.
'''
import plistlib
import errno
import os

import launchctl
import interface


BOOTPD_PLIST_PATH = '/etc/bootpd.plist'


class Subnet(object):
    '''
    Class that wraps a Subnet entry in the bootpd.plist file.
    '''
    def __init__(self, name, intf, net_range_low, net_range_high, tftp_server,
                 tftp_filename):
        assert intf.is_link_local(net_range_low)
        assert intf.is_link_local(net_range_high)
        assert (interface.ipv4_to_int(net_range_high) >=
                interface.ipv4_to_int(net_range_low))

        self.name           = name
        self.intf           = intf
        self.net_range_low  = net_range_low
        self.net_range_high = net_range_high
        self.tftp_server    = tftp_server
        self.tftp_filename  = tftp_filename

    def to_dict(self):
        '''
        Convert the Subnet into dictionary form appropriate for use with
        plistlib.

        Note: in some discussion forums it seems to imply that the dhcp option
        fields need to be base64 encoded <data> tags.  Here, we are populating
        them instead as plain old UTF-8 <string> tags.  My target device seems
        to be picking up the bootfile name correctly, so maybe things have
        changed or maybe using a <string> always worked.
        '''
        return {'name'           : self.name,
                'net_mask'       : self.intf.net_mask,
                'net_address'    : self.intf.net_addr,
                'net_range'      : [self.net_range_low, self.net_range_high],
                'allocate'       : True,
                'dhcp_option_66' : self.tftp_server,
                'dhcp_option_67' : self.tftp_filename,
               }


def get_config_plist():
    '''Returns the current /etc/bootpd.plist contents.'''
    return plistlib.readPlist(BOOTPD_PLIST_PATH)


def gen_config_plist(ifnames, subnets):
    '''
    Returns a string representation of the plist file defined by the set of
    interfaces and subnets.
    '''
    return plistlib.writePlistToString(
        {'dhcp_enabled' : ifnames,
         'Subnets' : [s.to_dict() for s in subnets],
        })


def enable(plist):
    '''
    Enables the com.apple.bootpd service and populates the /etc/bootpd.plist
    file with the specified plist string.
    '''
    service = launchctl.Service.from_label('com.apple.bootpd')
    service.unload()
    try:
        os.unlink(BOOTPD_PLIST_PATH)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    with open(BOOTPD_PLIST_PATH, 'w') as f:
        f.write(plist)
    service.load()
    service.start()


def disable():
    '''
    Disables the com.apple.bootpd service and removes the /etc/bootpd.plist
    file.
    '''
    service = launchctl.Service.from_label('com.apple.bootpd')
    service.stop()
    service.unload()
    os.unlink(BOOTPD_PLIST_PATH)
