from random import randrange
from time import time
from __future__ import generators,division
from Subs import *
from Cue import *

f1 = Fade('red', 0, 2, 100)
f2 = Fade('green', 1, 3, 50)
f3 = Fade('blue', 0, 4, 0)
f4 = Fade('clear', 0, 8, 75) 
c1 = Cue("Color shift", 0, 10, None, f1, f2, f3, f4)

cues = [c1]

patch = {
    
    'side l' : 45, # posts
    'side r' : 46,
    
    ('patio1','main 1',) : 1,
    ('main 2',) : 2,
    ('main 3',) : 3,
    ('main 4',) : 4,
    ('main 5',) : 5,
    ('god','main 6') : 6,
    ('main 7',) : 7,
    ('main 8',) : 8,
    ('main 9',) : 9,
    ('main 10',) : 10,
    ('main 11',):11,
    ('patio2','main 12',):12,

    'cycleft' : 43,
    'cycright' : 44, # ? might be a different circuit
    
    'house':68,
    ('desk1' ,'b11'):54, # left bank over house
    ('marry1' ,'b12'):53,
    ('b13',):52,
    ('hotbox1' ,'b14'):51,
    ('edge' ,'b15'):50,
    ('phone','b16'):49,
    ('cuba1'   ,'b21'):55, # mid bank
    ('b22',):56,
    ('b23',):57,
    ('b24'):58,
    ('b25'):59,
    ('desk2'   ,'b26'):60,
    ('rock','b31'):61, # right bank
    ('b32',):62,
    ('hotbox2' ,'b33'):63,
    ('b34',):64,
    ('marry2' ,'b35'):65,
    ('cuba2' ,'b36'):66,
    'oran1':21,    'oran2':25,    'oran3':29,    'oran4':33,
    'gree1':22,    'gree2':26,    'gree3':30,    'gree4':34,
    'blue1':23,    'blue2':27,    'blue3':31,    'blue4':35,
    'red1' :24,    'red2' :28,    'red3' :32,    'red4' :36,
}

from util import maxes,scaledict
FL=100
def fulls(chans):
    # pass a list or multiple args
    return dict([(c,FL) for c in chans])
def levs(chans,levs):
    return dict([(c,v) for c,v in zip(chans,levs)])

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

subs = {
    'over pit sm' : levs(range(1, 13),(100,0,0,91,77,79,86,55,92,77,59,0)),
    'over pit lg' : fulls(range(1, 13)),
    ('house', 'black') : { 68:100 },
    ('cyc', 'lightBlue'):{42:FL,43:FL},
    ('scp hot ctr', 'yellow'):{18:FL},
    ('scp more', '#AAAA00'):{18:FL,14:FL},
    ('scp all', '#AAAA00'):fulls((13,16,18,19,39)),
    ('col oran', '#EEEE99'):fulls('oran1 oran2 oran3 oran4'.split()),
    ('col red', 'red'):fulls('red1 red2 red3 red4'.split()),
    ('col blue', 'blue'):fulls('blue1 blue2 blue3 blue4'.split()),
    ('col gree', 'green'):fulls('gree1 gree2 gree3 gree4'.split()),
    'sidepost':fulls((45,46)),
    'edges':fulls((55,60,49,54,61,66)),
    'bank1ctr':fulls(('b22','b23','b24','b25')),
    'god' : fulls((6,)),
    ('strobe', 'grey'):strobe,
    
#    'midstage' : dict([(r, 100) for r in range(11, 21)]),
#    'backstage' : dict([(r, 100) for r in range(21, 31)]),
#    'frontchase' : mr_effect,
    'chase' : chase,
    # 'chase2' : chase,
#    'random' : randomdimmer,
}

subs["ba outrs"] = fulls("b11 b12 b13 b14 b15 b16 b31 b32 b33 b34 b35 b36".split())
subs["ba some"] = {'b12':40,'b13':FL,'b14':FL,'b15':40,
                   'b32':40,'b33':FL,'b34':FL,'b35':40,}
subs['*curtain'] = subs['ba some'].copy()
