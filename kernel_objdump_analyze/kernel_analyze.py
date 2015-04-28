#!/usr/bin/env python
#
#Analyze a kernel using objdump, listing which functions call which instructions
#instructions of interest are given as a file of newline-delimited regexes
#(text version, at&t syntax).
#
#We take an unzipped kernel source and a System.map to bound functions.
#If you don't have the unzipped version, you can use scripts/extract-vmlinux
#from the kernel.org tree to get it.  Likewise, you can use scripts/mksysmap to
#generate that one.
#
#We call 'objdump -d' and store that in memory, so this takes ~100MB of RAM 
#when running.

import re
import sys
import subprocess
import string

KERNEL='/home/zak/arch_kernel/vmlinux'
SYSMAP='/home/zak/arch_kernel/System.map'
INSNS='./instructions'
OBJDUMP='objdump'

regexes=[]
sysmap={} #bonus points for unreable case sensitive variable names?

#First, load regexes
with open(INSNS, "r") as ins:
    for line in ins:
        regexes.append(re.compile(line.rstrip()))

if(len(regexes)<=0):
  sys.exit("No instruction regexes found in %s!"%INSNS)
print("Found %d regexes in %s"%(len(regexes),INSNS))

#Next, load system.map to bound functions
with open(SYSMAP, "r") as maps:
    for line in maps:
      line_array = string.split(line)
      #only want code, so text section - not perfect since we get some labels
      if(line_array[1].lower()=='t'):
        #Store as int since we'll minimize later. 
        #Use abs() to deal with 64bit addr map (hopefully - only tested on 32b)
        sysmap[abs(int(line_array[0],16))]=line_array[2]

#Now see what we get. Use a subprocess so we start processes while objdump is
#chugging along
proc = subprocess.Popen([OBJDUMP,'-d',KERNEL],stdout=subprocess.PIPE)

print "#FUNCTIONNAME;INSTRUCTION;ADDRESS" #our output format
while True:
  objout = proc.stdout.readline()
  if objout == '':
    break
  #Example tab-delimited output:
  #ADDRESS    INSTRUCTION           ASCII
  #c1000000:  8b 0d 80 16 5d 01     mov    0x15d1680,%ecx
  line = string.split(objout.rstrip(),'\t')
  if(len(line)>=3):
    for regex in regexes:
      if(regex.match(line[2])):
        addr = int(line[0].replace(':',''),16)
        #Find the closest symbol without going below 0 (previous symbol)
        #Not the fastest out there, but good enough
        offset, funcname  = min(sysmap.items(), 
                                key=lambda (x,_):addr-x if addr-x > 0 
                                else sys.maxint)
        print "%s;%s;%s"%(funcname, line[2], hex(addr))
