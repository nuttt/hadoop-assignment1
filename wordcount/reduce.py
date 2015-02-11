#!/usr/bin/env python

import sys

# word counter
current_word = None
current_count = None

for line in sys.stdin:
  line = line.strip()

  # first fields go into {word}, the rest go in to {count}
  word, count = line.split('\t', 1)

  count = int(count)

  # counting same key, print when new key is arrive 
  if (word != current_word):
      if(current_word):
        # print as key value pair
        print "%s\t%d" % (current_word, current_count)
      current_count = count
      current_word = word
  else:
    current_count += count

# print out last word
if(current_word):
  print "%s\t%d" % (current_word, current_count)



  
