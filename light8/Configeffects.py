from random import randrange
from time import time
from __future__ import generators,division
from Subs import *
from Cue import *

def strobe(params, slideradjuster):
    patterns = {
        'blue' : fulls((23,27,31,35,'b0 4 b','b2 3 b')),
        'cyc' : {42:FL,43:FL},
        'scp all' : fulls((13,16,18,19,39)),
        '1-5' : fulls(range(1, 6)),
    }
    params.add_param('offtime',SliderParam(range=(0.1,0.3), res=0.001,
                                           initial=0.11, length=100))
    params.add_param('ontime',SliderParam(range=(0.0,0.8), res=0.001, 
                                          length=100))
    params.add_param('pattern',ListParam(patterns.keys()))
    params.add_param('current',LabelParam('none'))
    params.add_param('count',SliderParam(range=(0, 10), res=1, initial=0))
    lastchanged = time()
    state = 0
    blinkcounter = 0
    my_pattern = None

    while 1:
        if params['count'] and blinkcounter > params['count']:
            blinkcounter = 0
            slideradjuster.set(0)

        if params['pattern'] != None:
            params['current'] = params['pattern']
            my_pattern = params['pattern']

        if state == 0:
            delay = params['offtime']
        else:
            delay = params['ontime']
            
        if time() > (lastchanged + delay):
            # ready for change
            state = not state
            lastchanged = time()
            blinkcounter += 0.5

        try: # protect against keyerrors (and possibly everything else)
            if state:
                yield patterns[my_pattern]
            else:
                yield scaledict(patterns[my_pattern], .1)
        except:
            yield {}

def chase(params, slideradjuster):
    patterns = {
        'all': ( fulls(('b01','b21')),
                 fulls(('b02','b22')),
                 fulls(('b03','b23')),
                 fulls(('b04','b24')),
                 fulls(('b05','b25')),
                 fulls(('b06','b26')),
                 ),
        'red':( fulls(('b0 1 r','b2 2 r')),
                fulls(('b0 5 r','b2 6 r'))),
        'randcol':([fulls((x,)) for x
                    in ("b21 b23 b25 b03 b06 b24 b22 "+
                        "b24 b03 b23 b01 b04 b05 b22 "+
                        "b02 b02 b26 b21 b06 b25 b26 "+
                        "b01 b04 b05").split()]),
        'ctrpong':[fulls((x,)) for x in (
                   "b11 b12 b13 b14 b15 b16 b15 b14 b13 b12".split())],
        'l-r': ( fulls(('b01','b11','b21')),
                 fulls(('b02','b12','b22')),
                 fulls(('b03','b13','b23')),
                 fulls(('b04','b14','b24')),
                 fulls(('b05','b15','b25')),
                 fulls(('b06','b16','b26'))),
        'flutter':(
        fulls(('main 6','b15')),
        fulls(('main 1','b12')),
        fulls(('main 2','b11')),
        fulls(('b12',   'main 3')),
        fulls(('b15',   'main 9')),
        fulls(('b16',   'main 4')),
        fulls(('main 4','b13')),
        fulls(('main 3','b11')),
        fulls(('main 8','b15')),
        fulls(('main 9','b12')),
        fulls(('b11',   'main 1')),
        fulls(('main 5','b15')),
        fulls(('b13',   'main 6')),
        fulls(('b14',   'main 2')),
        fulls(('main 7','b16')),
        ),
        'randstage':([fulls((x,)) for x
                    in ("""
b22 27 b04 26 b26 21 28 b25 23 b02 31 b05 32 34 b03 24 b01 25
b23 29 22 35 30 b24 33 36 """).split()]),

        }

    params.add_param('steptime',SliderParam(range=(.1,3),
                                            initial=.4,length=150))
    params.add_param('overlap',SliderParam(range=(0,8),initial=1.5))
    params.add_param('pattern',ListParam(options=patterns.keys(),
                                         initial='all'))
    params.add_param('current',LabelParam('none'))
    
    steps=()
    
    def fn(x):
        warm=.1
        # the _/\_ wave for each step. input 0..1, output 0..1
        if x<0 or x>1:
            return warm
        if x<.5:
            return warm+(1.0-warm)*(x*2)
        else:
            return warm+(1.0-warm)*(2-(x*2))

    def stepbrightness(stepnum,numsteps,overlap,pos):
        startpos = stepnum/numsteps
        p=( (pos-startpos)*(1.0+overlap) )%1.0
        ret=fn( p )
        #print "step %(stepnum)i/%(numsteps)i pos %(pos)f ,p=%(p)f is %(ret)f" % locals()
        return ret

    queued=[] # list of steps, each step is starttime,stepcue
    lastaddtime=time()-100
    currentpattern='all'
    steps=patterns[currentpattern]
    stepsiter=iter(())
    while 1:
        params['current'] = params['pattern']

        # changed pattern?
        if params['pattern']!=currentpattern and params['pattern'] in patterns:
            currentpattern=params['pattern']
            steps=patterns[currentpattern]
            stepsiter=iter(steps) # restart iterator

        # time to put a new step in the queue?
        if time()>lastaddtime+params['steptime']:
            lastaddtime=time()
            try:
                nextstep = stepsiter.next()
            except StopIteration:
                stepsiter=iter(steps)
                nextstep=stepsiter.next()
            queued.append( (time(),nextstep) )

        # loop over queue, putting still-active (scaled) steps in shiftedsteps
        keepers=[]
        shiftedsteps=[]
        for started,s in queued:
            steptime = time()-started
            finish = started+(1.0+params['overlap'])*params['steptime']
            pos = (time()-started)/(finish-started)
            if time()<finish:
                keepers.append((started,s))
                shiftedsteps.append( scaledict(s,fn(pos)) )

        if len(keepers)>30:
            print "too many steps in chase - dumping some"
            queued=keepers[:20]
        else:
            queued=keepers
            
            
#        pos=(time()%params['steptime'])/params['steptime'] # 0..1 animated variable
#        shiftedsteps=[]
#        for i,s in zip(range(0,len(steps)),steps):
#            shiftedsteps.append( scaledict(s, stepbrightness(i,len(steps),params['overlap'],pos)) )
        yield maxes(shiftedsteps)

    
def randomdimmer(params, slideradjuster):
    params.add_param('magic', CheckboxParam())
    params.add_param('cheese', TextParam())
    params.add_param('stuff', ListParam(('a', 'b', 'c')))

    curtime = time()
    dim = 1
    while 4:
        if time() - curtime > 1:
            dim = randrange(1, 64)
            curtime = time()
        yield {dim : 100, 20 : params.get_param_value('magic')}

