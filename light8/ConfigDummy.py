from random import randrange
from time import time
from __future__ import generators,division
from Subs import *
from Cue import *

from Configeffects import *

f1 = Fade('bogus sub, i hope', 0, 2, 0.1)

cues = [
    Cue("Seat filler", 0, 10, f1),
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
    'cafe1': 15,
    'cafe2': 16,
    'dream':17,
    'xmas':41,
}

from util import maxes,scaledict
FL=100
def fulls(chans):
    # pass a list or multiple args
    return dict([(c,FL) for c in chans])
def levs(chans,levs):
    return dict([(c,v) for c,v in zip(chans,levs)])

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
}

#subs["*marry"] = { "hotbox1" : 100,}
subs["*phone booth"] = { "phone" : 100,}
## subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
##     "main 11" : 100, "main 10" : 100, "b34" : 100, "b25" : 100, "b24" : 100,
##     "b22" : 100, "desk2" : 78, "phone" : 46, "upfill3" : 69, "upfill2" : 100,
##     "main 3" : 68, "main 2" : 100, "main 5" : 100, "main 4" : 100,
##     "main 7" : 100, "main 9" : 100, "main 8" : 100, "edge" : 46,
##     "sidepost1" : 100, "sidepost2" : 100, "marry2" : 100, "marry1" : 100,}
## subs["*int mission"] = { "sidefill1" : 100, "main 4" : 100, "main 9" : 100,
##     "main 8" : 100, "b24" : 100, "b23" : 100, "desk1" : 100, "desk2" : 100,
##     "b22" : 100, "rock" : 100, "marry1" : 100, "cuba1" : 25, "cuba2" : 51,
##     "main 10" : 100,}
## subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
##     "main 11" : 100, "main 10" : 100, "b34" : 100, "b25" : 100, "b24" : 100,
##     "b22" : 100, "desk2" : 78, "phone" : 46, "hotbox1" : 100, "upfill3" : 69,
##     "upfill2" : 100, "main 3" : 68, "main 2" : 100, "main 5" : 100,
##     "main 4" : 100, "main 7" : 100, "hotbox2" : 100, "main 9" : 100,
##     "main 8" : 100, "edge" : 46, "sidepost1" : 100, "sidepost2" : 100,
##     "marry2" : 100, "marry1" : 100,}
## subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
##     "cycright" : 41, "upfill3" : 69, "upfill2" : 100, "upfill1" : 56,
##     "side l" : 100, "b25" : 100, "cycleft" : 41, "b22" : 100, "desk2" : 78,
##     "phone" : 46, "hotbox1" : 100, "upfill4" : 56, "b24" : 100, "side r" : 100,
##     "main 11" : 100, "main 10" : 100, "main 3" : 68, "main 2" : 100,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 100,
##     "main 9" : 100, "main 8" : 100, "b34" : 100, "edge" : 46, "god" : 100,
##     "marry2" : 100, "marry1" : 100,}
## subs["*broadway open"] = { "sidefill2" : 100, "sidefill1" : 100,
##     "cycright" : 41, "upfill3" : 69, "upfill2" : 100, "upfill1" : 56,
##     "b34" : 100, "b25" : 100, "side l" : 100, "b22" : 100, "desk2" : 78,
##     "phone" : 80, "hotbox1" : 100, "upfill4" : 56, "b24" : 100, "side r" : 100,
##     "main 11" : 100, "main 10" : 100, "main 3" : 100, "main 2" : 100,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 100,
##     "main 9" : 100, "main 8" : 100, "cycleft" : 41, "edge" : 80,
##     "god" : 100, "marry2" : 100, "marry1" : 100,}
## subs["*int mission"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
##     "main 11" : 100, "main 10" : 100, "b34" : 0, "b25" : 0, "b24" : 100,
##     "b23" : 100, "desk1" : 53, "desk2" : 100, "b22" : 100, "hotbox2" : 85,
##     "hotbox1" : 25, "b32" : 62, "upfill3" : 37, "upfill2" : 66, "main 3" : 0,
##     "main 5" : 70, "main 4" : 100, "main 7" : 100, "main 9" : 100,
##     "main 8" : 100, "rock" : 52, "marry2" : 100, "marry1" : 61, "cuba1" : 0,
##     "cuba2" : 78,}
## subs["*int mission"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
##     "main 11" : 100, "main 10" : 100, "b34" : 0, "b25" : 0, "b24" : 100,
##     "b23" : 100, "desk1" : 53, "desk2" : 100, "b22" : 100, "hotbox2" : 85,
##     "hotbox1" : 25, "cycright" : 66, "b32" : 62, "upfill3" : 37,
##     "upfill2" : 66, "main 3" : 57, "main 2" : 0, "main 5" : 70, "main 4" : 100,
##     "main 7" : 100, "main 9" : 100, "main 8" : 100, "rock" : 52,
##     "marry2" : 100, "marry1" : 61, "cuba1" : 0, "cuba2" : 78,}

## subs["*hotbox dance"] = { "cycright" : 19, "upfill3" : 32, "upfill2" : 46,
##     "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46, "b23" : 0,
##     "desk1" : 0, "desk2" : 24, "upfill4" : 26, "side r" : 46, "main 11" : 46,
##     "main 10" : 100, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
##     "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0, "b13" : 0,
##     "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0, "red4" : 100,
##     "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0, "phone" : 0,
##     "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 100,
##     "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
##     "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
## subs["*hotbox table"] = { "sidefill2" : 0, "main 3" : 80, "main 2" : 62,
##     "main 11" : 0, "main 4" : 29, "main 7" : 10, "main 9" : 64, "main 8" : 10,
##     "b25" : 0, "b22" : 100, "phone" : 0, "edge" : 0, "b13" : 0, "marry2" : 0,
##     "main 5" : 34, "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
## subs["*hotbox table"] = { "sidefill2" : 0, "main 11" : 0, "b25" : 0,
##     "b22" : 100, "desk2" : 58, "phone" : 0, "main 3" : 80, "main 2" : 62,
##     "main 5" : 34, "main 4" : 100, "main 7" : 10, "hotbox2" : 46,
##     "main 9" : 64, "main 8" : 10, "edge" : 0, "b13" : 0, "rock" : 22,
##     "marry2" : 0, "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
## subs["*hotbox small table"] = { "red3" : 100, "red2" : 100, "main 3" : 80,
##     "main 2" : 62, "main 5" : 34, "main 4" : 100, "main 7" : 10,
##     "red4" : 100, "main 9" : 64, "main 8" : 10, "rock" : 22, "red1" : 100,
##     "desk2" : 58, "b22" : 100, "hotbox2" : 46, "upfill4" : 62, "god" : 100,
##     "upfill1" : 62, "cuba1" : 22,}
## subs["*hotbox small table"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 62, "main 11" : 0, "main 10" : 0, "upfill1" : 62,
##     "red4" : 100, "b25" : 5, "b22" : 100, "desk2" : 58, "desk1" : 52,
##     "hotbox2" : 0, "sidefill2" : 0, "main 3" : 47, "main 2" : 0,
##     "main 5" : 0, "main 4" : 0, "main 7" : 0, "phone" : 0, "main 9" : 11,
##     "main 8" : 0, "god" : 100, "edge" : 0, "rock" : 0, "marry2" : 0,
##     "marry1" : 0, "hotback" : 0, "cuba1" : 0, "cuba2" : 0,}

## subs["*ext mission"] = { "sidefill2" : 100, "sidefill1" : 59,
##     "cycright" : 53, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
##     "b34" : 100, "b25" : 100, "side l" : 100, "b23" : 100, "b22" : 49,
##     "b32" : 80, "phone" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100,
##     "desk2" : 78, "main 11" : 100, "main 10" : 100, "main 3" : 0,
##     "main 2" : 100, "main 5" : 100, "main 4" : 0, "main 7" : 100,
##     "hotbox2" : 100, "main 9" : 100, "main 8" : 100, "god" : 100,
##     "cycleft" : 0, "edge" : 0, "b13" : 0, "rock" : 60, "marry2" : 100,
##     "marry1" : 0, "side r" : 100,}

## subs["*broadway night 1-7"] = { "sidefill2" : 37, "sidefill1" : 37,
##     "upfill3" : 11, "upfill2" : 23, "b34" : 28, "b25" : 37, "b24" : 94,
##     "b23" : 100, "b22" : 82, "desk2" : 0, "desk1" : 0, "hotbox2" : 11,
##     "hotbox1" : 0, "blue1" : 93, "main 11" : 37, "blue3" : 93, "blue2" : 93,
##     "blue4" : 93, "main 10" : 37, "main 3" : 25, "main 2" : 37, "main 5" : 37,
##     "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37, "edge" : 12,
##     "god" : 100, "marry2" : 0, "marry1" : 37,}
## subs["*cuba right"] = { "main 3" : 31, "main 2" : 0, "main 10" : 100,
##     "b34" : 100, "b22" : 31, "desk2" : 85, "desk1" : 39, "edge" : 31,
##     "sidefill1" : 7, "cuba1" : 100, "cuba2" : 100,}
## subs["*cuba dance"] = { "sidefill2" : 100, "sidefill1" : 100,
##     "upfill4" : 100, "upfill3" : 81, "upfill2" : 100, "upfill1" : 100,
##     "b34" : 100, "b25" : 100, "b24" : 100, "b23" : 100, "desk1" : 100,
##     "desk2" : 100, "b22" : 100, "phone" : 100, "main 11" : 100, "main 10" : 100,
##     "main 3" : 100, "main 2" : 100, "main 5" : 100, "main 4" : 100,
##     "main 7" : 100, "main 9" : 100, "main 8" : 100, "edge" : 100,
##     "god" : 100, "marry2" : 100, "marry1" : 100, "hotback" : 100,
##     "cuba1" : 100, "cuba2" : 100,}

