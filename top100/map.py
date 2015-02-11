#!/usr/bin/env python

import sys

for line in sys.stdin:
    line = line.strip()
    if line:
      word, count = line.split()

      # use {count} as key instead
      # add leading zero for correct lexicographical order
      # minus from 1000000 for descending sort order
      print "%07d\t%s" % (1000000-int(count), word)