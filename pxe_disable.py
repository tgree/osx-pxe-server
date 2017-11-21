#!/usr/bin/env python
'''
Tool to disable a pxe server on Mac OS X.
'''
import pxe

if __name__ == '__main__':
    pxe.disable('pxetgree.config')