## subs["*cuba love"] = { "sidefill2" : 0, "sidefill1" : 0, "upfill4" : 0,
##     "main 11" : 28, "main 10" : 28, "upfill1" : 0, "b34" : 9, "b25" : 100,
##     "b24" : 59, "b23" : 59, "b22" : 100, "desk2" : 16, "desk1" : 0,
##     "phone" : 0, "hotbox1" : 0, "upfill3" : 43, "upfill2" : 43, "main 3" : 28,
##     "main 2" : 100, "main 5" : 16, "main 4" : 16, "main 7" : 0, "main 9" : 65,
##     "main 8" : 74, "edge" : 0, "marry2" : 9, "marry1" : 0, "hotback" : 0,
##     "cuba1" : 0, "cuba2" : 0,}
## subs["*ext mission night"] = { "sidefill2" : 39, "sidefill1" : 23,
##     "cycright" : 20, "main 11" : 29, "main 10" : 29, "upfill1" : 8,
##     "b34" : 39, "b25" : 39, "side l" : 39, "b23" : 39, "b22" : 19,
##     "b32" : 31, "upfill4" : 8, "b24" : 39, "side r" : 39, "desk2" : 18,
##     "main 2" : 39, "main 5" : 39, "main 9" : 39, "main 8" : 39, "god" : 100,
##     "marry2" : 39,}
## subs["*ext mission night"] = { "sidefill2" : 39, "sidefill1" : 23,
##     "cycright" : 20, "main 11" : 29, "main 10" : 29, "upfill1" : 8,
##     "b34" : 39, "b25" : 39, "side l" : 39, "b23" : 39, "b22" : 19,
##     "b32" : 31, "upfill4" : 8, "b24" : 39, "side r" : 39, "desk2" : 18,
##     "main 2" : 39, "main 5" : 39, "main 9" : 39, "main 8" : 39, "god" : 100,
##     "marry2" : 39,}
## subs["*ext mission night"] = { "cycright" : 6, "main 11" : 15,
##     "main 10" : 15, "upfill1" : 0, "b25" : 25, "side l" : 39, "b23" : 25,
##     "b22" : 5, "desk2" : 4, "upfill4" : 0, "side r" : 39, "upfill3" : 0,
##     "upfill2" : 0, "patio1" : 0, "god" : 86, "edge" : 0, "b13" : 0,
##     "sidepost2" : 0, "marry2" : 25, "marry1" : 0, "cuba1" : 5, "cuba2" : 0,
##     "sidepost1" : 0, "sidefill2" : 25, "sidefill1" : 9, "b24" : 25,
##     "b34" : 25, "cycleft" : 0, "b32" : 17, "desk1" : 0, "hotbox2" : 25,
##     "hotbox1" : 0, "main 3" : 0, "main 2" : 25, "main 5" : 25, "main 4" : 25,
##     "main 7" : 25, "phone" : 0, "main 9" : 25, "main 8" : 25, "patio2" : 0,
##     "hotback" : 0, "rock" : 17,}
## subs["*ext mission night"] = { "b32" : 27, "sidefill2" : 34, "sidefill1" : 20,
##     "cycright" : 18, "main 11" : 34, "main 10" : 34, "upfill1" : 8,
##     "b34" : 34, "b25" : 34, "side l" : 34, "b23" : 34, "b22" : 16,
##     "desk2" : 26, "hotbox2" : 34, "upfill4" : 8, "b24" : 34, "side r" : 34,
##     "main 2" : 34, "main 5" : 34, "main 4" : 25, "main 7" : 34, "main 9" : 34,
##     "main 8" : 34, "rock" : 20, "god" : 100, "marry2" : 34, "cuba1" : 5,}

## subs["*sewer"] = { "sidefill2" : 33, "sidefill1" : 33, "upfill4" : 10,
##     "upfill3" : 22, "main 10" : 48, "upfill1" : 14, "b25" : 16, "b24" : 19,
##     "b23" : 64, "b22" : 50, "hotbox1" : 0, "main 11" : 40, "upfill2" : 61,
##     "main 2" : 54, "main 5" : 20, "main 4" : 45, "main 7" : 0, "main 9" : 84,
##     "main 8" : 45, "hotback" : 40, "sidepost1" : 31, "sidepost2" : 31,
##     "marry2" : 0, "marry1" : 0, "cuba1" : 59,}

## subs["*marry"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 100,
##     "main 11" : 55, "main 10" : 55, "upfill1" : 48, "b34" : 30, "patio1" : 0,
##     "b25" : 0, "side l" : 30, "b23" : 100, "b22" : 14, "b32" : 23,
##     "hotbox2" : 43, "hotbox1" : 49, "upfill4" : 48, "b24" : 100,
##     "desk2" : 23, "patio2" : 0, "main 3" : 0, "main 2" : 30, "main 5" : 0,
##     "main 4" : 0, "main 7" : 30, "phone" : 0, "main 9" : 30, "main 8" : 0,
##     "rock" : 17, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0, "god" : 100,
##     "marry2" : 34, "marry1" : 69, "cuba1" : 0, "cuba2" : 0, "side r" : 30,}

## subs['*1-01-0']=subs['*broadway open'].copy()
## subs['*1-02-0']=subs['*int mission'].copy()
## subs['*1-03-0']=subs['*phone booth'].copy()

## subs['*1-04-00-dance']=subs['*hotbox dance'].copy()
## subs['*1-04-10-after dance']=subs['*hotbox dance'].copy()
## subs['*1-04-20-table']=subs['*hotbox table'].copy()
## subs['*1-04-30-small table']=subs['*hotbox small table'].copy()

## subs['*1-05-0']=subs['*broadway open'].copy()
## subs['*1-06-0']=subs['*ext mission'].copy()
## subs['*1-07-0']=subs['*broadway night 1-7'].copy()


## subs['*1-08-00-left cafe']={ "main 3" : 100, "edge" : 100,}
## subs['*1-08-10-right cafe']= fulls(('cuba1','cuba2'))
## subs['*1-08-20-backdrop']=fulls(('upfill1','upfill2','upfill3','upfill4'))

## subs['*1-09-0']=subs['*cuba love'].copy()
## subs['*1-10-0']=subs['*ext mission night'].copy()

## subs['*2-01-0-dance']=subs['*hotbox dance'].copy()
## subs['*2-01-1-after dance']=subs['*hotbox dance'].copy()
## subs['*2-01-2-table']=subs['*hotbox table'].copy()
## subs['*2-01-3-small table']=subs['*hotbox small table'].copy()

## subs["*2-02-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 18,
##     "main 11" : 5, "main 10" : 5, "upfill1" : 70, "b34" : 34, "b25" : 71,
##     "side l" : 34, "b23" : 67, "b22" : 50, "b32" : 57, "desk1" : 0,
##     "hotbox2" : 59, "upfill4" : 70, "b24" : 67, "desk2" : 26, "main 3" : 0,
##     "main 2" : 5, "main 5" : 56, "main 4" : 0, "main 7" : 5, "main 9" : 5,
##     "main 8" : 5, "rock" : 20, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
##     "god" : 100, "marry2" : 50, "cuba1" : 0, "side r" : 34,}

## subs['*2-03-00-open dance']=subs['*sewer'].copy()
## subs['*2-03-10-dialogue']=subs['*sewer'].copy()
## subs['*2-03-20-luck']=subs['*sewer'].copy()

