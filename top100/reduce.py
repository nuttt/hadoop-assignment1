#!/usr/bin/env python

import sys

# collect word with same frequence
current_words = []
current_count = None
pos = 0

for line in sys.stdin:

  line = line.strip()

  if not line:
    break

  # put key in {count}, rest in {word}
  count, word = line.split('\t', 1)

  # convert key back to normal number
  count = 1000000-int(count)
  # new key
  if(count != current_count):
    # print old word list (join by tab)
    # print only top 100
    if current_count is not None and pos <= 100:
      print "%d\t%d\t%s" % (pos, current_count, "\t".join(current_words))

    # init new list
    pos += 1
    current_count = count
    current_words = []
  
  # add word to list
  current_words.append(word)

# final list which may not be printed yet
if pos <= 100:
  print "%d\t%d\t%s" % (pos, current_count, "\t".join(current_words))


  
