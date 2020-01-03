#!/usr/bin/env python

#Total bogus back-of-envlope model for calculating the maximum switching
#frequency of an individual transistor if temperature were a "solved problem"
#Maybe we're within a few orders of magnitude?

#Our model is the maximum current flowing from one transistor being used to
#switch another

#Use saturated velocity...
#I = n*q*A*v_d
#n = free charge density
#A = cross sectional area


#From 19.16 of (page 700) of Pierret
#I_dsat = W*Co(V_g-V_t)*v_sat
#Still a V_g dependence. I suppose we can always just assume that we will use
#default V_g for the processor

#Based on this model for drain current:
#https://ecee.colorado.edu/~bart/book/ex007.htm
#Need C_ox = epsilon/t_ox
#Need C_g = C_ox*W*L

#How to get R for charging the gate? Maybe we can just get some fudge-factor tau

#Assuming 1.4tau for switching speed based on this super reliable source:
#https://electronics.stackexchange.com/questions/20510/determine-mosfet-switching-speed

#TODO: how many transistors typically in a datapath? fanout, etc...
#Need to consider pipeline depth... that typically changes
#Really should just model as an ALU and assume an ideal pipeline
#Need to think of slowest reasonable functional unit to limit pipeline perf
#Maybe there's a standard instruction mix we can use and then assume very good
#circuits for those

#Considering quantum stuff: chapter 11 of QTATT
#Eq 11.2.3 for quantum transport with dephasing

#Maybe only include contact resistance? how to measure that?
#Considering poisson equation... 

#Can consider maximum conductance per level:
#25.8kOhm per channel
#Need to solve self-consistently Fig  1.4.5

#Page 24 of QTATT

#can't consider ballistic limit since actually a larger transistor would be
#faster - larger cross-sectional area
#but they would have a larger gate capacitor to charge...
#but the electrostatics get messy, lots of electrons close to each other
