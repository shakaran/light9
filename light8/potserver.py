#!/usr/bin/python

import socket,time

from io import *

pots = SerialPots()
pots.golive()

laste=""
lastlevs=(0,0,0,0)
dirs=[0,0,0,0]
samples=nsends=noises=0
watch=0
while 1:
    if samples > 30:
        fps=1.0*samples/(time.time()-watch)
        watch=time.time()
        print "S"*nsends+"n"*noises+" "*(samples-nsends-noises),"%.1f Hz"%fps
        samples=nsends=noises=0
    samples+=1
    l=pots.getlevels()
    
    # no change at all?
    if l==lastlevs:
        time.sleep(.01)    
        continue

    report=0 # we only will report if a dimmer moves twice in the same direction
    for i in range(0,4):
        change = l[i]-lastlevs[i]
        if change!=0:
            thisdir = (change>0)-(change<0)
            if thisdir==dirs[i]:
                # a dimmer is moving in a constant direction
                report=1
            dirs[i]=thisdir

    if report==0:
        noises+=1
        continue
    
    lastlevs = l
    nsends+=1

    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.setblocking(1)
        ret=s.connect_ex(("10.1.0.32", socket.getservbyname('rlslider','tcp')))
#        print ret        
        s.send("%d %d %d %d\n" % l)
        s.close()
    except Exception,e:
        print str(e)
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ret==111:
            print time.ctime(),"waiting for server"
            time.sleep(3)
        else:
            print time.ctime(),e



