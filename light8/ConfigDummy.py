from random import randrange
from time import time
from __future__ import generators,division
from Subs import *
from Cue import *

f1 = Fade('col blue', 0, 2, 1)
f2 = Fade('col gree', 1, 3, .50)
f3 = Fade('col oran', 0, 4, 0)
f4 = Fade('col red', 0, 8, .75) 

g1 = Fade('col blue', 1, 2, .20)
g2 = Fade('col gree', 0, 4, .10)
g3 = Fade('cyc', 1, 5, .20)
g4 = Fade('god', 0, 4, .15) 

r1 = Fade('col blue', 0, 2, 0)
r2 = Fade('col gree', 1, 3, .10)
r3 = Fade('col oran', 0, 4, .6)
r4 = Fade('col red', 0, 8, .15) 
r5 = Fade('cyc', 1, 5, .90)
r6 = Fade('god', 0, 8, .75) 

cues = [
    Cue("This", 0, 10, f1, f2, f3, f4),
    Cue("That", 0, 5, g1, g2, g3, g4),
    Cue("The other", 1, 7, f1, g2, g3, f4),
    Cue("Reset", 1, 9, r1, r2, r3, r4, r5, r6),
]

patch = {
    
    ('side l','sidepost1') : 45, # posts
    ('side r','sidepost2') : 46,
    
    'sidefill1' : 13,
    'sidefill2' : 14,

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
    'hotback':19,

    'cycleft' : 43,
    'cycright' : 42,
    
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
    'upfill1' : 40,
    'upfill2' : 38,
    'upfill3' : 37,
    'upfill4' : 39,
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
    ('house', 'black') : { 68:100 },
    ('col oran', '#EEEE99'):fulls('oran1 oran2 oran3 oran4'.split()),
    ('col red', 'red'):fulls('red1 red2 red3 red4'.split()),
    ('col blue', 'blue'):fulls('blue1 blue2 blue3 blue4'.split()),
    ('col gree', 'green'):fulls('gree1 gree2 gree3 gree4'.split()),
    'sidepost':fulls((45,46)),
    'bank1ctr':fulls(('b22','b23','b24','b25')),
    'god' : fulls((6,)),
#    ('strobe', 'grey'):strobe,
#    'chase' : chase,
#    'chase2' : chase,
    'cyc' : fulls(('cycleft','cycright')),
    'sidefill' : fulls(('sidefill1','sidefill2')),
    'patio left' : { 'patio1':FL },
    'patio right' : { 'patio2':FL },
    'upfill sides' : fulls(('upfill1','upfill4')),
    '*broadway open':{},
    '*int mission':{},
    '*phone booth':{},
    '*off broadway':{},
    '*cuba left':{},
    '*cuba right':{},
    '*cuba dance':{},
    '*cuba sky':{},
    '*cuba love':{},
    '*ext mission':{},
    '*hotbox dance':{},
    '*hotbox table':{},
    '*sewer':{},
    '*marry':{},
    
    
}

subs["*marry"] = { "hotbox1" : 100,}
subs["*phone booth"] = { "phone" : 100,}
subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
    "main 11" : 100, "main 10" : 100, "b34" : 100, "b25" : 100, "b24" : 100,
    "b22" : 100, "desk2" : 78, "phone" : 46, "upfill3" : 69, "upfill2" : 100,
    "main 3" : 68, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "edge" : 46,
    "sidepost1" : 100, "sidepost2" : 100, "marry2" : 100, "marry1" : 100,}
subs["*int mission"] = { "sidefill1" : 100, "main 4" : 100, "main 9" : 100,
    "main 8" : 100, "b24" : 100, "b23" : 100, "desk1" : 100, "desk2" : 100,
    "b22" : 100, "rock" : 100, "marry1" : 100, "cuba1" : 25, "cuba2" : 51,
    "main 10" : 100,}
subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
    "main 11" : 100, "main 10" : 100, "b34" : 100, "b25" : 100, "b24" : 100,
    "b22" : 100, "desk2" : 78, "phone" : 46, "hotbox1" : 100, "upfill3" : 69,
    "upfill2" : 100, "main 3" : 68, "main 2" : 100, "main 5" : 100,
    "main 4" : 100, "main 7" : 100, "hotbox2" : 100, "main 9" : 100,
    "main 8" : 100, "edge" : 46, "sidepost1" : 100, "sidepost2" : 100,
    "marry2" : 100, "marry1" : 100,}
subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 69, "upfill2" : 100, "upfill1" : 56,
    "side l" : 100, "b25" : 100, "cycleft" : 41, "b22" : 100, "desk2" : 78,
    "phone" : 46, "hotbox1" : 100, "upfill4" : 56, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 68, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 100,
    "main 9" : 100, "main 8" : 100, "b34" : 100, "edge" : 46, "god" : 100,
    "marry2" : 100, "marry1" : 100,}
subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 69, "upfill2" : 100, "upfill1" : 56,
    "b34" : 100, "b25" : 100, "side l" : 100, "b22" : 100, "desk2" : 78,
    "phone" : 80, "hotbox1" : 100, "upfill4" : 56, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 100, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 100,
    "main 9" : 100, "main 8" : 100, "cycleft" : 41, "edge" : 80,
    "god" : 100, "marry2" : 100, "marry1" : 100,}
subs["*int mission"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 100, "b34" : 0, "b25" : 0, "b24" : 100,
    "b23" : 100, "desk1" : 53, "desk2" : 100, "b22" : 100, "hotbox2" : 85,
    "hotbox1" : 25, "b32" : 62, "upfill3" : 37, "upfill2" : 66, "main 3" : 0,
    "main 5" : 70, "main 4" : 100, "main 7" : 100, "main 9" : 100,
    "main 8" : 100, "rock" : 52, "marry2" : 100, "marry1" : 61, "cuba1" : 0,
    "cuba2" : 78,}
subs["*int mission"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 100, "b34" : 0, "b25" : 0, "b24" : 100,
    "b23" : 100, "desk1" : 53, "desk2" : 100, "b22" : 100, "hotbox2" : 85,
    "hotbox1" : 25, "cycright" : 66, "b32" : 62, "upfill3" : 37,
    "upfill2" : 66, "main 3" : 57, "main 2" : 0, "main 5" : 70, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "rock" : 52,
    "marry2" : 100, "marry1" : 61, "cuba1" : 0, "cuba2" : 78,}
subs["*hotbox dance"] = { "red3" : 100, "sidefill2" : 46, "red1" : 100,
    "cycright" : 19, "upfill3" : 32, "upfill2" : 46, "upfill1" : 26,
    "red2" : 100, "side l" : 46, "b25" : 46, "cycleft" : 19, "sidefill1" : 46,
    "desk2" : 36, "b22" : 46, "phone" : 37, "hotbox1" : 46, "upfill4" : 26,
    "b24" : 46, "side r" : 46, "main 11" : 46, "main 10" : 46, "main 3" : 46,
    "main 2" : 46, "main 5" : 46, "main 4" : 46, "main 7" : 46, "hotbox2" : 46,
    "main 9" : 46, "main 8" : 46, "red4" : 100, "b34" : 46, "edge" : 37,
    "god" : 100, "marry2" : 46, "marry1" : 46,}
