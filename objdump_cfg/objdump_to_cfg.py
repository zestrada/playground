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

import re
import sys
import subprocess
import string

#Build a CFG for a function based on objdump -d
#usage: objdump_to_cfg.py "objdump -d output" function_name

#jumps from
#http://blog.fairchild.dk/2013/06/automagical-asm-control-flow-arrow-annotation/
jumps = { #define jumps, synomyms on same line
'ja':'if above', 'jnbe':'if not below or equal',
'jae':'if above or equal','jnb':'if not below','jnc':'if not carry',
'jb':'if below', 'jnae':'if not above or equal', 'jc':'if carry',
'jbe':'if below or equal', 'jna':'if not above',
'jcxz':'if cx register is 0', 'jecxz':'if cx register is 0',
'je':'if equal', 'jz':'if zero',
'jg':'if greater', 'jnle':'if not less or equal',
'jge':'if greater or equal',
'jl':'if less', 'jnge':'if not greater or equal',
'jle':'if less or equal', 'jnl':'if not less',
'jmp':'unconditional',
'jne':'if not equal', 'jnz':'if not zero',
'jng':'if not greater',
'jno':'if not overflow',
'jnp':'if not parity', 'jpo':'if parity odd',
'jns':'if not sign',
'jo':'if overflow',
'jp':'if parity', 'jpe':'if parity even',
'js':'if sign',
'jmpq': 'unconditional qword'}

calls = {'call': 'call', 'callq':'call qword'} 
rets = {'ret':'return', 'retq':'return qword'}

dump_file = sys.argv[1]
root_name = sys.argv[2] #The function that will be the root of our CFG

#below regexes based on those from Lok
symbol_re = re.compile("^([a-fA-F0-9]+) <([\.\w]+)>:\s*$") 
symbol_plt_re = re.compile("^([a-fA-F0-9]+) <([@\w]+)>:\s*$")

#TODO: handle conditionals
print "#address;[target1, target2, ...]" #our output format

#CFG: key is source address, values are all targets
#     note that source=0 means root and source=-1 means we came from an indirect
CFG={}

root=0 #The root of our CFG

#Store the objdump in memory, list of tuples (address, asm)
#Went with this over a dict since we should be iterating more than searching
#so having it sorted by address just makes sense
objdump=[]
indirect_count=0

def main():
  global root
  with open(dump_file) as f:
    for line in f:
      #First find out function of interest
      m=symbol_re.match(line)
      if(m):
        if(m.group(2) == root_name):
          print(m.group(1), m.group(2))
          root=int(m.group(1),16)

      #Example tab-delimited output:
      #ADDRESS    INSTRUCTION           ASCII
      #c1000000:  8b 0d 80 16 5d 01     mov    0x15d1680,%ecx
      fields = string.split(line.rstrip(),'\t')
      
      #Symbols have 2 fields, but their actual first instruction will have 3
      if(len(fields)<3):
        continue
      objdump.append((int(fields[0].replace(":",""),16), fields[2]))

  if(root==0):
    print "Could not find root function for CFG: %s" % root_name

  #Recursively process BBs until we get a return to 0
  iterate_bb(0, root, [0])
  print_CFG()
  print("Indirect calls/jumps: %d"%indirect_count)

####END MAIN BEGIN FUNCTION DEFS#####
def print_CFG():
  for(key, value) in CFG.iteritems():
    print("0x%x: %s"%(key, string.join('0x%x' % t for t in value)))

def get_objdump_index(address):
  item = 0
  first = 0
  last = len(objdump)-1

  while first<=last:
    mid = (first+last)/2
    item = objdump[mid][0]
    if(item==address):
      return mid
    else:
      if(address < item):
        last = mid-1
      else:
        first = mid+1
  print("couldn't find address: %s"%address) 
  print("couldn't find address: 0x%x"%int(address,16)) 
  print("Last searched was: 0x%x"%item)
  raise ValueError

def add_cfg_edge(source,dest):
  global CFG
  if(source not in CFG):
    CFG[source]=[]
  CFG[source].append(dest)

def print_instr(instr):
    print("0x%x: %s"%(objdump[instr][0],objdump[instr][1]))

def iterate_bb(source, blockaddr, callstack):
  global indirect_count
  print("src: 0x%x, block: 0x%x, stack: %s"%(source,blockaddr,
        string.join('0x%x' % s for s in callstack)))
  #Stop conditions: we return from root or an indirect (somehow)
  if(blockaddr==0 or blockaddr==-1):
    return
  add_cfg_edge(source, blockaddr)
  #Now, step through until we hit a jump, call, or ret
  for i in range(get_objdump_index(blockaddr),len(objdump)):
    target_hex=0
    split = string.split(objdump[i][1])
    instr=split[0]
    if(len(split)>=2):
      target = split[1]
      try:
        target_hex = int(target,16)	
      except:
        #already an int or an indirect (which won't be used)
        target_hex = target

    #Look for jumps
    if(instr in jumps):
      if '*' in target:
        #Count it, abandon all hope
        indirect_count+=1
        return
      if(instr == "jmp" or instr == "jmpq"):
        #unconditional
        return iterate_bb(blockaddr, target_hex, callstack[:])
      else:
        #Jump taken
        iterate_bb(blockaddr, target_hex, callstack[:])
        #Jump not taken
        iterate_bb(blockaddr, objdump[i+1][0], callstack[:])
        return    

    #Look for calls 
    if(instr in calls):
      #Indirect or in PLT, just skip over it as if we returned
      if '*' in target or 'plt' in split[2]:
        indirect_count+=1
        return iterate_bb(-1, objdump[i+1][0], callstack[:])
      else: #for readability
        #Tried appending within a slice, but it was unhappy
        newstack=callstack[:]
        newstack.append(objdump[i+1][0])
        return iterate_bb(blockaddr, target_hex, newstack)

    if(instr in rets):
      return iterate_bb(blockaddr, callstack[-1], callstack[:-1])

main()
