#!/usr/bin/python
'''
Module to control the Mac OS X tftpd launchctl daemon.
'''
import errno
import os

import launchctl


TFTP_PUBLIC_PATH = '/private/tftpboot/'


def is_file_published(sub_path):
    '''
    Returns true if the specified sub_path rooted from the base tftp server
    directory is being served up.
    '''
    if os.path.isabs(sub_path):
        return False

    try:
        os.stat(os.path.join(TFTP_PUBLIC_PATH, sub_path))
        return True
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e

    return False


def enable():
    '''Enables the com.apple.tftpd service.'''
    service = launchctl.Service.from_label('com.apple.tftpd')
    service.unload()
    service.load()
    service.start()


def disable():
    '''Disables the com.apple.tftpd service.'''
    service = launchctl.Service.from_label('com.apple.tftpd')
    service.stop()
    service.unload()
