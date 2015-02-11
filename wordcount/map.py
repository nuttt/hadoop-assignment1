#!/usr/bin/env python

import re
import sys

for line in sys.stdin:
		# remove front/back whitespace
    line = line.strip()
    
    # split word, remove unnecessary punctuation
    words = re.findall('((?:[a-z][^\s]*[a-z])|(?:[a-z]))', line.lower())

    # print as key-value pair, divided by tab
    for word in words:
        print "%s\t%d" % (word, 1)
