Assignment I : Hadoop
==========================
ณัฐพล พัฒนาวิจิตร 5431010121

ขั้นตอนการทำ MapReduce
-----------
ในที่นี้ได้แบ่งขั้นตอนการทำ MapReduce เป็นสองขั้นตอน ได้แก่

1. การนับคำ
2. การเรียงคำตามความถี่ เพื่อหาคำที่มีจำนวนมากที่สุด 100 คำแรก

### 1. การนับคำ

#### 1.1 Map
ในขั้นตอนการทำ Map นั้น ได้ทำการแบ่งประโยคในแต่ละบรรทัดออกมาเป็นคำ โดยใช้ Regular Expression ช่วยในการทำอักขระที่เป็นสัญลักษณ์ที่มักจะอยู่ติดกับคำ เช่น `" -- ! . ?` ออก และทำการตัดแบ่งคำตาม Spacebar แล้วจึงแปลงแต่ละคำให้เป็น  Key-Value Pair โดยมี Key เป็นคำนั้นๆ และมี Value เป็น 1 เพื่อเอาไปทำการนับต่อไป โดยในการใช้งาน Hadoop แบบ Hadoop Streaming นั้น Key และ Value จะทำการคั่นด้วย Tab (`\t`)

**Sourcecode `wordcount/map.py`**

```
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

```

#### 1.2 Reduce

ในขั้นตอนการ Reduce ได้ทำการรวมจำนวนคำที่เป็นคำเดียวกัน ซึ่งจะมี Key เดียวกัน โดยใน Hadoop Streaming นั้น Key-Value Pair จะเข้ามาโดยเรียงตาม Key ดังนั้น Key เดียวกันก็จะอยู่ติดกันเสมอ จึงทำการนับเพิ่มเมื่อเจอ Key เดียวกัน และแสดงผลลัพท์ของ Key เดิมเมื่อเจอ Key ใหม่

**Sourcecode `wordcount/reduce.py`**

```
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
  
```

### 2. การเรียงคำตามความถี่ เพื่อหาคำที่มีจำนวนมากที่สุด 100 คำแรก

#### 2.1 Map

ทำการแปลง Input ที่ให้อยู่ในรูป Key-Value Pair (คำ, จำนวน)  ให้อยู่ในรูป Key-Value Pair ของ (*1,000,000 - จำนวน*, *คำ*) โดยคำที่มีจำนวนเดียวกันก็จะมี Key เดียวกัน เพื่อให้ Hadoop ทำการ Sort ตามจำนวนคำ (Sort ตาม Key)  ก่อนที่จะส่งต่อไปยังขั้นตอนการ Reduce และใช้ Key เป็น  *1,000,000 - จำนวน* เพื่อ Sort จากมากไปน้อย

ข้อที่ต้องระวังคือ Hadoop Streaming นั้นใช้ Key และ Value เป็น String เมื่อทำการ Sorting ก็จะทำการ Sort แบบตามตัวอักษรไปด้วย (Lexicographical Order) ดังนั้นจึงต้องแสดง Key โดยมี 0 นำหน้า เพื่อให้การ Sort นั้นทำได้ถูกต้อง

**Sourcecode: `top100/map.py`**

```
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
```

#### 2.2 Reduce

ในขั้นตอนนี้ ทำการแสดงผล 100 คำแรกที่มีความถี่สูงสุด เนื่องจาก Hadoop จะทำการ  Sort key มาให้แล้วก่อนที่จะใส่เข้ามาในขั้นตอน Reduce ดังนั้นเราจึงสามารถนับจำนวนคำที่แสดงผลไปแล้วจนกว่าจะครบ 100 อันดับจึงหยุดแสดงผล โดยในที่ได้ทำการรวมคำที่มีความถี่เท่าคันเข้าไปอยู่ในอันดับเดียวกันด้วย

วิธีการนี้จะใช้ได้เมื่อ Reduce ทำงานบนเครื่องเดียวเท่านั้น เวลาการใช้งานอาจจะต้องใส่ Parameter `-numReduceTasks 1` เมื่อ Hadoop ทำงานอยู่บนหลายๆ เครื่อง เพื่อบังคับให้ Reduce ทำงานอยู่บนเครื่องเดียว

**Sourcecode: `top100/reduce.py`**

```
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

```


ขั้นตอนการติดตั้งและใช้งาน
---------------------------------------

### 1. ติดตั้งและใช้งาน Hadoop บน Docker

1. โหลด Container ของ Hadoop สำหรับ Docker
	
		docker pull sequenceiq/hadoop-docker:2.6.0
	