## subs['*2-04-0']=subs['*2-02-0'].copy() # sue me
## subs['*2-05-0']=subs['*int mission'].copy()
## subs['*2-06-0']=subs['*marry'].copy()
## subs['*2-07-0']=subs['*broadway open'].copy()
## subs["*curtain"] = { "god" : 100, "house" : 81,}
## subs["*curtain"] = { "sidefill2" : 76, "sidefill1" : 76, "upfill4" : 39,
##     "main 11" : 76, "main 10" : 76, "upfill1" : 39, "house" : 81,
##     "desk1" : 76, "desk2" : 76, "phone" : 76, "hotbox1" : 39, "upfill3" : 39,
##     "upfill2" : 39, "main 3" : 76, "main 5" : 100, "main 4" : 76,
##     "hotbox2" : 39, "god" : 100, "edge" : 76, "marry2" : 76, "marry1" : 76,
##     "hotback" : 76, "cuba1" : 76, "cuba2" : 76,}
## subs["*1-01-9 end conversations"] = { "sidefill2" : 63, "sidefill1" : 26,
##     "upfill4" : 4, "upfill3" : 43, "upfill2" : 63, "upfill1" : 4,
##     "b34" : 63, "b25" : 63, "side l" : 63, "b23" : 12, "b22" : 63,
##     "desk2" : 12, "phone" : 50, "hotbox1" : 63, "b24" : 42, "side r" : 63,
##     "main 11" : 63, "main 10" : 63, "main 3" : 26, "main 2" : 63,
##     "main 5" : 63, "main 4" : 63, "main 7" : 63, "hotbox2" : 63,
##     "main 9" : 63, "main 8" : 63, "edge" : 13, "god" : 100, "marry2" : 63,
##     "marry1" : 63, "cuba1" : 63, "cuba2" : 42,}
## subs["*1-02-1 desk solo"] = { "sidefill2" : 51, "cycright" : 66,
##     "upfill3" : 37, "upfill2" : 66, "rock" : 52, "b24" : 100, "b23" : 100,
##     "desk1" : 53, "desk2" : 100, "b22" : 100, "hotbox2" : 85, "hotbox1" : 25,
##     "b32" : 62, "blue1" : 33, "main 11" : 100, "blue3" : 33, "blue2" : 33,
##     "blue4" : 33, "main 10" : 100, "main 3" : 57, "main 5" : 70,
##     "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
##     "god" : 100, "marry2" : 100, "marry1" : 61, "cuba2" : 78,}
## subs["*1-02-1 desk solo"] = { "sidefill2" : 51, "cycright" : 37,
##     "upfill3" : 0, "upfill2" : 0, "cycleft" : 0, "b24" : 22, "b23" : 100,
##     "desk1" : 53, "desk2" : 89, "b22" : 100, "hotbox2" : 7, "hotbox1" : 25,
##     "b32" : 0, "blue1" : 33, "main 11" : 22, "blue3" : 33, "blue2" : 33,
##     "blue4" : 33, "main 10" : 22, "main 3" : 57, "main 5" : 0, "main 4" : 22,
##     "main 7" : 100, "main 9" : 22, "god" : 100, "rock" : 14, "main 8" : 22,
##     "marry2" : 22, "marry1" : 61, "cuba2" : 0,}
## subs["*1-04-01 dark tables"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 26, "upfill3" : 32, "upfill2" : 46, "upfill1" : 26,
##     "red4" : 100, "b34" : 30, "cycleft" : 19, "desk2" : 24, "hotbox2" : 78,
##     "hotbox1" : 42, "cycright" : 19, "b32" : 43, "blue1" : 33, "main 11" : 46,
##     "blue3" : 33, "blue2" : 33, "blue4" : 33, "main 10" : 100, "main 3" : 46,
##     "main 2" : 46, "main 5" : 100, "main 4" : 46, "main 7" : 100,
##     "main 9" : 46, "main 8" : 46, "hotback" : 100, "god" : 100,}
## subs["*1-04-01 dark tables"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 26, "upfill3" : 32, "upfill2" : 46, "upfill1" : 26,
##     "red4" : 100, "b34" : 12, "cycleft" : 19, "b23" : 67, "desk2" : 24,
##     "hotbox2" : 45, "hotbox1" : 46, "cycright" : 19, "b24" : 67,
##     "b32" : 2, "blue1" : 33, "main 11" : 46, "blue3" : 33, "blue2" : 33,
##     "blue4" : 33, "main 10" : 100, "main 3" : 13, "main 2" : 46,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "main 9" : 100,
##     "main 8" : 29, "edge" : 9, "god" : 100, "hotback" : 100, "cuba2" : 0,}
## subs["*1-04-01 dark tables"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 26, "upfill3" : 32, "upfill2" : 46, "upfill1" : 26,
##     "red4" : 100, "b34" : 12, "cycleft" : 19, "b23" : 67, "desk2" : 24,
##     "hotbox2" : 45, "hotbox1" : 46, "cycright" : 19, "b24" : 67,
##     "b32" : 2, "blue1" : 33, "main 11" : 46, "blue3" : 33, "blue2" : 33,
##     "blue4" : 33, "main 10" : 100, "main 3" : 13, "main 2" : 46,
##     "main 5" : 0, "main 4" : 100, "main 7" : 100, "main 9" : 100,
##     "main 8" : 29, "edge" : 9, "god" : 100, "hotback" : 100, "cuba2" : 0,}
## subs["*1-04-01 dark tables"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 26, "upfill3" : 0, "upfill2" : 0, "upfill1" : 26,
##     "red4" : 100, "b34" : 12, "cycleft" : 19, "b23" : 67, "desk2" : 24,
##     "hotbox2" : 45, "hotbox1" : 46, "cycright" : 19, "b24" : 67,
##     "b32" : 2, "blue1" : 33, "main 11" : 46, "blue3" : 33, "blue2" : 33,
##     "blue4" : 33, "main 10" : 100, "main 3" : 13, "main 2" : 46,
##     "main 5" : 0, "main 4" : 100, "main 7" : 100, "main 9" : 100,
##     "main 8" : 29, "edge" : 9, "god" : 100, "hotback" : 100, "cuba2" : 0,}
## subs["*1-05-0"] = { "sidefill2" : 100, "sidefill1" : 100, "cycright" : 39,
##     "upfill3" : 40, "upfill2" : 40, "upfill1" : 0, "b34" : 34, "b25" : 100,
##     "side l" : 100, "b23" : 100, "b22" : 100, "desk2" : 31, "desk1" : 19,
##     "phone" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100, "side r" : 82,
##     "main 11" : 89, "main 10" : 100, "main 3" : 85, "main 2" : 100,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 38,
##     "main 9" : 100, "main 8" : 100, "cycleft" : 27, "edge" : 48,
##     "b13" : 100, "god" : 100, "marry2" : 0, "marry1" : 0,}
## subs["*1-05-0"] = { "sidefill2" : 100, "sidefill1" : 100, "cycright" : 36,
##     "upfill3" : 37, "upfill2" : 37, "upfill1" : 0, "b34" : 13, "b25" : 100,
##     "side l" : 100, "b23" : 100, "b22" : 100, "desk2" : 31, "desk1" : 19,
##     "phone" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100, "side r" : 82,
##     "main 11" : 89, "main 10" : 100, "main 3" : 85, "main 2" : 100,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 17,
##     "main 9" : 100, "main 8" : 100, "cycleft" : 18, "edge" : 37,
##     "b13" : 100, "god" : 100, "marry2" : 0, "marry1" : 0,}
## subs["*1-07-0"] = { "sidefill2" : 37, "sidefill1" : 37, "b24" : 100,
##     "upfill3" : 11, "upfill2" : 23, "b34" : 28, "b25" : 64, "side l" : 49,
##     "b23" : 100, "b22" : 82, "desk2" : 0, "desk1" : 0, "hotbox2" : 11,
##     "hotbox1" : 0, "side r" : 36, "blue1" : 93, "main 11" : 37, "blue3" : 93,
##     "blue2" : 93, "blue4" : 93, "main 10" : 37, "main 3" : 25, "main 2" : 37,
##     "main 5" : 37, "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37,
##     "edge" : 12, "god" : 100, "marry2" : 0, "marry1" : 37,}
## subs["*1-08-10-right cafe"] = { "main 9" : 0, "cuba2" : 100, "b34" : 54,
##     "main 8" : 0, "cuba1" : 100, "b32" : 43,}
## subs["*1-08-30-full"] = { "b32" : 43, "sidefill2" : 38, "sidefill1" : 38,
##     "cycright" : 15, "upfill3" : 100, "upfill2" : 100, "upfill1" : 100,
##     "side l" : 38, "b25" : 100, "cycleft" : 15, "b23" : 100, "b22" : 100,
##     "desk2" : 30, "phone" : 31, "hotbox1" : 38, "upfill4" : 100,
##     "b24" : 100, "side r" : 38, "main 11" : 38, "main 10" : 38, "main 3" : 38,
##     "main 2" : 38, "main 5" : 38, "main 4" : 38, "main 7" : 38, "hotbox2" : 38,
##     "main 9" : 38, "main 8" : 38, "b34" : 54, "edge" : 31, "god" : 100,
##     "marry2" : 38, "marry1" : 38, "cuba1" : 100, "cuba2" : 100,}
## subs["*1-09-0"] = { "red3" : 64, "red2" : 64, "red1" : 64, "upfill3" : 43,
##     "upfill2" : 43, "red4" : 64, "b34" : 9, "b25" : 100, "b24" : 59,
##     "b23" : 59, "b22" : 100, "desk2" : 16, "blue1" : 53, "main 11" : 28,
##     "blue3" : 53, "blue2" : 53, "blue4" : 53, "main 10" : 28, "main 3" : 28,
##     "main 2" : 100, "main 5" : 16, "main 4" : 16, "main 9" : 65,
##     "main 8" : 74, "god" : 100, "marry2" : 9,}
## subs["*1-10-0"] = { "b32" : 27, "sidefill2" : 34, "sidefill1" : 20,
##     "cycright" : 18, "main 11" : 34, "main 10" : 34, "upfill1" : 9,
##     "b34" : 34, "b25" : 34, "side l" : 34, "b23" : 34, "b22" : 16,
##     "desk2" : 26, "hotbox2" : 34, "upfill4" : 9, "b24" : 34, "side r" : 34,
##     "blue1" : 70, "blue3" : 70, "blue2" : 70, "blue4" : 70, "main 2" : 34,
##     "main 5" : 34, "main 4" : 25, "main 7" : 34, "main 9" : 34, "main 8" : 34,
##     "rock" : 20, "god" : 100, "marry2" : 34, "cuba1" : 5,}
## subs["*curtain"] = { "sidefill2" : 73, "sidefill1" : 73, "cycright" : 30,
##     "upfill3" : 50, "upfill2" : 73, "upfill1" : 41, "side l" : 73,
##     "house" : 73, "b25" : 73, "cycleft" : 30, "b22" : 73, "desk2" : 57,
##     "phone" : 58, "hotbox1" : 73, "upfill4" : 41, "b24" : 73, "side r" : 73,
##     "main 11" : 73, "main 10" : 73, "main 3" : 73, "main 2" : 73,
##     "main 5" : 73, "main 4" : 73, "main 7" : 73, "hotbox2" : 73,
##     "main 9" : 73, "main 8" : 73, "b34" : 73, "edge" : 58, "god" : 100,
##     "marry2" : 73, "marry1" : 73,}
## subs["*curtain"] = { "sidefill2" : 73, "sidefill1" : 73, "cycright" : 30,
##     "upfill3" : 50, "upfill2" : 73, "upfill1" : 41, "b34" : 73, "house" : 73,
##     "b25" : 73, "side l" : 73, "b22" : 73, "desk2" : 57, "phone" : 58,
##     "hotbox1" : 0, "upfill4" : 41, "b24" : 73, "side r" : 73, "main 11" : 73,
##     "main 10" : 73, "main 3" : 73, "main 2" : 73, "main 5" : 73,
##     "main 4" : 73, "main 7" : 73, "hotbox2" : 73, "main 9" : 73,
##     "main 8" : 73, "cycleft" : 30, "edge" : 58, "god" : 100, "marry2" : 73,
##     "marry1" : 73,}
## subs["*2-01-01-solo"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 67, "main 11" : 46, "upfill2" : 1, "upfill1" : 67,
##     "red4" : 100, "b34" : 30, "cycleft" : 55, "desk2" : 24, "hotbox2" : 78,
##     "hotbox1" : 42, "cycright" : 55, "b32" : 43, "main 10" : 100,
##     "main 3" : 46, "main 2" : 46, "main 5" : 100, "main 4" : 46,
##     "main 7" : 100, "main 9" : 46, "main 8" : 46, "hotback" : 100,
##     "god" : 100,}
## subs["*2-01-01-solo"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 67, "main 11" : 0, "upfill2" : 1, "upfill1" : 67,
##     "red4" : 100, "b34" : 0, "cycleft" : 55, "desk2" : 24, "hotbox2" : 78,
##     "hotbox1" : 42, "cycright" : 55, "b32" : 43, "main 10" : 0, "main 3" : 0,
##     "main 2" : 0, "main 5" : 0, "main 4" : 0, "main 7" : 100, "phone" : 0,
##     "main 9" : 0, "main 8" : 0, "hotback" : 100, "god" : 100, "cuba1" : 0,
##     "cuba2" : 0,}
## subs["*2-01-01-solo"] = { "red3" : 100, "red2" : 100, "red1" : 100,
##     "upfill4" : 67, "main 11" : 0, "upfill2" : 1, "upfill1" : 67,
##     "red4" : 100, "b34" : 0, "cycleft" : 55, "b23" : 100, "desk2" : 24,
##     "hotbox2" : 78, "hotbox1" : 42, "cycright" : 55, "b24" : 100,
##     "b32" : 43, "main 10" : 0, "main 3" : 0, "main 2" : 0, "main 5" : 0,
##     "main 4" : 0, "main 7" : 100, "phone" : 0, "main 9" : 0, "main 8" : 0,
##     "hotback" : 100, "god" : 100, "cuba1" : 0, "cuba2" : 0,}
## subs["*2-02-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 0,
##     "main 11" : 5, "main 10" : 68, "upfill1" : 0, "b34" : 0, "b25" : 0,
##     "side l" : 34, "b23" : 0, "b22" : 0, "b32" : 0, "desk1" : 0,
##     "hotbox2" : 0, "upfill4" : 0, "b24" : 0, "desk2" : 0, "main 3" : 0,
##     "main 2" : 5, "main 5" : 18, "main 4" : 60, "main 7" : 42, "main 9" : 68,
##     "main 8" : 50, "rock" : 0, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
##     "god" : 100, "marry2" : 65, "cuba1" : 0, "side r" : 34,}
## subs["*2-02-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 0,
##     "main 11" : 5, "main 10" : 68, "upfill1" : 0, "b34" : 0, "b25" : 0,
##     "side l" : 34, "b23" : 0, "b22" : 0, "b32" : 0, "desk1" : 0,
##     "hotbox2" : 0, "upfill4" : 0, "b24" : 0, "desk2" : 0, "main 3" : 0,
##     "main 2" : 5, "main 5" : 18, "main 4" : 60, "main 7" : 42, "main 9" : 68,
##     "main 8" : 50, "rock" : 0, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
##     "god" : 100, "marry2" : 65, "hotback" : 0, "cuba1" : 0, "side r" : 34,}
## subs["*2-03-00-open dance"] = { "sidefill2" : 33, "sidefill1" : 33,
##     "upfill4" : 10, "upfill3" : 22, "main 10" : 61, "upfill1" : 14,
##     "b25" : 16, "b24" : 19, "b23" : 28, "b22" : 50, "hotbox1" : 0,
##     "main 11" : 28, "upfill2" : 61, "main 2" : 54, "main 5" : 20,
##     "main 4" : 45, "main 7" : 0, "main 9" : 42, "main 8" : 34, "hotback" : 40,
##     "sidepost1" : 31, "sidepost2" : 31, "marry2" : 0, "marry1" : 0,
##     "cuba1" : 59,}
## subs["*2-03-10-dialogue"] = { "sidefill2" : 34, "sidefill1" : 57,
##     "upfill4" : 10, "upfill3" : 22, "main 10" : 48, "upfill1" : 14,
##     "b25" : 16, "b24" : 19, "b23" : 64, "b22" : 62, "hotbox1" : 0,
##     "main 11" : 40, "upfill2" : 61, "main 2" : 54, "main 5" : 20,
##     "main 4" : 45, "main 7" : 0, "main 9" : 73, "main 8" : 22, "hotback" : 40,
##     "sidepost1" : 31, "sidepost2" : 31, "marry2" : 0, "marry1" : 0,
##     "cuba1" : 59, "b13" : 60,}
## subs["*2-04-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 18,
##     "main 11" : 5, "main 10" : 5, "upfill1" : 70, "b34" : 34, "b25" : 71,
##     "side l" : 34, "b23" : 67, "b22" : 50, "b32" : 57, "desk1" : 0,
##     "hotbox2" : 59, "upfill4" : 70, "b24" : 67, "desk2" : 26, "main 3" : 30,
##     "main 2" : 5, "main 5" : 56, "main 4" : 0, "main 7" : 5, "main 9" : 5,
##     "main 8" : 5, "god" : 100, "edge" : 0, "side r" : 34, "b13" : 43,
##     "sidepost2" : 0, "rock" : 20, "marry2" : 50, "cuba1" : 0, "sidepost1" : 0,}
## subs["*2-04-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 18,
##     "main 11" : 5, "main 10" : 5, "upfill1" : 70, "b34" : 34, "b25" : 71,
##     "side l" : 34, "b23" : 67, "b22" : 50, "b32" : 57, "desk1" : 24,
##     "hotbox2" : 59, "upfill4" : 70, "b24" : 67, "desk2" : 26, "main 3" : 45,
##     "main 2" : 5, "main 5" : 56, "main 4" : 0, "main 7" : 5, "main 9" : 5,
##     "main 8" : 5, "god" : 100, "edge" : 0, "side r" : 34, "b13" : 39,
##     "sidepost2" : 0, "rock" : 20, "marry2" : 50, "cuba1" : 0, "sidepost1" : 0,}
## subs["*2-05-0"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
##     "main 11" : 100, "main 10" : 55, "b34" : 0, "b25" : 0, "b24" : 68,
##     "b23" : 68, "desk1" : 3, "desk2" : 92, "b22" : 68, "hotbox2" : 61,
##     "hotbox1" : 0, "cycright" : 66, "b32" : 36, "upfill3" : 37, "upfill2" : 66,
##     "main 3" : 45, "main 2" : 0, "main 5" : 70, "main 4" : 50, "main 7" : 55,
##     "main 9" : 55, "main 8" : 55, "rock" : 26, "marry2" : 64, "marry1" : 11,
##     "cuba1" : 0, "cuba2" : 52,}
## subs["*2-05-1-dream"] = { "sidefill2" : 51, "cycright" : 66, "main 11" : 100,
##     "upfill2" : 66, "god" : 100, "b24" : 68, "b23" : 68, "desk1" : 3,
##     "b32" : 36, "b22" : 68, "hotbox2" : 61, "desk2" : 92, "upfill3" : 37,
##     "main 10" : 55, "main 3" : 45, "main 5" : 70, "main 4" : 50,
##     "main 7" : 55, "main 9" : 55, "main 8" : 55, "rock" : 26, "marry2" : 64,
##     "marry1" : 11, "cuba2" : 52,}
## subs["*2-05-1-dream"] = { "sidefill2" : 51, "cycright" : 0, "main 11" : 7,
##     "upfill2" : 0, "upfill1" : 0, "b34" : 0, "cycleft" : 0, "b24" : 0,
##     "b23" : 0, "desk1" : 0, "desk2" : 92, "b22" : 0, "hotbox2" : 0,
##     "hotbox1" : 0, "upfill4" : 0, "b32" : 0, "upfill3" : 0, "main 10" : 0,
##     "main 3" : 0, "main 2" : 0, "main 5" : 0, "main 4" : 0, "main 7" : 0,
##     "phone" : 0, "main 9" : 0, "god" : 100, "rock" : 90, "edge" : 0,
##     "b13" : 0, "main 8" : 0, "marry2" : 0, "marry1" : 0, "cuba2" : 0,}
## subs["*2-05-2-boat"] = { "sidefill2" : 43, "cycright" : 55, "main 11" : 84,
##     "upfill2" : 55, "god" : 100, "b24" : 84, "b23" : 84, "desk1" : 44,
##     "b32" : 52, "b22" : 84, "hotbox2" : 71, "hotbox1" : 21, "desk2" : 84,
##     "upfill3" : 31, "main 10" : 84, "main 3" : 48, "main 5" : 59,
##     "main 4" : 84, "main 7" : 84, "main 9" : 84, "main 8" : 84, "rock" : 43,
##     "marry2" : 84, "marry1" : 51, "cuba2" : 65,}
## subs["*2-05-2-boat"] = { "sidefill2" : 43, "cycright" : 55, "main 11" : 84,
##     "upfill2" : 55, "rock" : 43, "b24" : 100, "b23" : 100, "desk1" : 44,
##     "b32" : 52, "b22" : 100, "hotbox2" : 95, "hotbox1" : 21, "desk2" : 84,
##     "upfill3" : 31, "main 10" : 84, "main 3" : 72, "main 5" : 83,
##     "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
##     "god" : 100, "marry2" : 100, "marry1" : 75, "cuba2" : 65,}
## subs["*2-07-0"] = { "sidefill2" : 100, "sidefill1" : 83, "cycright" : 41,
##     "upfill3" : 69, "upfill2" : 100, "upfill1" : 56, "b34" : 100,
##     "b25" : 100, "side l" : 100, "b22" : 100, "desk2" : 78, "phone" : 62,
##     "hotbox1" : 14, "upfill4" : 56, "b24" : 100, "side r" : 100,
##     "main 11" : 100, "main 10" : 100, "main 3" : 83, "main 2" : 100,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 5,
##     "main 9" : 100, "main 8" : 100, "god" : 100, "cycleft" : 41,
##     "edge" : 63, "rock" : 0, "marry2" : 100, "marry1" : 100,}
## subs["*2-07-0"] = { "sidefill2" : 100, "sidefill1" : 83, "cycright" : 41,
##     "upfill3" : 69, "upfill2" : 100, "upfill1" : 56, "b34" : 100,
##     "b25" : 100, "side l" : 100, "b23" : 100, "b22" : 100, "desk2" : 78,
##     "phone" : 62, "hotbox1" : 14, "upfill4" : 56, "b24" : 100, "side r" : 100,
##     "main 11" : 100, "main 10" : 100, "main 3" : 83, "main 2" : 100,
##     "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 5,
##     "main 9" : 100, "main 8" : 100, "god" : 100, "cycleft" : 41,
##     "edge" : 63, "rock" : 0, "marry2" : 100, "marry1" : 100,}

