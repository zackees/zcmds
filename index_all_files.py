#! /usr/bin/python

import os
import sys

sys.path.append('.')
import fileutils

def file_size(f):
	try:
		val = os.stat(f).st_size
		return '%s' % val
	except PermissionError:
		return "-1"
	except FileNotFoundError:
		return "-1"

def _main():
	try:
	    for root, dirs, files in os.walk('/', topdown=False):
	        for name in files:
	            f = os.path.abspath(os.path.join(root, name))
	            print('"%s", %s' % (f, file_size(f)))
	except KeyboardInterrupt:
		sys.exit(1)


if __name__ == "__main__":
  _main()
