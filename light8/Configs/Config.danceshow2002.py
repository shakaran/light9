from random import randrange
from time import time
from __future__ import generators,division
from Subs import *


patch = {
    'side l' : 45,
    'side r' : 46,
    'main 1' : 1,
    'main 2' : 2,
    'main 3' : 3,
    'main 4' : 4,
    'main 5' : 5,
    'main 6' : 6,
    'main 7' : 7,
    'main 8' : 8,
    'main 9' : 9,
    'main 10' : 10,
    'center sc' : 20,
    'sr sky' : 43,
    'blacklight' : 15,
    'house':68,
    ('b0 1 r' ,'b01'):54, # left bank over house
    ('b0 2 p' ,'b02'):53,
    ('b0 3 o' ,'b03'):52,
    ('b0 4 b' ,'b04'):51,
    ('b0 5 r' ,'b05'):50,
    ('b0 6 lb','b06'):49,
    ('b1 1'   ,'b11'):55, # mid bank
    ('b1 2'   ,'b12'):56,
    ('b1 3'   ,'b13'):57,
    ('b1 4'   ,'b14'):58,
    ('b1 5'   ,'b15'):59,
    ('b1 6'   ,'b16'):60,
    ('b2 1 lb','b21'):61, # right bank
    ('b2 2 r' ,'b22'):62,
    ('b2 3 b' ,'b23'):63,
    ('b2 4 o' ,'b24'):64,
    ('b2 5 p' ,'b25'):65,
    ('b2 6 r' ,'b26'):66,   
}

from util import maxes,scaledict
FL=100
def fulls(chans):
    # pass a list or multiple args
    return dict([(c,FL) for c in chans])
def levs(chans,levs):
    return dict([(c,v) for c,v in zip(chans,levs)])

def blacklight(params, slideradjuster):
    params.add_param('nd',CheckboxParam())
    while 1:
        yield {'blacklight':100*params['nd']}

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
    ('col oran', '#EEEE99'):fulls((21,25,29,33)),
    ('col red', 'red'):fulls((24,28,32,36)),
    ('col red big', 'red'):fulls((24,28,32,36,
                         'b0 1 r','b0 5 r','b2 2 r','b2 6 r')),
    ('col blue', 'blue'):fulls((23,27,31,35,'b0 4 b','b2 3 b')),
    ('col gree', 'green'):fulls((22,26,30,34)),
    'sidepost':fulls((45,46)),
    'edges':fulls((55,60,49,54,61,66)),
    'bank1ctr':fulls(('b12','b13','b14','b15')),
    ('blacklight', 'purple'):blacklight,
    'over pit ctr' : fulls((6,)),
    ('strobe', 'grey'):strobe,
    
#    'midstage' : dict([(r, 100) for r in range(11, 21)]),
#    'backstage' : dict([(r, 100) for r in range(21, 31)]),
#    'frontchase' : mr_effect,
    'chase' : chase,
    'chase2' : chase,
#    'random' : randomdimmer,
}
subs["*10"] = { "14" : 46.000000,
                "18" : 46.000000,
                "22" : 88.000000,
                "23" : 95.000000,
                "24" : 19.000000,
                "26" : 88.000000,
                "27" : 95.000000, "28" : 19.000000,
                "30" : 88.000000, "31" : 95.000000,
                "32" : 19.000000, "34" : 88.000000,
                "35" : 95.000000, "36" : 19.000000,
                "b0 5 r" : 7.000000, "b0 4 b" : 95.000000,
                "b0 1 r" : 7.000000, "b2 2 r" : 7.000000,
                "b2 3 b" : 95.000000, "b2 6 r" : 7.000000, }
subs["*13"] = { "main 1" : 51.0, "main 2" : 51.0, "main 3" : 51.0,
                "main 4" : 51.0, "main 5" : 51.0, "main 6" : 51.0,
                "main 7" : 51.0, "main 8" : 51.0, "main 9" : 51.0,
                "main 10" : 51.0, "11" : 51.0, "12" : 51.0,
                "blacklight" : 0.0, "21" : 56.0, "22" : 50.0,
                "24" : 51.0, "25" : 56.0, "26" : 50.0, "28" : 51.0,
                "29" : 56.0, "30" : 50.0, "32" : 51.0, "33" : 56.0,
                "34" : 50.0, "36" : 51.0, "b0 5 r" : 51.0,
                "b0 1 r" : 51.0, "b2 2 r" : 51.0, "b2 6 r" : 51.0, }
subs["*16"] = { "main 1" : 54, "main 4" : 49, "main 5" : 41, "main 6" : 43,
    "main 7" : 46, "main 8" : 29, "main 9" : 50, "main 10" : 41,
    "11" : 32, "13" : 77, "16" : 77, "18" : 77, "19" : 77, "39" : 77,
    "42" : 30, "sr sky" : 30,}