2. Start Hadoop Container

		docker run -i -t -P -v ~/hadoop1:/data sequenceiq/hadoop-docker:2.6.0 /etc/bootstrap.sh -bash

	โดยได้กำหนด Parameter ดังนี้
	- `-i` เปิด stdin ค้างไว้เพื่อใส่ Input ได้
	- `-t` จำลองการทำงานของ TTY (Terminal)
	- `-P` ทำการ Map Port ทั้งหมดของ Docker container เข้าสู่ Host machine
	- `-v ~/hadoop1:/data`  เชื่อมต่อ Folder `~/hadoop1` จากเครื่อง Host เข้ากับ `/data` ใน Docker container

	และให้ Container ทำการรัน `/etc/bootstrap.sh -bash` เพื่อเริ่มต้นการทำงาน Process ของ Hadoop และเปิด Bash Shell

3. ตั้ง Working Directory ไปอยู่ที่ Hadoop

		cd $HADOOP_PREFIX

4. Copy Input File เข้าไปใน HDFS (Hadoop File System)

	ในที่นี้ได้ทำการ Copy โฟลเดอร์ `/data/input-hp` เข้าไปใน `/user/root/data` ใน HDFS

		bin/hadoop fs -copyFromLocal /data/input-hp /user/root/data
		
			เมื่อทำการ ls ดูด้วยคำสั่ง

		bin/hadoop fs -ls /user/root/data

	จะได้ผลลัพท์ดังนี้

		Found 1 items
		-rw-r--r--   1 root supergroup     986859 2015-02-10 23:39 /user/root/data/HP-HalfBloodPrice.txt

5. ประมวลผล MapReduce ด้วย Hadoop Streaming

	ทำการรัน WordCount ด้วย Hadoop Streaming ดังนี้
	
		bin/hadoop jar share/hadoop/tools/lib/hadoop-streaming-2.6.0.jar -file /data/wordcount/map.py -mapper /data/wordcount/map.py -file /data/wordcount/reduce.py -reducer /data/wordcount/reduce.py -input /user/root/data/input-hp/* -output /user/root/data/output-wordcount

	โดยมีการตั้งค่า Parameter ดังนี้
	- `-file /data/wordcount/map.py` ใช้ไฟล์ `map.py` จาก Local File
	- `-mapper /data/wordcount/map.py` กำหนด Mapper
	- `-file /data/wordcount/reduce.py` ใช้ไฟล์ `reduce.py` จาก Local File
	- `-reducer /data/wordcount/reduce.py` กำหนด Reducer
	- `-input /user/root/data/input-hp/*` กำหนด Input Path ใน HDFS
	- `-output /user/root/data/output-wordcount` กำหนด Output  Path ใน HDFS

	ทำการรัน Top100 ด้วย Hadoop Streaming ดังนี้

		bin/hadoop jar share/hadoop/tools/lib/hadoop-streaming-2.6.0.jar -file /data/top100/map.py -mapper /data/top100/map.py -file /data/top100/reduce.py -reducer /data/top100/reduce.py -input /user/root/data/output-wordcount/part-* -output /user/root/data/output-top100

6. ดูผลลัพท์ผ่าน Terminal

		bin/hadoop fs -cat /user/root/data/output-top100/*

	โดยได้ผลลัพท์ดังนี้	 (อยู่ในรูปแบบ อันดับ, ความถี่, และคำ)

		1	7558	the
		2	4294	to
		3	4053	and
		4	3419	of
		5	3314	he
		6	3283	a
		7	2617	harry
		8	2449	said
		9	2396	was
		10	2249	his
		11	2239	you
		12	2134	i
		13	1978	that
		14	1923	in
		15	1902	it
		16	1658	had
		17	1302	at
		18	1241	as
		19	1137	not
		20	1104	but
		21	1071	with
		22	1032	him
		23	986	for
		24	941	on
		25	876	dumbledore
		26	850	her
		27	805	have
		28	799	ron
		29	788	she
		30	764	be
		31	685	what
		32	662	they
		33	651	hermione
		34	645	all
		35	628	out
		36	598	this
		37	582	were
		38	570	there
		39	560	up	from
		40	552	so
		41	550	been
		42	540	is
		43	523	them
		44	521	into
		45	518	who
		46	515	me
		47	484	no
		48	475	could
		49	453	would
		50	451	did
		51	448	an
		52	446	we
		53	435	now
		54	425	do
		55	421	back
		56	401	one
		57	400	then
		58	391	when
		59	388	by
		60	383	well	your
		61	380	just
		62	379	about
		63	377	over
		64	374	if
		65	367	know
		66	352	like
		67	344	or
		68	343	slughorn
		69	339	snape
		70	335	think	looked
		71	333	are
		72	329	very
		73	326	malfoy	more	don't
		74	317	see
		75	311	time
		76	306	their
		77	305	though
		78	297	down
		79	294	my
		80	289	around
		81	284	again
		82	279	got
		83	277	professor
		84	275	how
		85	268	still
		86	250	room
		87	249	looking	thought
		88	245	before
		89	244	which	will	off
		90	243	than
		91	239	look
		92	238	once
		93	236	right
		94	231	yes	can
		95	230	it's	little
		96	225	asked
		97	221	face
		98	218	ginny
		99	211	get
		100 210 hand
		