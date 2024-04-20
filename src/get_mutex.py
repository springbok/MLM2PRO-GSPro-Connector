"""
    Name:

        GetMutex.py

    Description:

        Provides a method by which an application can ensure that only one
        instance of it can be running at any given time.

    Usage:

        if (app := GetMutex()).IsRunning():
            print("Application is already running")
            sys.exit()
                                                                             """

import os
import sys

from win32event import CreateMutex
from win32api   import CloseHandle, GetLastError
from winerror   import ERROR_ALREADY_EXISTS

class GetMutex:
    """ Limits application to single instance """

    def __init__(self):
        thisfile   = os.path.split(sys.argv[0])[-1]
        self.name  = thisfile + "_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = CreateMutex(None, False, self.name)
        self.error = GetLastError()

    def IsRunning(self):
        return (self.error == ERROR_ALREADY_EXISTS)

    def __del__(self):
        if self.mutex: CloseHandle(self.mutex)

if __name__ == "__main__":
    # check if another instance of this program is running
    if (myapp := GetMutex()).IsRunning():
        print("Another instance of this program is already running")
        sys.exit(0)

    # not running, safe to continue...
    print("No another instance is running, can continue here")

    try:
        while True: pass
    except KeyboardInterrupt: pass