subs["*3"] = { "main 1" : 47, "main 2" : 47, "main 3" : 47, "main 4" : 47,
    "main 5" : 47, "main 6" : 47, "main 7" : 47, "main 8" : 47, "main 9" : 47,
    "main 10" : 47, "11" : 47, "12" : 47, "blacklight" : 0, "21" : 67,
    "22" : 69, "23" : 69, "24" : 78, "25" : 67, "26" : 69, "27" : 69,
    "28" : 78, "29" : 67, "30" : 69, "31" : 69, "32" : 78, "33" : 67,
    "34" : 69, "35" : 69, "36" : 78, "b0 4 b" : 69, "b1 2" : 61,
    "b1 3" : 61, "b1 4" : 61, "b1 5" : 61, "b2 3 b" : 69,}
subs["*12"] = { "main 1" : 25, "main 4" : 23, "main 5" : 19, "main 6" : 20,
    "main 7" : 22, "main 8" : 14, "main 9" : 23, "main 10" : 19,
    "11" : 15, "13" : 36, "16" : 36, "18" : 36, "19" : 36, "22" : 65,
    "23" : 100, "24" : 23, "26" : 65, "27" : 100, "28" : 23, "30" : 65,
    "31" : 100, "32" : 23, "34" : 65, "35" : 100, "36" : 23, "39" : 36,
    "b0 4 b" : 100, "b1 2" : 62, "b1 3" : 62, "b1 4" : 62, "b1 5" : 62,
    "b2 3 b" : 100,}
subs["*curtain"] = { "main 4" : 44, "main 5" : 37, "main 6" : 86,
    "main 7" : 42, "main 8" : 32, "main 9" : 45, "42" : 41, "sr sky" : 41,
    "b0 6 lb" : 27, "b0 1 r" : 27, "b1 1" : 27, "b1 2" : 100, "b1 3" : 100,
    "b1 4" : 100, "b1 5" : 100, "b1 6" : 27, "b2 1 lb" : 27, "b2 6 r" : 27,
                     
                     }
subs["ba outrs"] = fulls("b01 b02 b03 b04 b05 b06 b21 b22 b23 b24 b25 b26".split())
subs["ba some"] = {'b02':40,'b03':FL,'b04':FL,'b05':40,
                   'b22':40,'b23':FL,'b24':FL,'b25':40,}
subs['*curtain'].update(subs['ba some'])

subs["*2"] = { "main 1" : 77, "main 4" : 70, "main 5" : 59, "main 6" : 61,
    "main 7" : 66, "main 8" : 42, "main 9" : 71, "main 10" : 59,
    "11" : 45, "24" : 77, "28" : 77, "32" : 77, "36" : 77, "b0 5 r" : 77,
    "b0 1 r" : 77, "b2 2 r" : 77, "b2 6 r" : 77,}
subs["*6"] = { "main 1" : 37, "main 4" : 33, "main 5" : 28, "main 6" : 29,
    "main 7" : 32, "main 8" : 20, "main 9" : 34, "main 10" : 28,
    "11" : 22, "13" : 37, "blacklight" : 0, "16" : 37, "18" : 37,
    "19" : 37, "21" : 82, "22" : 82, "23" : 82, "24" : 82, "25" : 82,
    "26" : 82, "27" : 82, "28" : 82, "29" : 82, "30" : 82, "31" : 82,
    "32" : 82, "33" : 82, "34" : 82, "35" : 82, "36" : 82, "39" : 37,
    "b0 5 r" : 82, "b0 4 b" : 82, "b0 1 r" : 82, "b2 2 r" : 82, "b2 3 b" : 82,
    "b2 6 r" : 82,}
subs["*8"] = { "13" : 60, "16" : 60, "18" : 60, "19" : 60, "22" : 14,
    "23" : 100, "26" : 14, "27" : 100, "30" : 14, "31" : 100, "34" : 14,
    "35" : 100, "39" : 60, "b0 6 lb" : 14, "b0 4 b" : 100, "b0 1 r" : 14,
    "b1 1" : 14, "b1 2" : 70, "b1 3" : 70, "b1 4" : 70, "b1 5" : 70,
    "b1 6" : 14, "b2 1 lb" : 14, "b2 3 b" : 100, "b2 6 r" : 14,}
subs["*5"] = { "main 1" : 81, "main 4" : 74, "main 5" : 62, "main 6" : 64,
    "main 7" : 70, "main 8" : 44, "main 9" : 75, "main 10" : 62,
    "11" : 48, "21" : 29, "24" : 29, "25" : 29, "28" : 29, "29" : 29,
    "32" : 29, "33" : 29, "36" : 29, "42" : 37, "sr sky" : 37, "b0 5 r" : 29,
    "b0 4 b" : 72, "b0 3 o" : 72, "b0 2 p" : 29, "b2 2 r" : 29, "b2 3 b" : 72,
    "b2 4 o" : 72, "b2 5 p" : 29,}
