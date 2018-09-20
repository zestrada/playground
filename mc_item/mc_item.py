#!/usr/bin/python
import random
#VT2 MC simulation - how many boxes to get to 300?

####Configuration####
START=113 #Level to start at
MAX=300 #Level you are going for
RANGE=[-10,10] #Range of uniform random numbers
ITERS=1000 #How many iterations of the simulation factor into the average

####Variables####
AVG_PULLS=0.0 #The final result

#We will repeat the simulation for N ITERS (TODO: implement convergence test)
for i in range(ITERS):
    level=START
    count=0
    while level<MAX:
        pull=random.randint(RANGE[0],RANGE[1])
        if pull>0:
            level+=pull
        count+=1
        print(count,level)
    print("---------")
    AVG_PULLS+=float(count)/float(ITERS)
print("Average number of boxes: %g",AVG_PULLS)