###################################


subs["*1-01-0"] = { "sidefill2" : 100, "sidefill1" : 100, "cycright" : 41,
    "upfill3" : 69, "upfill2" : 100, "upfill1" : 56, "b34" : 100,
    "b25" : 100, "side l" : 100, "b22" : 100, "desk2" : 78, "phone" : 80,
    "hotbox1" : 100, "upfill4" : 56, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 100, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 100,
    "main 9" : 100, "main 8" : 100, "cycleft" : 41, "edge" : 80,
    "god" : 100, "marry2" : 100, "marry1" : 100,}
subs["*1-01-9 end conversations"] = { "sidefill2" : 63, "sidefill1" : 26,
    "upfill4" : 4, "upfill3" : 43, "upfill2" : 63, "upfill1" : 4,
    "b34" : 63, "b25" : 63, "side l" : 63, "b23" : 12, "b22" : 63,
    "desk2" : 12, "phone" : 50, "hotbox1" : 63, "b24" : 42, "side r" : 63,
    "main 11" : 63, "main 10" : 63, "main 3" : 26, "main 2" : 63,
    "main 5" : 63, "main 4" : 63, "main 7" : 63, "hotbox2" : 63,
    "main 9" : 63, "main 8" : 63, "edge" : 13, "god" : 100, "marry2" : 63,
    "marry1" : 63, "cuba1" : 63, "cuba2" : 42,}
subs["*1-02-0"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 100, "b34" : 0, "b25" : 0, "b24" : 100,
    "b23" : 100, "desk1" : 53, "desk2" : 100, "b22" : 100, "hotbox2" : 85,
    "hotbox1" : 25, "cycright" : 66, "b32" : 62, "upfill3" : 37,
    "upfill2" : 66, "main 3" : 57, "main 2" : 0, "main 5" : 70, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "rock" : 52,
    "marry2" : 100, "marry1" : 61, "cuba1" : 0, "cuba2" : 78,}
