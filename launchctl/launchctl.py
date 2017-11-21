#!/usr/bin/env python
'''
Module for controlling Mac OS X daemons via launchctl.
'''
import xml
import subprocess
import plistlib
import sys
import os


class ExecException(Exception):
    '''
    Exception raised if executing launchctl returns an error.
    '''
    def __init__(self, msg, stdout=None, stderr=None, *args, **kwargs):
        super(ExecException, self).__init__(msg, *args, **kwargs)
        self.stderr = stderr
        self.stdout = stdout


class ServiceStatus(object):
    '''
    Holds the status of a Service as retrieved from Service.status().
    '''
    def __init__(self, service, pid, status):
        self.service = service
        self.pid     = pid
        self.status  = status


class Service(object):
    '''
    Handle for some launchctl service.
    '''
    database = None

    def __init__(self, path, label):
        self.path  = path
        self.label = label

    @staticmethod
    def get_database(path):
        '''
        Given a path to a directory containing plist files, build the
        Service.database static by parsing those files.
        '''
        if Service.database is not None:
            return Service.database

        Service.database = {}
        for fn in os.listdir(path):
            if not fn.endswith('.plist'):
                continue

            fpath = os.path.join(path, fn)
            try:
                pl = plistlib.readPlist(fpath)
            except xml.parsers.expat.ExpatError:
                continue

            if 'Label' not in pl:
                continue

            label = pl['Label']
            Service.database[label] = Service(fpath, label)

        return Service.database

    @staticmethod
    def get_default_database():
        '''
        Builds the Service.database using the standard LaunchDaemons directory.
        '''
        return Service.get_database('/System/Library/LaunchDaemons/')

    @staticmethod
    def from_label(label):
        '''
        Given a service label (i.e. 'com.apple.tftpd'), return the Service
        object corresponding to that label.
        '''
        return Service.get_default_database().get(label)

    @staticmethod
    def launchctl_exec(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       *args, **kwargs):
        '''
        Invokes launchctl with the specified arguments, communicates with the
        process and checks for error values.
        '''
        cmd = ['/usr/bin/env', 'launchctl'] + cmd
        proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, *args,
                                **kwargs)
        stdout, stderr = proc.communicate()
        if proc.returncode:
            raise ExecException('Error %u executing %s.' % (proc.returncode,
                                                            cmd),
                                stdout=stdout, stderr=stderr)
        return (stdout, stderr)

    def load(self):
        '''
        Invokes launchctl to load the service.
        '''
        Service.launchctl_exec(['load', '-w', self.path])
        print 'Service %s loaded.' % self.label

    def start(self):
        '''
        Invokes launchctl to start the service.
        '''
        Service.launchctl_exec(['start', self.label])
        print 'Service %s started.' % self.label

    def stop(self):
        '''
        Invokes launchctl to stop the service.  Note that the service may be
        automatically restarted by launchd depending on how it works.
        '''
        Service.launchctl_exec(['stop', self.label])
        print 'Service %s stopped.' % self.label

    def unload(self):
        '''
        Invokes launchctl to unload the service.
        '''
        Service.launchctl_exec(['unload', '-w', self.path])
        print 'Service %s unloaded.' % self.label

    def status(self):
        '''
        Returns the Service's most recent status.
        '''
        stdout, _ = Service.launchctl_exec(['list'])
        lines = stdout.splitlines()
        for l in lines:
            if l.endswith(self.label):
                words  = l.split()
                pid    = int(words[0], 10) if words[0] != '-' else None
                status = int(words[1], 10)
                return ServiceStatus(self, pid, status)


def _main():
    if len(sys.argv) < 2:
        print 'usage: launchctl.py <label> [<label2> ...]'
    else:
        for label in sys.argv[1:]:
            service = Service.from_label(label)
            if service:
                status = service.status()
                if status is not None:
                    print '%s: %s (PID: %s RC: %s)' % (label, service.path,
                                                       status.pid,
                                                       status.status)
                else:
                    print '%s: %s' % (label, service.path)
            else:
                print '%s: Not found.' % label


if __name__ == '__main__':
    _main()
