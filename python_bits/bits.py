#!/bin/sh
#Shortcuts for helping with bit manipulations interactively in python
#(aka I got sick of typing "XXXYYYYYZZ to MiB" in google)

#This is a line of shell script that lets us execute as interactive python
"exec" "/usr/bin/env" "python" "-i" "$0" "$@"

import math
from ctypes import c_ulonglong

#Ripped from the kernel
PAGE_SHIFT=12
PAGE_SIZE=(1 << PAGE_SHIFT)
PAGE_MASK=((~(PAGE_SIZE-1)))

#The below functions assume bytes
def toKB(x):
  return x/(2**10)

def toMB(x):
  return x/(2**20)

def toGB(x):
  return x/(2**30)

def KB(x)
  return x*(2**10)

def MB(x)
  return x*(2**20)

def GB(x)
  return x*(2**30)

def bits(x):
  return int(math.ceil(math.log(x,2)))

#One day I'll grow up and use ipython. Until then, there's this
def h(x):
  print hex(x)
