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
#I_dsat = Z*Co(V_g-V_t)*v_sat

#Based on this model for drain current:
#https://ecee.colorado.edu/~bart/book/ex007.htm
#Need C_ox = epsilon/t_ox
#Need C_g = C_ox*W*L

#How to get R for charging the gate? Maybe we can just get some fudge-factor tau

#Assuming 1.4tau for switching speed based on this super reliable source:
#https://electronics.stackexchange.com/questions/20510/determine-mosfet-switching-speed

#TODO: how many transistors typically in a datapath? fanout, etc...