subs["*1-02-1 desk solo"] = { "sidefill2" : 51, "cycright" : 37,
    "upfill3" : 0, "upfill2" : 0, "god" : 100, "cycleft" : 0, "b23" : 100,
    "desk1" : 53, "desk2" : 89, "b22" : 100, "hotbox2" : 7, "hotbox1" : 25,
    "b24" : 22, "b32" : 0, "blue1" : 33, "main 11" : 22, "blue3" : 33,
    "blue2" : 33, "blue4" : 33, "main 10" : 22, "main 3" : 57, "main 5" : 0,
    "main 4" : 22, "main 7" : 100, "main 9" : 22, "main 8" : 22,
    "rock" : 14, "marry2" : 22, "marry1" : 61, "cuba2" : 0,}
subs["*1-03-0"] = { "phone" : 100,}
subs["*1-04-00-dance"] = { "cycright" : 19, "upfill3" : 32, "upfill2" : 46,
    "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46, "b23" : 0,
    "desk1" : 0, "desk2" : 24, "upfill4" : 26, "side r" : 46, "main 11" : 46,
    "main 10" : 100, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0, "b13" : 0,
    "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0, "red4" : 100,
    "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0, "phone" : 0,
    "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 100,
    "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
    "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
subs["*1-04-01 dark tables"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 26, "upfill3" : 0, "upfill2" : 0, "upfill1" : 26,
    "red4" : 100, "b34" : 12, "cycleft" : 19, "b23" : 67, "desk2" : 24,
    "hotbox2" : 45, "hotbox1" : 46, "cycright" : 19, "b24" : 67,
    "b32" : 2, "blue1" : 33, "main 11" : 46, "blue3" : 33, "blue2" : 33,
    "blue4" : 33, "main 10" : 100, "main 3" : 13, "main 2" : 46,
    "main 5" : 0, "main 4" : 100, "main 7" : 100, "main 9" : 100,
    "main 8" : 29, "edge" : 9, "god" : 100, "hotback" : 100, "cuba2" : 0,}
subs["*1-04-10-after dance"] = { "cycright" : 19, "upfill3" : 32,
    "upfill2" : 46, "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46,
    "b23" : 0, "desk1" : 0, "desk2" : 24, "upfill4" : 26, "side r" : 46,
    "main 11" : 46, "main 10" : 100, "god" : 100, "edge" : 0, "sidepost1" : 0,
    "sidepost2" : 0, "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0,
    "b13" : 0, "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0,
    "red4" : 100, "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0,
    "phone" : 0, "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 100,
    "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
    "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
subs["*1-04-20-table"] = { "sidefill2" : 0, "main 11" : 0, "b25" : 0,
    "b22" : 100, "desk2" : 58, "phone" : 0, "main 3" : 80, "main 2" : 62,
    "main 5" : 34, "main 4" : 100, "main 7" : 10, "hotbox2" : 46,
    "main 9" : 64, "main 8" : 10, "edge" : 0, "b13" : 0, "rock" : 22,
    "marry2" : 0, "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
subs["*1-04-30-small table"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 62, "main 11" : 0, "main 10" : 0, "upfill1" : 62,
    "red4" : 100, "b25" : 5, "b22" : 100, "desk2" : 58, "desk1" : 52,
    "hotbox2" : 0, "sidefill2" : 0, "main 3" : 47, "main 2" : 0,
    "main 5" : 0, "main 4" : 0, "main 7" : 0, "phone" : 0, "main 9" : 11,
    "main 8" : 0, "god" : 100, "edge" : 0, "rock" : 0, "marry2" : 0,
    "marry1" : 0, "hotback" : 0, "cuba1" : 0, "cuba2" : 0,}
subs["*1-05-0"] = { "sidefill2" : 100, "sidefill1" : 100, "cycright" : 36,
    "upfill3" : 37, "upfill2" : 37, "upfill1" : 0, "b34" : 13, "b25" : 100,
    "side l" : 100, "b23" : 100, "b22" : 100, "desk2" : 31, "desk1" : 19,
    "phone" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100, "side r" : 82,
    "main 11" : 89, "main 10" : 100, "main 3" : 85, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 17,
    "main 9" : 100, "main 8" : 100, "cycleft" : 18, "edge" : 37,
    "b13" : 100, "god" : 100, "marry2" : 0, "marry1" : 0,}
subs["*1-06-0"] = { "sidefill2" : 100, "sidefill1" : 59, "cycright" : 53,
    "upfill3" : 0, "upfill2" : 0, "upfill1" : 0, "b34" : 100, "b25" : 100,
    "side l" : 100, "b23" : 100, "b22" : 49, "b32" : 80, "phone" : 0,
    "hotbox1" : 0, "upfill4" : 0, "b24" : 100, "desk2" : 78, "main 11" : 100,
    "main 10" : 100, "main 3" : 0, "main 2" : 100, "main 5" : 100,
    "main 4" : 0, "main 7" : 100, "hotbox2" : 100, "main 9" : 100,
    "main 8" : 100, "god" : 100, "cycleft" : 0, "edge" : 0, "b13" : 0,
    "rock" : 60, "marry2" : 100, "marry1" : 0, "side r" : 100,}
subs["*1-07-0"] = { "sidefill2" : 37, "sidefill1" : 37, "side l" : 49,
    "upfill3" : 11, "upfill2" : 23, "b34" : 28, "b25" : 64, "b24" : 100,
    "b23" : 100, "b22" : 82, "desk2" : 0, "desk1" : 0, "hotbox2" : 11,
    "hotbox1" : 0, "side r" : 36, "blue1" : 93, "main 11" : 37, "blue3" : 93,
    "blue2" : 93, "blue4" : 93, "main 10" : 37, "main 3" : 25, "main 2" : 37,
    "main 5" : 37, "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37,
    "edge" : 12, "god" : 100, "marry2" : 0, "marry1" : 37,}
subs["*1-08-00-left cafe"] = { "main 3" : 100, "edge" : 100,}
subs["*1-08-10-right cafe"] = { "b34" : 54, "b32" : 43, "main 9" : 0,
    "main 8" : 0, "cuba1" : 100, "cuba2" : 100,}
subs["*1-08-20-backdrop"] = { "upfill4" : 100, "upfill3" : 100,
    "upfill2" : 100, "upfill1" : 100,}
subs["*1-08-30-full"] = { "sidefill2" : 38, "sidefill1" : 38,
    "cycright" : 15, "upfill3" : 100, "main 10" : 38, "upfill1" : 100,
    "b34" : 54, "b25" : 100, "side l" : 38, "b23" : 100, "b22" : 100,
    "b32" : 43, "phone" : 31, "hotbox1" : 38, "upfill4" : 100, "b24" : 100,
    "desk2" : 30, "main 11" : 38, "upfill2" : 100, "main 3" : 38,
    "main 2" : 38, "main 5" : 38, "main 4" : 38, "main 7" : 38, "hotbox2" : 38,
    "main 9" : 38, "main 8" : 38, "cycleft" : 15, "edge" : 31, "god" : 100,
    "marry2" : 38, "marry1" : 38, "cuba1" : 100, "cuba2" : 100, "side r" : 38,}
subs["*1-09-0"] = { "red3" : 64, "red2" : 64, "red1" : 64, "upfill3" : 43,
    "upfill2" : 43, "red4" : 64, "b34" : 9, "b25" : 100, "b24" : 59,
    "b23" : 59, "b22" : 100, "desk2" : 16, "blue1" : 53, "main 11" : 28,
    "blue3" : 53, "blue2" : 53, "blue4" : 53, "main 10" : 28, "main 3" : 28,
    "main 2" : 100, "main 5" : 16, "main 4" : 16, "main 9" : 65,
    "main 8" : 74, "god" : 100, "marry2" : 9,}
subs["*1-10-0"] = { "sidefill2" : 34, "sidefill1" : 20, "cycright" : 18,
    "main 11" : 34, "main 10" : 34, "upfill1" : 9, "b34" : 34, "b25" : 34,
    "side l" : 34, "b23" : 34, "b22" : 16, "b32" : 27, "hotbox2" : 34,
    "upfill4" : 9, "b24" : 34, "desk2" : 26, "blue1" : 70, "blue3" : 70,
    "blue2" : 70, "blue4" : 70, "main 2" : 34, "main 5" : 34, "main 4" : 25,
    "main 7" : 34, "main 9" : 34, "main 8" : 34, "god" : 100, "rock" : 20,
    "marry2" : 34, "cuba1" : 5, "side r" : 34,}
subs["*2-01-0-dance"] = { "cycright" : 19, "upfill3" : 32, "upfill2" : 46,
    "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46, "b23" : 0,
    "desk1" : 0, "desk2" : 24, "upfill4" : 26, "side r" : 46, "main 11" : 46,
    "main 10" : 100, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0, "b13" : 0,
    "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0, "red4" : 100,
    "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0, "phone" : 0,
    "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 100,
    "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
    "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
subs["*2-01-01-solo"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 67, "main 11" : 0, "upfill2" : 1, "upfill1" : 67,
    "red4" : 100, "b34" : 0, "cycleft" : 55, "b23" : 100, "desk2" : 24,
    "hotbox2" : 78, "hotbox1" : 42, "cycright" : 55, "b24" : 100,
    "b32" : 43, "main 10" : 0, "main 3" : 0, "main 2" : 0, "main 5" : 0,
    "main 4" : 0, "main 7" : 100, "phone" : 0, "main 9" : 0, "main 8" : 0,
    "hotback" : 100, "god" : 100, "cuba1" : 0, "cuba2" : 0,}
subs["*2-01-1-after dance"] = { "cycright" : 19, "upfill3" : 32,
    "upfill2" : 46, "upfill1" : 26, "sidefill2" : 0, "b25" : 0, "side l" : 46,
    "b23" : 0, "desk1" : 0, "desk2" : 24, "upfill4" : 26, "side r" : 46,
    "main 11" : 46, "main 10" : 100, "god" : 100, "edge" : 0, "sidepost1" : 0,
    "sidepost2" : 0, "marry2" : 0, "marry1" : 0, "cuba1" : 0, "cuba2" : 0,
    "b13" : 0, "red3" : 100, "red2" : 100, "sidefill1" : 0, "b24" : 0,
    "red4" : 100, "b34" : 30, "cycleft" : 19, "b32" : 43, "b22" : 0,
    "phone" : 0, "hotbox1" : 42, "main 3" : 46, "main 2" : 46, "main 5" : 100,
    "main 4" : 46, "main 7" : 100, "hotbox2" : 78, "main 9" : 46,
    "main 8" : 46, "hotback" : 100, "rock" : 0, "red1" : 100,}
subs["*2-01-2-table"] = { "sidefill2" : 0, "main 11" : 0, "b25" : 0,
    "b22" : 100, "desk2" : 58, "phone" : 0, "main 3" : 80, "main 2" : 62,
    "main 5" : 34, "main 4" : 100, "main 7" : 10, "hotbox2" : 46,
    "main 9" : 64, "main 8" : 10, "edge" : 0, "b13" : 0, "rock" : 22,
    "marry2" : 0, "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
subs["*2-01-3-small table"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 62, "main 11" : 0, "main 10" : 0, "upfill1" : 62,
    "red4" : 100, "b25" : 5, "b22" : 100, "desk2" : 58, "desk1" : 52,
    "hotbox2" : 0, "sidefill2" : 0, "main 3" : 47, "main 2" : 0,
    "main 5" : 0, "main 4" : 0, "main 7" : 0, "phone" : 0, "main 9" : 11,
    "main 8" : 0, "god" : 100, "edge" : 0, "rock" : 0, "marry2" : 0,
    "marry1" : 0, "hotback" : 0, "cuba1" : 0, "cuba2" : 0,}
subs["*2-02-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 0,
    "main 11" : 5, "main 10" : 68, "upfill1" : 0, "b34" : 0, "b25" : 0,
    "side l" : 34, "b23" : 0, "b22" : 0, "b32" : 0, "desk1" : 0,
    "hotbox2" : 0, "upfill4" : 0, "b24" : 0, "desk2" : 0, "main 3" : 0,
    "main 2" : 5, "main 5" : 18, "main 4" : 60, "main 7" : 42, "main 9" : 68,
    "main 8" : 50, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "rock" : 0, "marry2" : 65, "hotback" : 0, "cuba1" : 0, "side r" : 34,}
subs["*2-03-00-open dance"] = { "sidefill2" : 33, "sidefill1" : 33,
    "upfill4" : 10, "upfill3" : 22, "main 10" : 61, "upfill1" : 14,
    "b25" : 16, "b24" : 19, "b23" : 28, "b22" : 50, "hotbox1" : 0,
    "main 11" : 28, "upfill2" : 61, "main 2" : 54, "main 5" : 20,
    "main 4" : 45, "main 7" : 0, "main 9" : 42, "main 8" : 34, "hotback" : 40,
    "sidepost1" : 31, "sidepost2" : 31, "marry2" : 0, "marry1" : 0,
    "cuba1" : 59,}
subs["*2-03-10-dialogue"] = { "sidefill2" : 34, "sidefill1" : 57,
    "upfill4" : 10, "upfill3" : 22, "main 10" : 48, "upfill1" : 14,
    "b25" : 16, "b24" : 19, "b23" : 64, "b22" : 62, "hotbox1" : 0,
    "main 11" : 40, "upfill2" : 61, "main 2" : 54, "main 5" : 20,
    "main 4" : 45, "main 7" : 0, "main 9" : 73, "main 8" : 22, "hotback" : 40,
    "sidepost1" : 31, "sidepost2" : 31, "marry2" : 0, "marry1" : 0,
    "cuba1" : 59, "b13" : 60,}
subs["*2-03-20-luck"] = { "sidefill2" : 33, "sidefill1" : 33,
    "upfill4" : 10, "upfill3" : 22, "main 10" : 48, "upfill1" : 14,
    "b25" : 16, "b24" : 19, "b23" : 64, "b22" : 50, "hotbox1" : 0,
    "main 11" : 40, "upfill2" : 61, "main 2" : 54, "main 5" : 20,
    "main 4" : 45, "main 7" : 0, "main 9" : 84, "main 8" : 45, "hotback" : 40,
    "sidepost1" : 31, "sidepost2" : 31, "marry2" : 0, "marry1" : 0,
    "cuba1" : 59,}
subs["*2-04-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 18,
    "main 11" : 5, "main 10" : 5, "upfill1" : 70, "b34" : 34, "b25" : 71,
    "side l" : 34, "b23" : 67, "b22" : 50, "b32" : 57, "desk1" : 24,
    "hotbox2" : 59, "upfill4" : 70, "b24" : 67, "desk2" : 26, "b13" : 39,
    "main 3" : 45, "main 2" : 5, "main 5" : 56, "main 4" : 0, "main 7" : 5,
    "main 9" : 5, "main 8" : 5, "rock" : 20, "edge" : 0, "sidepost1" : 0,
    "sidepost2" : 0, "god" : 100, "marry2" : 50, "cuba1" : 0, "side r" : 34,}
subs["*2-05-0"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 55, "b34" : 0, "b25" : 0, "b24" : 68,
    "b23" : 68, "desk1" : 3, "desk2" : 92, "b22" : 68, "hotbox2" : 61,
    "hotbox1" : 0, "cycright" : 66, "b32" : 36, "upfill3" : 37, "upfill2" : 66,
    "main 3" : 45, "main 2" : 0, "main 5" : 70, "main 4" : 50, "main 7" : 55,
    "main 9" : 55, "main 8" : 55, "rock" : 26, "marry2" : 64, "marry1" : 11,
    "cuba1" : 0, "cuba2" : 52,}
subs["*2-05-1-dream"] = { "sidefill2" : 0, "cycright" : 0, "main 11" : 7,
    "upfill2" : 0, "upfill1" : 0, "b34" : 0, "cycleft" : 0, "b23" : 0,
    "desk1" : 0, "desk2" : 42, "b22" : 0, "hotbox2" : 0, "hotbox1" : 0,
    "upfill4" : 0, "b24" : 0, "b32" : 0, "upfill3" : 0, "main 10" : 0,
    "main 3" : 0, "main 2" : 0, "main 5" : 0, "main 4" : 0, "main 7" : 0,
    "phone" : 0, "main 9" : 0, "main 8" : 0, "god" : 100, "edge" : 0, 'dream' : 100,
    "b13" : 0, "rock" : 0, "marry2" : 0, "marry1" : 0, "cuba2" : 0,}
subs["*2-05-2-boat"] = { "sidefill2" : 43, "cycright" : 55, "main 11" : 84,
    "upfill2" : 55, "god" : 100, "b24" : 100, "b23" : 100, "desk1" : 44,
    "b32" : 52, "b22" : 100, "hotbox2" : 95, "hotbox1" : 21, "desk2" : 84,
    "upfill3" : 31, "main 10" : 84, "main 3" : 72, "main 5" : 83,
    "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
    "rock" : 43, "marry2" : 100, "marry1" : 75, "cuba2" : 65,}
subs["*2-06-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 100,
    "main 11" : 55, "main 10" : 55, "upfill1" : 48, "b34" : 30, "b25" : 0,
    "side l" : 30, "b23" : 100, "b22" : 14, "b32" : 23, "main 4" : 0,
    "hotbox2" : 43, "hotbox1" : 49, "upfill4" : 48, "b24" : 100,
    "desk2" : 23, "patio2" : 0, "main 3" : 0, "main 2" : 30, "main 5" : 0,
    "patio1" : 0, "main 7" : 30, "phone" : 0, "main 9" : 30, "main 8" : 0,
    "rock" : 17, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0, "god" : 100,
    "marry2" : 34, "marry1" : 69, "cuba1" : 0, "cuba2" : 0, "side r" : 30,}
subs["*2-07-0"] = { "sidefill2" : 100, "sidefill1" : 83, "cycright" : 41,
    "upfill3" : 69, "upfill2" : 100, "upfill1" : 56, "b34" : 100,
    "b25" : 100, "side l" : 100, "b23" : 100, "b22" : 100, "desk2" : 78,
    "phone" : 62, "hotbox1" : 14, "upfill4" : 56, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 83, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 5,
    "main 9" : 100, "main 8" : 100, "rock" : 0, "cycleft" : 41, "edge" : 63,
    "god" : 100, "marry2" : 100, "marry1" : 100,}
subs["*curtain"] = { "sidefill2" : 73, "sidefill1" : 73, "cycright" : 30,
    "upfill3" : 50, "upfill2" : 100, "upfill1" : 41, "b34" : 73,
    "b25" : 73, "side l" : 73, "b22" : 73, "desk2" : 57,
    "phone" : 58, "hotbox1" : 0, "upfill4" : 41, "b24" : 73, "side r" : 73,
    "main 11" : 73, "main 10" : 73, "main 3" : 73, "main 2" : 73,
    "main 5" : 73, "main 4" : 73, "main 7" : 73, "hotbox2" : 73,
    "main 9" : 73, "main 8" : 73, "cycleft" : 30, "edge" : 58,
    "marry2" : 73, "marry1" : 73,}
subs["*spare"] = {}
subs["*1-08-00-left cafe"] = { "cafe1" : 100, "main 3" : 100,
    "edge" : 100, "cuba1" : 0,}
subs["*1-08-10-right cafe"] = { "b34" : 54, "cuba2" : 100, "main 9" : 0,
    "main 8" : 0, "cafe2" : 100, "cuba1" : 100, "b32" : 43,}
subs["*1-01-0"] = { "sidefill2" : 100, "sidefill1" : 100, "cycright" : 41,
    "upfill3" : 60, "upfill2" : 91, "upfill1" : 56, "b34" : 100,
    "b25" : 100, "side l" : 100, "b22" : 100, "desk2" : 78, "phone" : 80,
    "hotbox1" : 43, "upfill4" : 68, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 100, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 91,
    "main 9" : 100, "main 8" : 100, "cycleft" : 41, "edge" : 80,
    "god" : 100, "marry2" : 100, "marry1" : 100,}
subs["*curtain"] = { "sidefill2" : 23, "sidefill1" : 23, "cycright" : 0,
    "upfill3" : 18, "upfill2" : 68, "upfill1" : 9, "b34" : 73, 
    "b25" : 73, "side l" : 73, "b22" : 73, "desk2" : 57, "phone" : 58,
    "hotbox1" : 0, "upfill4" : 9, "b24" : 73, "side r" : 73, "main 11" : 73,
    "main 10" : 73, "main 3" : 73, "main 2" : 73, "main 5" : 73,
    "main 4" : 73, "main 7" : 73, "hotbox2" : 73, "main 9" : 73,
    "main 8" : 73, "cycleft" : 0, "edge" : 58, "god" : 100, "marry2" : 73,
    "marry1" : 73,}
subs["*1-01-9 end conversations"] = { "sidefill2" : 63, "sidefill1" : 26,
    "upfill4" : 29, "upfill3" : 43, "upfill2" : 63, "upfill1" : 29,
    "b34" : 63, "b25" : 63, "side l" : 63, "b23" : 12, "b22" : 63,
    "desk2" : 12, "phone" : 50, "hotbox1" : 37, "cycright" : 25,
    "b24" : 42, "side r" : 63, "main 11" : 63, "main 10" : 63, "main 3" : 26,
    "main 2" : 63, "main 5" : 100, "main 4" : 63, "main 7" : 63,
    "hotbox2" : 63, "main 9" : 63, "main 8" : 63, "cycleft" : 25,
    "edge" : 13, "god" : 100, "marry2" : 63, "marry1" : 100, "cuba1" : 63,
    "cuba2" : 42,}
subs["*1-02-0"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 100, "upfill1" : 0, "b34" : 0, "b25" : 0,
    "b24" : 100, "b23" : 100, "desk1" : 53, "desk2" : 65, "b22" : 100,
    "hotbox2" : 100, "hotbox1" : 25, "cycright" : 63, "b32" : 14,
    "upfill3" : 55, "upfill2" : 6, "main 3" : 57, "main 2" : 0, "main 5" : 70,
    "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
    "cycleft" : 0, "hotback" : 0, "rock" : 23, "marry2" : 47, "marry1" : 61,
    "dream" : 0, "cuba1" : 0, "cuba2" : 78,}
subs["*1-02-0"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 100, "upfill1" : 0, "b34" : 0, "b25" : 0,
    "b24" : 100, "b23" : 100, "desk1" : 53, "desk2" : 65, "b22" : 100,
    "hotbox2" : 100, "hotbox1" : 25, "cycright" : 63, "b32" : 14,
    "upfill3" : 55, "upfill2" : 6, "main 3" : 57, "main 2" : 0, "main 5" : 70,
    "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
    "cycleft" : 0, "hotback" : 0, "rock" : 23, "marry2" : 47, "marry1" : 61,
    "dream" : 0, "cuba1" : 0, "cuba2" : 78,}
subs["*1-02-0"] = { "sidefill2" : 51, "sidefill1" : 0, "upfill4" : 0,
    "main 11" : 100, "main 10" : 100, "upfill1" : 0, "b34" : 0, "b25" : 0,
    "b24" : 100, "b23" : 100, "desk1" : 53, "desk2" : 65, "b22" : 100,
    "hotbox2" : 100, "hotbox1" : 25, "cycright" : 63, "b32" : 14,
    "upfill3" : 55, "upfill2" : 6, "main 3" : 0, "main 2" : 0, "main 5" : 70,
    "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
    "cycleft" : 0, "hotback" : 0, "rock" : 23, "marry2" : 47, "marry1" : 61,
    "dream" : 0, "cuba1" : 0, "cuba2" : 78,}
subs["*1-02-1 desk solo"] = { "sidefill2" : 51, "cycright" : 37,
    "upfill3" : 0, "upfill2" : 0, "main 8" : 22, "cycleft" : 0, "b23" : 100,
    "desk1" : 53, "desk2" : 89, "b22" : 100, "hotbox2" : 7, "hotbox1" : 25,
    "b24" : 22, "b32" : 0, "blue1" : 33, "main 11" : 22, "blue3" : 33,
    "blue2" : 33, "blue4" : 33, "main 10" : 22, "main 3" : 9, "main 5" : 0,
    "main 4" : 22, "main 7" : 100, "main 9" : 22, "god" : 100, "rock" : 14,
    "marry2" : 22, "marry1" : 61, "cuba2" : 0,}
subs["*1-04-02 solo ada"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 26, "main 11" : 46, "main 10" : 100, "upfill1" : 26,
    "red4" : 100, "b34" : 12, "cycleft" : 19, "b23" : 67, "desk2" : 24,
    "hotbox2" : 45, "hotbox1" : 46, "cycright" : 19, "b24" : 67,
    "b32" : 2, "blue1" : 33, "blue3" : 33, "blue2" : 33, "blue4" : 33,
    "main 3" : 13, "main 2" : 46, "main 4" : 100, "main 7" : 100,
    "main 9" : 100, "main 8" : 29, "edge" : 9, "hotback" : 100, "god" : 100,}
subs["*1-04-20-table"] = { "red3" : 0, "sidefill2" : 0, "red1" : 100,
    "main 11" : 0, "red2" : 0, "b25" : 0, "b22" : 100, "desk2" : 58,
    "hotbox2" : 46, "main 3" : 80, "main 2" : 62, "main 5" : 34,
    "main 4" : 100, "main 7" : 10, "phone" : 0, "main 9" : 64, "main 8" : 10,
    "red4" : 0, "edge" : 0, "b13" : 0, "rock" : 22, "marry2" : 0,
    "marry1" : 0, "hotback" : 0, "cuba1" : 22, "cuba2" : 0,}
subs["*1-04-30-small table"] = { "red3" : 0, "red2" : 0, "red1" : 100,
    "upfill4" : 62, "main 11" : 0, "main 10" : 0, "upfill1" : 62,
    "red4" : 0, "b25" : 0, "b22" : 100, "desk2" : 34, "desk1" : 50,
    "hotbox2" : 0, "sidefill2" : 0, "main 3" : 0, "main 2" : 0, "main 5" : 0,
    "main 4" : 0, "main 7" : 0, "phone" : 0, "main 9" : 0, "main 8" : 0,
    "god" : 100, "edge" : 0, "rock" : 0, "marry2" : 0, "marry1" : 0,
    "hotback" : 0, "cuba1" : 0, "cuba2" : 0,}
subs["*1-07-0"] = { "sidefill2" : 37, "sidefill1" : 37, "side l" : 49,
    "upfill3" : 6, "upfill2" : 18, "b34" : 28, "b25" : 64, "b24" : 100,
    "b23" : 100, "b22" : 82, "desk2" : 0, "desk1" : 0, "hotbox2" : 11,
    "hotbox1" : 0, "side r" : 36, "blue1" : 93, "main 11" : 37, "blue3" : 93,
    "blue2" : 93, "blue4" : 93, "main 10" : 37, "main 3" : 25, "main 2" : 37,
    "main 5" : 37, "main 4" : 37, "main 7" : 37, "main 9" : 37, "main 8" : 37,
    "edge" : 12, "god" : 100, "marry2" : 0, "marry1" : 37,}
subs["*1-08-00-left cafe"] = { "b22" : 40, "hotbox1" : 0, "edge" : 41,
    "cafe1" : 71, "main 3" : 1, "cuba1" : 0,}
subs["*1-08-10-right cafe"] = { "b34" : 31, "cuba2" : 76, "main 9" : 0,
    "main 8" : 0, "cafe2" : 100, "cuba1" : 53, "b32" : 10,}
subs["*1-08-30-full"] = { "cycright" : 15, "upfill3" : 100, "main 10" : 38,
    "upfill1" : 100, "sidefill2" : 38, "b25" : 100, "side l" : 38,
    "b23" : 100, "b22" : 100, "desk2" : 30, "oran3" : 82, "upfill4" : 100,
    "side r" : 38, "main 11" : 38, "oran1" : 82, "upfill2" : 100,
    "gree2" : 15, "cafe1" : 100, "cafe2" : 100, "gree1" : 15, "gree4" : 15,
    "marry2" : 38, "marry1" : 38, "cuba1" : 100, "cuba2" : 100, "red3" : 77,
    "red2" : 77, "sidefill1" : 38, "b24" : 100, "god" : 100, "red4" : 95,
    "b34" : 54, "cycleft" : 15, "b32" : 43, "phone" : 31, "hotbox1" : 38,
    "blue1" : 15, "oran2" : 82, "blue3" : 15, "blue2" : 15, "blue4" : 15,
    "oran4" : 82, "main 3" : 38, "main 2" : 38, "main 5" : 38, "main 4" : 38,
    "main 7" : 38, "hotbox2" : 38, "main 9" : 38, "main 8" : 38,
    "edge" : 31, "gree3" : 15, "red1" : 77,}
subs["*1-09-0"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 30, "upfill3" : 43, "upfill2" : 43, "upfill1" : 30,
    "red4" : 100, "b34" : 9, "main 8" : 47, "b25" : 62, "b24" : 21,
    "b23" : 21, "b22" : 32, "desk2" : 16, "blue1" : 92, "oran2" : 31,
    "oran3" : 31, "main 11" : 37, "oran1" : 31, "blue2" : 92, "blue3" : 92,
    "main 10" : 43, "main 3" : 0, "main 2" : 61, "main 5" : 64, "main 4" : 0,
    "main 7" : 0, "gree2" : 53, "cafe1" : 37, "cafe2" : 37, "gree1" : 53,
    "gree4" : 53, "blue4" : 92, "god" : 100, "main 9" : 38, "gree3" : 53,
    "marry2" : 9, "oran4" : 31,}
subs["*1-09-0"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 30, "upfill3" : 43, "upfill2" : 43, "upfill1" : 30,
    "red4" : 100, "b34" : 9, "main 8" : 47, "b25" : 62, "b24" : 21,
    "b23" : 21, "b22" : 32, "desk2" : 16, "blue1" : 92, "oran2" : 31,
    "oran3" : 31, "main 11" : 37, "oran1" : 31, "blue2" : 92, "blue3" : 92,
    "main 10" : 43, "main 3" : 0, "main 2" : 61, "main 5" : 64, "main 4" : 0,
    "main 7" : 0, "gree2" : 53, "cafe1" : 37, "cafe2" : 37, "gree1" : 53,
    "gree4" : 53, "blue4" : 92, "god" : 100, "main 9" : 38, "gree3" : 53,
    "marry2" : 9, "oran4" : 31,}
subs["*1-10-0"] = { "sidefill2" : 23, "sidefill1" : 6, "cycright" : 0,
    "main 11" : 34, "main 10" : 34, "upfill1" : 0, "red4" : 0, "b34" : 34,
    "b25" : 34, "side l" : 23, "b23" : 20, "b22" : 44, "b32" : 27,
    "hotbox2" : 34, "upfill4" : 0, "b24" : 34, "desk2" : 11, "blue1" : 84,
    "blue3" : 0, "blue2" : 54, "blue4" : 0, "main 2" : 34, "main 5" : 34,
    "main 4" : 25, "main 7" : 34, "main 9" : 34, "main 8" : 34, "god" : 100,
    "cycleft" : 0, "rock" : 3, "marry2" : 0, "cuba1" : 5, "side r" : 14,}
subs["*2-01-1-darker dance"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 26, "upfill3" : 32, "upfill2" : 46, "upfill1" : 26,
    "red4" : 100, "b34" : 30, "cycleft" : 19, "desk2" : 24, "hotbox2" : 78,
    "hotbox1" : 42, "cycright" : 19, "b32" : 43, "main 11" : 46,
    "main 10" : 100, "main 3" : 46, "main 2" : 46, "main 5" : 100,
    "main 4" : 46, "main 7" : 100, "main 9" : 46, "main 8" : 46,
    "hotback" : 100, "god" : 100,}
subs["*2-01-1-darker dance"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 26, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "red4" : 100, "b34" : 9, "cycleft" : 19, "desk2" : 10, "hotbox2" : 52,
    "hotbox1" : 42, "cycright" : 19, "b32" : 4, "main 11" : 0, "main 10" : 0,
    "main 3" : 0, "main 2" : 0, "main 5" : 0, "main 4" : 0, "main 7" : 0,
    "main 9" : 0, "main 8" : 0, "god" : 100, "hotback" : 100, "rock" : 0,
    "xmas" : 0,}
subs["*2-01-1-darker dance"] = { "red3" : 100, "red2" : 100, "red1" : 100,
    "upfill4" : 26, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "red4" : 100, "b34" : 9, "cycleft" : 19, "b23" : 93, "desk2" : 10,
    "hotbox2" : 52, "hotbox1" : 42, "cycright" : 19, "b24" : 93,
    "b32" : 4, "main 11" : 0, "main 10" : 0, "main 3" : 0, "main 2" : 0,
    "main 5" : 0, "main 4" : 0, "main 7" : 0, "main 9" : 0, "main 8" : 0,
    "god" : 100, "hotback" : 100, "rock" : 0, "xmas" : 0,}
subs["*2-01-2-table"] = { "sidefill2" : 0, "red1" : 100, "main 11" : 0,
    "b25" : 0, "b22" : 100, "desk2" : 58, "hotbox2" : 46, "main 3" : 80,
    "main 2" : 62, "main 5" : 34, "main 4" : 100, "main 7" : 10,
    "phone" : 0, "main 9" : 64, "main 8" : 10, "edge" : 0, "b13" : 0,
    "rock" : 22, "marry2" : 0, "marry1" : 0, "hotback" : 0, "cuba1" : 22,
    "cuba2" : 0,}
subs["*2-01-2-table"] = { "sidefill2" : 0, "red1" : 100, "upfill4" : 76,
    "main 11" : 0, "upfill2" : 76, "upfill1" : 76, "b25" : 0, "b22" : 100,
    "desk2" : 58, "hotbox2" : 46, "upfill3" : 76, "main 3" : 80,
    "main 2" : 62, "main 5" : 34, "main 4" : 100, "main 7" : 10,
    "phone" : 0, "main 9" : 64, "main 8" : 10, "edge" : 0, "b13" : 0,
    "rock" : 22, "marry2" : 0, "marry1" : 0, "hotback" : 0, "cuba1" : 22,
    "cuba2" : 0,}
subs["*2-01-3-small table"] = { "red3" : 0, "red2" : 0, "red1" : 100,
    "upfill4" : 62, "main 11" : 0, "main 10" : 0, "upfill1" : 62,
    "red4" : 0, "b25" : 5, "b22" : 56, "desk2" : 58, "desk1" : 47,
    "hotbox2" : 0, "sidefill2" : 0, "main 3" : 18, "main 2" : 0,
    "main 5" : 0, "main 4" : 0, "main 7" : 0, "phone" : 0, "main 9" : 11,
    "main 8" : 0, "god" : 100, "edge" : 0, "rock" : 0, "marry2" : 0,
    "marry1" : 0, "hotback" : 0, "cuba1" : 0, "cuba2" : 0,}
subs["*2-02-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 0,
    "main 11" : 0, "main 10" : 53, "upfill1" : 0, "b34" : 0, "b25" : 0,
    "side l" : 34, "b23" : 76, "b22" : 0, "b32" : 0, "desk1" : 0,
    "hotbox2" : 0, "upfill4" : 0, "b24" : 30, "desk2" : 0, "main 3" : 0,
    "main 2" : 5, "main 5" : 18, "main 4" : 24, "main 7" : 42, "main 9" : 60,
    "main 8" : 36, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "rock" : 0, "marry2" : 38, "hotback" : 0, "cuba1" : 0, "side r" : 34,}
subs["*2-02-0"] = { "sidefill2" : 0, "sidefill1" : 0, "cycright" : 0,
    "main 11" : 0, "main 10" : 53, "upfill1" : 0, "b34" : 0, "b25" : 0,
    "side l" : 34, "b23" : 76, "b22" : 0, "b32" : 0, "desk1" : 0,
    "hotbox2" : 0, "upfill4" : 0, "b24" : 52, "desk2" : 0, "main 3" : 0,
    "main 2" : 5, "main 5" : 18, "main 4" : 24, "main 7" : 42, "main 9" : 60,
    "main 8" : 36, "god" : 100, "edge" : 0, "sidepost1" : 0, "sidepost2" : 0,
    "rock" : 0, "marry2" : 38, "hotback" : 0, "cuba1" : 0, "side r" : 34,}
subs["*2-03-00-open dance"] = { "red3" : 75, "sidefill2" : 0,
    "sidefill1" : 0, "upfill4" : 10, "upfill3" : 22, "main 10" : 40,
    "upfill1" : 14, "red2" : 75, "b25" : 0, "b24" : 0, "b23" : 0,
    "b22" : 11, "hotbox1" : 0, "blue1" : 70, "main 11" : 28, "blue3" : 70,
    "blue2" : 70, "blue4" : 92, "upfill2" : 61, "red4" : 97, "main 2" : 60,
    "main 5" : 20, "main 4" : 45, "main 7" : 0, "main 9" : 42, "main 8" : 26,
    "gree1" : 75, "gree4" : 75, "gree2" : 75, "hotback" : 40, "sidepost1" : 31,
    "sidepost2" : 31, "gree3" : 75, "marry2" : 0, "marry1" : 0, "red1" : 75,
    "cuba1" : 20,}
subs["*2-03-00-open dance"] = { "red3" : 75, "sidefill2" : 0,
    "sidefill1" : 0, "upfill4" : 17, "upfill3" : 26, "main 10" : 40,
    "upfill1" : 27, "red2" : 75, "b25" : 0, "b24" : 0, "b23" : 0,
    "b22" : 11, "hotbox1" : 0, "blue1" : 70, "main 11" : 28, "blue3" : 70,
    "blue2" : 70, "blue4" : 92, "upfill2" : 31, "red4" : 97, "main 2" : 60,
    "main 5" : 20, "main 4" : 45, "main 7" : 0, "main 9" : 42, "main 8" : 26,
    "gree1" : 75, "gree4" : 75, "gree2" : 75, "hotback" : 40, "sidepost1" : 31,
    "sidepost2" : 31, "gree3" : 75, "marry2" : 0, "marry1" : 0, "red1" : 75,
    "cuba1" : 20,}
subs["*2-03-20-luck"] = { "sidefill2" : 0, "sidefill1" : 0, "upfill4" : 10,
    "upfill3" : 22, "main 10" : 0, "upfill1" : 14, "b25" : 93, "b24" : 100,
    "b23" : 100, "b22" : 43, "hotbox1" : 0, "main 11" : 0, "upfill2" : 61,
    "main 3" : 0, "main 2" : 0, "main 5" : 0, "main 4" : 0, "main 7" : 100,
    "main 9" : 0, "main 8" : 57, "edge" : 0, "sidepost1" : 31, "sidepost2" : 31,
    "marry2" : 0, "marry1" : 0, "hotback" : 40, "cuba1" : 5,}
subs["*2-05-0"] = { "sidefill2" : 51, "cycright" : 63, "main 11" : 100,
    "main 10" : 100, "god" : 100, "b24" : 100, "b23" : 100, "desk1" : 53,
    "desk2" : 65, "b22" : 100, "hotbox2" : 100, "hotbox1" : 25, "b32" : 14,
    "upfill3" : 55, "upfill2" : 6, "main 5" : 70, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "rock" : 23,
    "marry2" : 47, "marry1" : 61, "cuba2" : 78,}
subs["*2-05-0"] = { "sidefill2" : 25, "cycright" : 0, "main 11" : 100,
    "main 10" : 100, "rock" : 23, "b24" : 100, "b23" : 100, "desk1" : 53,
    "desk2" : 65, "b22" : 100, "hotbox2" : 100, "hotbox1" : 25, "b32" : 14,
    "upfill3" : 34, "upfill2" : 6, "main 5" : 70, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "god" : 100,
    "marry2" : 47, "marry1" : 61, "cuba2" : 9,}
subs["*2-05-1-dream"] = { "sidefill2" : 0, "cycright" : 0, "main 11" : 7,
    "upfill2" : 16, "upfill1" : 0, "b34" : 0, "cycleft" : 0, "b23" : 0,
    "desk1" : 0, "desk2" : 42, "b22" : 0, "hotbox2" : 0, "hotbox1" : 0,
    "upfill4" : 0, "b24" : 0, "b32" : 0, "upfill3" : 0, "main 10" : 0,
    "main 3" : 0, "main 2" : 0, "main 5" : 0, "main 4" : 0, "main 7" : 0,
    "phone" : 0, "main 9" : 0, "main 8" : 0, "god" : 100, "edge" : 0,
    "b13" : 0, "rock" : 0, "marry2" : 0, "marry1" : 0, "dream" : 100,
    "cuba2" : 0,}
subs["*2-07-0"] = { "sidefill2" : 100, "sidefill1" : 83, "cycright" : 41,
    "upfill3" : 69, "upfill2" : 100, "upfill1" : 56, "b34" : 100,
    "b25" : 100, "side l" : 100, "b23" : 100, "b22" : 100, "desk2" : 78,
    "phone" : 62, "hotbox1" : 14, "upfill4" : 56, "b24" : 100, "side r" : 100,
    "main 11" : 100, "main 10" : 100, "main 3" : 83, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "hotbox2" : 5,
    "main 9" : 100, "main 8" : 100, "rock" : 0, "cycleft" : 41, "edge" : 63,
    "god" : 100, "marry2" : 100, "marry1" : 100, "xmas" : 100,}
