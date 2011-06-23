#!/usr/bin/env python
import imp
import sys
import os
import pprint

if '.' not in sys.path:
    sys.path = list('.') + sys.path

from django.core.management import execute_manager

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Can't find the file 'settings.py' in the directory containing %r or it's parent.\n" % __file__)
    sys.exit(1)

import settings

if __name__ == "__main__":
    execute_manager(settings)
