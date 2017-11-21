#!/usr/bin/env python
'''
Tool to manage a pxe server on Mac OS X.
'''
import interface
import bootpd
import tftpd


class PXEException(Exception):
    '''
    Exception thrown if an error occurs enabling or disabling the PXE server.
    '''
    pass


def enable(config_name, ifname, first_ip, last_ip, bootfile):
    '''
    Set up dhcpd and tftpd to serve up ip addresses in the specified range and
    the specified bootfile on the specified interface and tags the
    configuration as named config_name.
    '''
    if not tftpd.is_file_published(bootfile):
        raise PXEException('%s not found in %s' % (bootfile,
                                                   tftpd.TFTP_PUBLIC_PATH))

    intf   = interface.from_ifname(ifname)
    subnet = bootpd.Subnet(config_name, intf, first_ip, last_ip, intf.ip,
                           bootfile)
    plist  = bootpd.gen_config_plist([ifname], [subnet])

    tftpd.enable()
    bootpd.enable(plist)


def disable(config_name):
    '''
    Disables the dhcpd and tftpd daemons if the current configuration is named
    config_name.
    '''
    plist = bootpd.get_config_plist()
    if plist['Subnets'][0]['name'] != config_name:
        raise Exception('bootpd was configured by some other process.')

    bootpd.disable()
    tftpd.disable()
