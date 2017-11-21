#!/usr/bin/env python
'''
Tool to enable a pxe server on Mac OS X.
'''
import argparse

import pxe

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', '-i', required=True)
    parser.add_argument('--first-ip', '-f', required=True)
    parser.add_argument('--last-ip', '-l', required=True)
    parser.add_argument('--bootfile', '-b', required=True)
    rv = parser.parse_args()

    try:
        pxe.enable('pxetgree.config', rv.interface, rv.first_ip, rv.last_ip,
                   rv.bootfile)
    except pxe.PXEException as e:
        print e