subs["*hotbox dance"] = { "cycright" : 19, "upfill3" : 32, "upfill2" : 46,
    "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46, "b23" : 0,
    "desk1" : 0, "desk2" : 0, "upfill4" : 26, "side r" : 46, "main 11" : 46,
    "main 10" : 46, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0, "b13" : 0,
    "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0, "red4" : 100,
    "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0, "phone" : 0,
    "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 46,
    "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
    "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
subs["*hotbox dance"] = { "cycright" : 19, "upfill3" : 32, "upfill2" : 46,
    "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46, "b23" : 0,
    "desk1" : 0, "desk2" : 24, "upfill4" : 26, "side r" : 46, "main 11" : 46,
    "main 10" : 100, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0, "b13" : 0,
    "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0, "red4" : 100,
    "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0, "phone" : 0,
    "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 100,
    "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
    "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
subs["*hotbox table"] = { "sidefill2" : 0, "main 3" : 80, "main 2" : 62,
    "main 11" : 0, "main 4" : 29, "main 7" : 10, "main 9" : 64, "main 8" : 10,
    "b25" : 0, "b22" : 100, "phone" : 0, "edge" : 0, "b13" : 0, "marry2" : 0,
    "main 5" : 34, "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
subs["*hotbox table"] = { "sidefill2" : 0, "main 11" : 0, "b25" : 0,
    "b22" : 100, "desk2" : 58, "phone" : 0, "main 3" : 80, "main 2" : 62,
    "main 5" : 34, "main 4" : 100, "main 7" : 10, "hotbox2" : 46,
    "main 9" : 64, "main 8" : 10, "edge" : 0, "b13" : 0, "rock" : 22,
    "marry2" : 0, "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
subs["*hotbox small table"] = { "red3" : 100, "red2" : 100, "main 3" : 80,
    "main 2" : 62, "main 5" : 34, "main 4" : 100, "main 7" : 10,
    "red4" : 100, "main 9" : 64, "main 8" : 10, "rock" : 22, "red1" : 100,
    "desk2" : 58, "b22" : 100, "hotbox2" : 46, "upfill4" : 62, "god" : 100,
    "upfill1" : 62, "cuba1" : 22,}
subs["*hotbox small table"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 62, "main 11" : 0, "main 10" : 0, "upfill1" : 62,
    "red4" : 100, "b25" : 5, "b22" : 100, "desk2" : 58, "desk1" : 52,
    "hotbox2" : 0, "sidefill2" : 0, "main 3" : 47, "main 2" : 0,
    "main 5" : 0, "main 4" : 0, "main 7" : 0, "phone" : 0, "main 9" : 11,
    "main 8" : 0, "god" : 100, "edge" : 0, "rock" : 0, "marry2" : 0,
    "marry1" : 0, "hotback" : 0, "cuba1" : 0, "cuba2" : 0,}
subs["*ext mission"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 69, "upfill2" : 100, "upfill1" : 56,
    "side l" : 100, "b25" : 100, "cycleft" : 41, "b22" : 100, "desk2" : 78,
    "phone" : 80, "hotbox1" : 100, "upfill4" : 56, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 100, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 100,
    "main 9" : 100, "main 8" : 100, "b34" : 100, "edge" : 80, "god" : 100,
    "marry2" : 100, "marry1" : 100,}
subs["*ext mission"] = { "sidefill2" : 100, "sidefill1" : 59,
    "cycright" : 53, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "b34" : 100, "b25" : 100, "side l" : 100, "b23" : 100, "b22" : 49,
    "b32" : 80, "phone" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100,
    "desk2" : 78, "main 11" : 100, "main 10" : 100, "main 3" : 0,
    "main 2" : 100, "main 5" : 100, "main 4" : 0, "main 7" : 100,
    "hotbox2" : 100, "main 9" : 100, "main 8" : 100, "god" : 100,
    "cycleft" : 0, "edge" : 0, "b13" : 0, "rock" : 60, "marry2" : 100,
    "marry1" : 0, "side r" : 100,}
subs["*broadway night 1-7"] = { "sidefill2" : 37, "sidefill1" : 37,
    "cycright" : 15, "upfill3" : 25, "upfill2" : 37, "upfill1" : 20,
    "side l" : 37, "b25" : 37, "cycleft" : 15, "b22" : 37, "desk2" : 28,
    "phone" : 29, "hotbox1" : 37, "upfill4" : 20, "b24" : 37, "side r" : 37,
    "main 11" : 37, "main 10" : 37, "main 3" : 37, "main 2" : 37,
    "main 5" : 37, "main 4" : 37, "main 7" : 37, "hotbox2" : 37,
    "main 9" : 37, "main 8" : 37, "b34" : 37, "edge" : 29, "god" : 100,
    "marry2" : 37, "marry1" : 37,}
subs["*broadway night 1-7"] = { "sidefill2" : 37, "sidefill1" : 37,
    "upfill3" : 11, "upfill2" : 23, "b34" : 37, "b25" : 37, "b24" : 94,
    "b23" : 100, "b22" : 61, "desk2" : 28, "hotbox2" : 37, "hotbox1" : 37,
    "blue1" : 93, "main 11" : 37, "blue3" : 93, "blue2" : 93, "blue4" : 93,
    "main 10" : 37, "main 3" : 25, "main 2" : 37, "main 5" : 37,
    "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37, "edge" : 12,
    "god" : 100, "marry2" : 37, "marry1" : 37,}
subs["*broadway night 1-7"] = { "sidefill2" : 37, "sidefill1" : 37,
    "upfill3" : 11, "upfill2" : 23, "b34" : 37, "b25" : 37, "b24" : 94,
    "b23" : 100, "b22" : 61, "desk2" : 0, "desk1" : 0, "hotbox2" : 37,
    "hotbox1" : 0, "blue1" : 93, "main 11" : 37, "blue3" : 93, "blue2" : 93,
    "blue4" : 93, "main 10" : 37, "main 3" : 25, "main 2" : 37, "main 5" : 37,
    "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37, "edge" : 12,
    "god" : 100, "marry2" : 37, "marry1" : 37,}
subs["*broadway night 1-7"] = { "sidefill2" : 37, "sidefill1" : 37,
    "upfill3" : 11, "upfill2" : 23, "b34" : 28, "b25" : 37, "b24" : 94,
    "b23" : 100, "b22" : 82, "desk2" : 0, "desk1" : 0, "hotbox2" : 11,
    "hotbox1" : 0, "blue1" : 93, "main 11" : 37, "blue3" : 93, "blue2" : 93,
    "blue4" : 93, "main 10" : 37, "main 3" : 25, "main 2" : 37, "main 5" : 37,
    "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37, "edge" : 12,
    "god" : 100, "marry2" : 0, "marry1" : 37,}
subs["*cuba right"] = { "main 3" : 31, "main 2" : 0, "main 10" : 100,
    "b34" : 100, "b22" : 31, "desk2" : 85, "desk1" : 39, "edge" : 31,
    "sidefill1" : 7, "cuba1" : 100, "cuba2" : 100,}
subs["*cuba dance"] = { "sidefill2" : 100, "sidefill1" : 100,
    "upfill4" : 100, "upfill3" : 81, "upfill2" : 100, "upfill1" : 100,
    "b34" : 100, "b25" : 100, "b24" : 100, "b23" : 100, "desk1" : 100,
    "desk2" : 100, "b22" : 100, "phone" : 100, "main 11" : 100, "main 10" : 100,
    "main 3" : 100, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "edge" : 100,
    "god" : 100, "marry2" : 100, "marry1" : 100, "hotback" : 100,
    "cuba1" : 100, "cuba2" : 100,}
subs["*cuba love"] = { "sidefill2" : 0, "sidefill1" : 0, "upfill4" : 61,
    "main 11" : 100, "main 10" : 100, "upfill1" : 61, "b25" : 100,
    "b24" : 100, "b23" : 100, "b22" : 100, "desk2" : 0, "desk1" : 0,
    "phone" : 0, "hotbox1" : 0, "upfill3" : 61, "upfill2" : 61, "main 3" : 0,
    "main 2" : 100, "main 5" : 100, "main 4" : 100, "main 7" : 100,
    "main 9" : 73, "main 8" : 100, "edge" : 0, "hotback" : 0, "marry2" : 0,
    "marry1" : 0, "cuba1" : 0, "cuba2" : 0,}
subs["*cuba love"] = { "sidefill2" : 0, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 28, "main 10" : 28, "upfill1" : 0, "b34" : 9, "b25" : 100,
    "b24" : 59, "b23" : 59, "b22" : 100, "desk2" : 0, "desk1" : 0,
    "phone" : 0, "hotbox1" : 0, "upfill3" : 43, "upfill2" : 43, "main 3" : 0,
    "main 2" : 100, "main 5" : 16, "main 4" : 16, "main 7" : 0, "main 9" : 73,
    "main 8" : 100, "edge" : 0, "marry2" : 9, "marry1" : 0, "hotback" : 0,
    "cuba1" : 0, "cuba2" : 0,}
subs["*cuba love"] = { "sidefill2" : 0, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 28, "main 10" : 28, "upfill1" : 0, "b34" : 9, "b25" : 100,
    "b24" : 59, "b23" : 59, "b22" : 100, "desk2" : 0, "desk1" : 0,
    "phone" : 0, "hotbox1" : 0, "upfill3" : 43, "upfill2" : 43, "main 3" : 0,
    "main 2" : 100, "main 5" : 16, "main 4" : 16, "main 7" : 0, "main 9" : 65,
    "main 8" : 74, "edge" : 0, "marry2" : 9, "marry1" : 0, "hotback" : 0,
    "cuba1" : 0, "cuba2" : 0,}
subs["*cuba love"] = { "sidefill2" : 0, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 28, "main 10" : 28, "upfill1" : 0, "b34" : 9, "b25" : 100,
    "b24" : 59, "b23" : 59, "b22" : 100, "desk2" : 16, "desk1" : 0,
    "phone" : 0, "hotbox1" : 0, "upfill3" : 43, "upfill2" : 43, "main 3" : 28,
    "main 2" : 100, "main 5" : 16, "main 4" : 16, "main 7" : 0, "main 9" : 65,
    "main 8" : 74, "edge" : 0, "marry2" : 9, "marry1" : 0, "hotback" : 0,
    "cuba1" : 0, "cuba2" : 0,}
subs["*ext mission night"] = { "sidefill2" : 39, "sidefill1" : 23,
    "cycright" : 20, "main 11" : 29, "main 10" : 29, "upfill1" : 8,
    "b34" : 39, "b25" : 39, "side l" : 39, "b23" : 39, "b22" : 19,
    "b32" : 31, "upfill4" : 8, "b24" : 39, "side r" : 39, "desk2" : 18,
    "main 2" : 39, "main 5" : 39, "main 9" : 39, "main 8" : 39, "god" : 100,
    "marry2" : 39,}
subs["*ext mission night"] = { "sidefill2" : 39, "sidefill1" : 23,
    "cycright" : 20, "main 11" : 29, "main 10" : 29, "upfill1" : 8,
    "b34" : 39, "b25" : 39, "side l" : 39, "b23" : 39, "b22" : 19,
    "b32" : 31, "upfill4" : 8, "b24" : 39, "side r" : 39, "desk2" : 18,
    "main 2" : 39, "main 5" : 39, "main 9" : 39, "main 8" : 39, "god" : 100,
    "marry2" : 39,}
subs["*ext mission night"] = { "cycright" : 6, "main 11" : 15,
    "main 10" : 15, "upfill1" : 0, "b25" : 25, "side l" : 39, "b23" : 25,
    "b22" : 5, "desk2" : 4, "upfill4" : 0, "side r" : 39, "upfill3" : 0,
    "upfill2" : 0, "patio1" : 0, "god" : 86, "edge" : 0, "b13" : 0,
    "sidepost2" : 0, "marry2" : 25, "marry1" : 0, "cuba1" : 5, "cuba2" : 0,
    "sidepost1" : 0, "sidefill2" : 25, "sidefill1" : 9, "b24" : 25,
    "b34" : 25, "cycleft" : 0, "b32" : 17, "desk1" : 0, "hotbox2" : 25,
    "hotbox1" : 0, "main 3" : 0, "main 2" : 25, "main 5" : 25, "main 4" : 25,
    "main 7" : 25, "phone" : 0, "main 9" : 25, "main 8" : 25, "patio2" : 0,
    "hotback" : 0, "rock" : 17,}
subs["*ext mission night"] = { "b32" : 27, "sidefill2" : 34, "sidefill1" : 20,
    "cycright" : 18, "main 11" : 34, "main 10" : 34, "upfill1" : 8,
    "b34" : 34, "b25" : 34, "side l" : 34, "b23" : 34, "b22" : 16,
    "desk2" : 26, "hotbox2" : 34, "upfill4" : 8, "b24" : 34, "side r" : 34,
    "main 2" : 34, "main 5" : 34, "main 4" : 25, "main 7" : 34, "main 9" : 34,
    "main 8" : 34, "rock" : 20, "god" : 100, "marry2" : 34, "cuba1" : 5,}
subs["*2-2"] = { "b32" : 27, "sidefill2" : 34, "sidefill1" : 20,
    "cycright" : 18, "main 11" : 34, "main 10" : 34, "upfill1" : 70,
    "b34" : 34, "b25" : 34, "side l" : 34, "b23" : 34, "b22" : 16,
    "desk2" : 26, "hotbox2" : 34, "upfill4" : 70, "b24" : 34, "side r" : 34,
    "main 2" : 34, "main 5" : 34, "main 4" : 25, "main 7" : 34, "main 9" : 34,
    "main 8" : 34, "rock" : 20, "god" : 100, "marry2" : 34, "cuba1" : 5,}
subs["*2-2"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 18,
    "main 11" : 5, "main 10" : 5, "upfill1" : 70, "b34" : 34, "b25" : 71,
    "side l" : 34, "b23" : 67, "b22" : 50, "b32" : 57, "desk1" : 0,
    "hotbox2" : 59, "upfill4" : 70, "b24" : 67, "desk2" : 26, "main 3" : 0,
    "main 2" : 5, "main 5" : 5, "main 4" : 0, "main 7" : 5, "main 9" : 5,
    "main 8" : 5, "rock" : 20, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "god" : 100, "marry2" : 50, "cuba1" : 0, "side r" : 34,}
subs["*sewer"] = { "main 10" : 71, "upfill4" : 100, "main 11" : 66,
    "main 4" : 71, "upfill1" : 88, "main 8" : 71, "main 7" : 71,
    "main 5" : 100, "hotbox1" : 88, "hotback" : 66, "marry2" : 66,
    "upfill3" : 88, "marry1" : 66, "upfill2" : 100,}
subs["*2-2"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 18,
    "main 11" : 5, "main 10" : 5, "upfill1" : 70, "b34" : 34, "b25" : 71,
    "side l" : 34, "b23" : 67, "b22" : 50, "b32" : 57, "desk1" : 0,
    "hotbox2" : 59, "upfill4" : 70, "b24" : 67, "desk2" : 26, "main 3" : 0,
    "main 2" : 5, "main 5" : 56, "main 4" : 0, "main 7" : 5, "main 9" : 5,
    "main 8" : 5, "rock" : 20, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "god" : 100, "marry2" : 50, "cuba1" : 0, "side r" : 34,}
subs["*sewer"] = { "sidefill2" : 33, "sidefill1" : 33, "upfill4" : 10,
    "upfill3" : 22, "main 10" : 48, "upfill1" : 14, "b25" : 16, "b24" : 19,
    "b23" : 46, "b22" : 50, "hotbox1" : 0, "main 11" : 40, "upfill2" : 61,
    "main 2" : 54, "main 5" : 20, "main 4" : 45, "main 7" : 0, "main 9" : 84,
    "main 8" : 45, "hotback" : 40, "marry2" : 0, "marry1" : 0,}
subs["*sewer"] = { "sidefill2" : 33, "sidefill1" : 33, "upfill4" : 10,
    "upfill3" : 22, "main 10" : 48, "upfill1" : 14, "b25" : 16, "b24" : 19,
    "b23" : 64, "b22" : 50, "hotbox1" : 0, "main 11" : 40, "upfill2" : 61,
    "main 2" : 54, "main 5" : 20, "main 4" : 45, "main 7" : 0, "main 9" : 84,
    "main 8" : 45, "hotback" : 40, "sidepost1" : 31, "sidepost2" : 31,
    "marry2" : 0, "marry1" : 0,}
subs["*sewer"] = { "sidefill2" : 33, "sidefill1" : 33, "upfill4" : 10,
    "upfill3" : 22, "main 10" : 48, "upfill1" : 14, "b25" : 16, "b24" : 19,
    "b23" : 64, "b22" : 50, "hotbox1" : 0, "main 11" : 40, "upfill2" : 61,
    "main 2" : 54, "main 5" : 20, "main 4" : 45, "main 7" : 0, "main 9" : 84,
    "main 8" : 45, "hotback" : 40, "sidepost1" : 31, "sidepost2" : 31,
    "marry2" : 0, "marry1" : 0, "cuba1" : 59,}
subs["*marry"] = { "b32" : 23, "sidefill2" : 30, "sidefill1" : 17,
    "cycright" : 15, "main 11" : 30, "main 10" : 30, "upfill1" : 48,
    "b34" : 30, "b25" : 30, "side l" : 30, "b23" : 30, "b22" : 14,
    "desk2" : 23, "hotbox2" : 30, "upfill4" : 48, "b24" : 30, "side r" : 30,
    "main 3" : 30, "main 2" : 30, "main 5" : 30, "main 4" : 22, "main 7" : 30,
    "main 9" : 30, "main 8" : 30, "rock" : 17, "edge" : 15, "god" : 100,
    "marry2" : 30, "cuba1" : 4,}
subs["*marry"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 100,
    "main 11" : 55, "main 10" : 55, "upfill1" : 48, "b34" : 30, "b25" : 0,
    "side l" : 30, "b23" : 100, "b22" : 14, "b32" : 23, "main 4" : 0,
    "hotbox2" : 43, "hotbox1" : 49, "upfill4" : 48, "b24" : 100,
    "desk2" : 23, "patio2" : 0, "main 3" : 0, "main 2" : 30, "main 5" : 0,
    "patio1" : 0, "main 7" : 30, "phone" : 0, "main 9" : 30, "main 8" : 0,
    "rock" : 17, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0, "god" : 100,
    "marry2" : 34, "marry1" : 69, "cuba1" : 0, "cuba2" : 0, "side r" : 30,}
subs["*marry"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 100,
    "main 11" : 55, "main 10" : 55, "upfill1" : 48, "b34" : 30, "patio1" : 0,
    "b25" : 0, "side l" : 30, "b23" : 100, "b22" : 14, "b32" : 23,
    "hotbox2" : 43, "hotbox1" : 49, "upfill4" : 48, "b24" : 100,
    "desk2" : 23, "patio2" : 0, "main 3" : 0, "main 2" : 30, "main 5" : 0,
    "main 4" : 0, "main 7" : 30, "phone" : 0, "main 9" : 30, "main 8" : 0,
    "rock" : 17, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0, "god" : 100,
    "marry2" : 34, "marry1" : 69, "cuba1" : 0, "cuba2" : 0, "side r" : 30,}
