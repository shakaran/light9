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
subs={}

subs[('col blue', 'blue')]={ 'blue1': 100, 'blue2': 100, 'blue3': 100, 'blue4': 100, }

subs[('col gree', 'green')]={ 'gree1': 100, 'gree2': 100, 'gree3': 100, 'gree4': 100, }

subs[('col oran', '#EEEE99')]={ 'oran1': 100, 'oran2': 100, 'oran3': 100, 'oran4': 100, }

subs[('col red', 'red')]={ 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, }

subs[('house', 'black')]={ 'house': 100, }

subs[('*1-01-0', 'white')]={ 'b22': 100, 'b24': 100, 'b25': 100, 'b34': 100, 'cycleft': 41, 'cycright': 41, 'desk2': 78, 'edge': 80, 'hotbox1': 43, 'hotbox2': 91, 'main 10': 100, 'main 11': 100, 'main 2': 100, 'main 3': 100, 'main 4': 100, 'main 5': 100, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'marry1': 100, 'marry2': 100, 'side l': 100, 'side r': 100, 'sidefill1': 100, 'sidefill2': 100, 'upfill1': 56, 'upfill2': 91, 'upfill3': 60, 'upfill4': 68, }

subs['*1-01-9 end conversations']={ 'b22': 63, 'b23': 12, 'b24': 42, 'b25': 63, 'b34': 63, 'cuba1': 63, 'cuba2': 42, 'cycleft': 25, 'cycright': 25, 'desk2': 12, 'edge': 13, 'hotbox1': 37, 'hotbox2': 63, 'main 10': 63, 'main 11': 63, 'main 2': 63, 'main 3': 26, 'main 4': 63, 'main 5': 100, 'main 7': 63, 'main 8': 63, 'main 9': 63, 'marry1': 100, 'marry2': 63, 'side l': 63, 'side r': 63, 'sidefill1': 26, 'sidefill2': 63, 'upfill1': 29, 'upfill2': 63, 'upfill3': 43, 'upfill4': 29, }

subs[('*1-02-0', 'white')]={ 'b22': 100, 'b23': 100, 'b24': 100, 'b32': 14, 'cuba2': 38, 'cycright': 63, 'desk1': 53, 'desk2': 65, 'hotbox1': 25, 'hotbox2': 100, 'main 10': 100, 'main 11': 100, 'main 4': 100, 'main 5': 70, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'marry1': 61, 'marry2': 47, 'rock': 23, 'sidefill2': 51, 'upfill2': 6, 'upfill3': 55, }

subs['*1-02-1 desk solo']={ 'b22': 100, 'b23': 100, 'b24': 22, 'cycright': 37, 'desk1': 53, 'desk2': 89, 'hotbox1': 25, 'hotbox2': 7, 'main 10': 22, 'main 11': 22, 'main 3': 9, 'main 4': 22, 'main 7': 100, 'main 8': 22, 'main 9': 22, 'marry1': 61, 'marry2': 22, 'rock': 14, }

subs[('*1-03-0', 'white')]={ 'phone': 100, 'upfill2':50, 'upfill3':50, }

subs[('*1-04-00-dance', 'white')]={ 'b32': 43, 'b34': 30, 'cycleft': 19, 'cycright': 19, 'desk2': 24, 'hotback': 100, 'hotbox1': 42, 'hotbox2': 78, 'main 10': 100, 'main 11': 46, 'main 2': 46, 'main 3': 46, 'main 4': 46, 'main 5': 100, 'main 7': 100, 'main 8': 46, 'main 9': 46, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 26, 'upfill2': 46, 'upfill3': 32, 'upfill4': 26, }

subs['*1-04-01 dark tables']={ 'b23': 67, 'b24': 67, 'b32': 2, 'b34': 12, 'blue1': 33, 'blue2': 33, 'blue3': 33, 'blue4': 33, 'cycleft': 19, 'cycright': 19, 'desk2': 24, 'edge': 9, 'hotback': 100, 'hotbox1': 46, 'hotbox2': 45, 'main 10': 100, 'main 11': 46, 'main 2': 46, 'main 3': 13, 'main 4': 100, 'main 7': 100, 'main 8': 29, 'main 9': 100, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 26, 'upfill4': 26, }

subs['*1-04-02 solo ada']={ 'b23': 62, 'b24': 100, 'b32': 2, 'b34': 12, 'blue1': 33, 'blue2': 33, 'blue3': 33, 'blue4': 33, 'cycleft': 19, 'cycright': 19, 'desk2': 24, 'hotback': 100, 'hotbox1': 32, 'hotbox2': 24, 'main 10': 11, 'main 11': 2, 'main 2': 13, 'main 4': 100, 'main 7': 100, 'main 9': 61, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 26, 'upfill4': 26, }

subs['*1-04-10-after dance']={ 'b32': 43, 'b34': 30, 'cycleft': 19, 'cycright': 19, 'desk2': 24, 'hotback': 100, 'hotbox1': 42, 'hotbox2': 78, 'main 10': 100, 'main 11': 46, 'main 2': 46, 'main 3': 46, 'main 4': 46, 'main 5': 100, 'main 7': 100, 'main 8': 46, 'main 9': 46, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 26, 'upfill2': 46, 'upfill3': 32, 'upfill4': 26, }

subs['*1-04-20-table']={ 'b22': 100, 'cuba1': 22, 'desk2': 58, 'hotbox2': 46, 'main 2': 62, 'main 3': 80, 'main 4': 100, 'main 5': 34, 'main 7': 10, 'main 8': 10, 'main 9': 64, 'red1': 100, 'rock': 22, }

subs['*1-04-30-small table']={ 'b22': 100, 'desk1': 50, 'desk2': 34, 'red1': 100, 'upfill1': 62, 'upfill4': 62, }

subs[('*1-05-0', 'white')]={ 'b13': 100, 'b22': 100, 'b23': 100, 'b24': 100, 'b25': 100, 'b34': 13, 'cycleft': 18, 'cycright': 36, 'desk1': 19, 'desk2': 31, 'edge': 37, 'hotbox2': 17, 'main 10': 100, 'main 11': 89, 'main 2': 100, 'main 3': 85, 'main 4': 100, 'main 5': 100, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'side l': 100, 'side r': 82, 'sidefill1': 100, 'sidefill2': 100, 'upfill2': 37, 'upfill3': 37, }

subs[('*1-06-0', 'white')]={ 'b22': 49, 'b23': 100, 'b24': 100, 'b25': 100, 'b32': 80, 'b34': 100, 'cycright': 53, 'desk2': 78, 'hotbox2': 100, 'main 10': 100, 'main 11': 100, 'main 2': 100, 'main 5': 100, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'marry2': 100, 'rock': 60, 'side l': 100, 'side r': 100, 'sidefill1': 59, 'sidefill2': 100, }

subs[('*1-07-0', 'white')]={ 'b22': 82, 'b23': 100, 'b24': 100, 'b25': 64, 'b34': 28, 'blue1': 93, 'blue2': 93, 'blue3': 93, 'blue4': 93, 'edge': 12, 'hotbox2': 11, 'main 10': 37, 'main 11': 37, 'main 2': 37, 'main 3': 25, 'main 4': 37, 'main 5': 37, 'main 7': 37, 'main 8': 37, 'main 9': 37, 'marry1': 37, 'side l': 49, 'side r': 36, 'sidefill1': 37, 'sidefill2': 37, 'upfill2': 18, 'upfill3': 6, }

subs[('*1-08-00-left cafe', 'white')]={ 'b22': 40, 'cafe1': 71, 'edge': 41, }

subs['*1-08-10-right cafe']={ 'b32': 10, 'b34': 31, 'cafe2': 100, 'cuba1': 53, 'cuba2': 76, }

subs['*1-08-10-centerwalk']={ 'b23': 100, 'b24': 100, }

subs['*1-08-10-rightwalk']={ 'b25': 100, }

subs['*1-08-20-backdrop']={ 'upfill1': 100, 'upfill2': 100, 'upfill3': 100, 'upfill4': 100, }

subs['*1-08-30-full']={ 'b22': 100, 'b23': 100, 'b24': 100, 'b25': 100, 'b32': 23, 'b34': 24, 'blue1': 15, 'blue2': 15, 'blue3': 15, 'blue4': 15, 'cafe1': 100, 'cafe2': 50, 'cycleft': 15, 'cycright': 15, 'desk2': 30, 'edge': 31, 'gree1': 15, 'gree2': 15, 'gree3': 15, 'gree4': 15, 'hotbox1': 38, 'hotbox2': 38, 'main 10': 38, 'main 11': 38, 'main 2': 38, 'main 3': 38, 'main 4': 38, 'main 5': 38, 'main 7': 38, 'main 8': 38, 'main 9': 38, 'marry1': 38, 'marry2': 38, 'oran1': 82, 'oran2': 82, 'oran3': 82, 'oran4': 82, 'phone': 31, 'red1': 77, 'red2': 77, 'red3': 77, 'red4': 95, 'side l': 38, 'side r': 38, 'sidefill1': 38, 'sidefill2': 38, 'upfill1': 100, 'upfill2': 100, 'upfill3': 100, 'upfill4': 100, }

subs[('*1-09-0', 'white')]={ 'b22': 32, 'b23': 21, 'b24': 21, 'b25': 62, 'b34': 9, 'blue1': 92, 'blue2': 92, 'blue3': 92, 'blue4': 92, 'cafe1': 37, 'cafe2': 37, 'desk2': 16, 'gree1': 53, 'gree2': 53, 'gree3': 53, 'gree4': 53, 'main 10': 43, 'main 11': 37, 'main 2': 61, 'main 5': 64, 'main 8': 47, 'main 9': 38, 'marry2': 9, 'oran1': 31, 'oran2': 31, 'oran3': 31, 'oran4': 31, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 30, 'upfill2': 43, 'upfill3': 43, 'upfill4': 30, }

subs[('*1-10-0', 'white')]={ 'b13': 15, 'b22': 44, 'b23': 20, 'b24': 34, 'b25': 34, 'b32': 27, 'b34': 34, 'blue1': 84, 'blue2': 54, 'cuba1': 5, 'desk1': 17, 'desk2': 11, 'hotbox2': 34, 'main 10': 34, 'main 11': 34, 'main 2': 34, 'main 3': 25, 'main 4': 25, 'main 5': 34, 'main 7': 34, 'main 8': 34, 'main 9': 34, 'rock': 3, 'side l': 23, 'side r': 14, 'sidefill1': 6, 'sidefill2': 23, }

subs[('*2-01-0-dance', 'white')]={ 'b32': 43, 'b34': 30, 'cycleft': 19, 'cycright': 19, 'desk2': 24, 'hotback': 100, 'hotbox1': 42, 'hotbox2': 78, 'main 10': 100, 'main 11': 46, 'main 2': 46, 'main 3': 46, 'main 4': 46, 'main 5': 100, 'main 7': 100, 'main 8': 46, 'main 9': 46, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 26, 'upfill2': 46, 'upfill3': 32, 'upfill4': 26, }

subs['*2-01-01-solo']={ 'b23': 100, 'b24': 100, 'b32': 43, 'cycleft': 55, 'cycright': 55, 'desk2': 24, 'hotback': 100, 'hotbox1': 42, 'hotbox2': 78, 'main 7': 100, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 67, 'upfill2': 1, 'upfill4': 67, }

subs['*2-01-1-after dance']={ 'b32': 43, 'b34': 30, 'cycleft': 19, 'cycright': 19, 'desk2': 24, 'hotback': 100, 'hotbox1': 42, 'hotbox2': 78, 'main 10': 100, 'main 11': 46, 'main 2': 46, 'main 3': 46, 'main 4': 46, 'main 5': 100, 'main 7': 100, 'main 8': 46, 'main 9': 46, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill1': 26, 'upfill2': 46, 'upfill3': 32, 'upfill4': 26, }

subs['*2-01-1-darker dance']={ 'b23': 93, 'b24': 93, 'b32': 4, 'b34': 9, 'cycleft': 19, 'cycright': 19, 'desk2': 10, 'hotback': 100, 'hotbox1': 42, 'hotbox2': 52, 'red1': 100, 'red2': 100, 'red3': 100, 'red4': 100, 'upfill4': 26, }

subs['*2-01-2-table']={ 'b22': 100, 'cuba1': 22, 'desk2': 58, 'hotbox2': 46, 'main 2': 62, 'main 3': 80, 'main 4': 100, 'main 5': 34, 'main 7': 10, 'main 8': 10, 'main 9': 64, 'red1': 100, 'rock': 22, 'upfill1': 76, 'upfill2': 76, 'upfill3': 76, 'upfill4': 76, }

subs['*2-01-3-small table']={ 'b22': 56, 'b25': 5, 'desk1': 47, 'desk2': 58, 'main 3': 18, 'main 9': 11, 'red1': 100, 'upfill1': 62, 'upfill4': 62, }

subs[('*2-02-0', 'white')]={ 'b23': 76, 'b24': 52, 'main 10': 53, 'main 2': 53, 'main 4': 24, 'main 5': 18, 'main 7': 42, 'main 8': 36, 'main 9': 60, 'marry2': 38, 'side r': 34, }

subs['*2-02-1-works']={'upfill2':50,'upfill3':50,'cycright':50}

subs[('*2-03-00-open dance', 'white')]={ 'b22': 11, 'blue1': 70, 'blue2': 70, 'blue3': 70, 'blue4': 92, 'cuba1': 20, 'gree1': 75, 'gree2': 75, 'gree3': 75, 'gree4': 75, 'hotback': 40, 'main 10': 40, 'main 11': 28, 'main 2': 60, 'main 4': 45, 'main 5': 20, 'main 8': 26, 'main 9': 42, 'red1': 75, 'red2': 75, 'red3': 75, 'red4': 97, 'side l': 31, 'side r': 31, 'upfill1': 27, 'upfill2': 31, 'upfill3': 26, 'upfill4': 17, }

subs['*2-03-10-dialogue']={ 'b13': 60, 'b22': 62, 'b23': 64, 'b24': 19, 'b25': 16, 'blue1': 70, 'blue2': 70, 'blue3': 70, 'blue4': 92, 'cuba1': 59, 'gree1': 75, 'gree2': 75, 'gree3': 75, 'gree4': 75, 'hotback': 40, 'main 10': 48, 'main 11': 40, 'main 2': 54, 'main 4': 45, 'main 5': 20, 'main 8': 22, 'main 9': 73, 'red1': 75, 'red2': 75, 'red3': 75, 'red4': 97, 'side l': 31, 'side r': 31, 'sidefill1': 20, 'sidefill2': 20, 'upfill1': 27, 'upfill2': 31, 'upfill3': 26, 'upfill4': 17, }

subs['*2-03-20-luckcover']={ 'b22': 20, 'b23': 20, 'b24': 20, 'b25': 20, 'blue1': 70, 'blue2': 70, 'blue3': 70, 'blue4': 92, 'cuba1': 5, 'gree1': 75, 'gree2': 75, 'gree3': 75, 'gree4': 75, 'hotback': 40, 'main 7': 100, 'main 8': 57, 'red1': 75, 'red2': 75, 'red3': 75, 'red4': 97, 'side l': 31, 'side r': 31, 'upfill1': 27, 'upfill2': 31, 'upfill3': 26, 'upfill4': 17, }

subs['*2-03-20-luck-l']={ 'b22': 100, }

subs['*2-03-20-luck-c']={ 'b23': 100, 'b24': 100, }

subs['*2-03-20-luck-r']={ 'b25': 100, }

subs[('*2-04-0', 'white')]={ 'b13': 39, 'b22': 50, 'b23': 67, 'b24': 67, 'b25': 71, 'b32': 57, 'b34': 34, 'blue1': 63, 'blue2': 63, 'blue3': 63, 'blue4': 63, 'cycright': 18, 'desk1': 24, 'desk2': 26, 'hotbox2': 59, 'main 10': 5, 'main 11': 5, 'main 2': 5, 'main 3': 45, 'main 5': 56, 'main 7': 5, 'main 8': 5, 'main 9': 5, 'marry2': 50, 'rock': 20, 'side r': 34, 'upfill1': 70, 'upfill4': 70, }

subs[('*2-05-0', 'white')]={ 'b22': 100, 'b23': 100, 'b24': 100, 'b32': 14, 'cuba2': 9, 'desk1': 53, 'desk2': 65, 'hotbox1': 25, 'hotbox2': 100, 'main 10': 100, 'main 11': 100, 'main 4': 100, 'main 5': 70, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'marry1': 61, 'marry2': 47, 'rock': 23, 'sidefill2': 25, 'upfill2': 6, 'upfill3': 34, }

subs['*2-05-1-dream']={ 'desk2': 42, 'dream': 100, 'main 11': 7, 'upfill2': 16, }

subs['*2-05-2-boat']={ 'b22': 100, 'b23': 100, 'b24': 100, 'b32': 52, 'cuba2': 65, 'cycright': 55, 'desk1': 44, 'desk2': 84, 'hotbox1': 21, 'hotbox2': 95, 'main 10': 84, 'main 11': 84, 'main 3': 72, 'main 4': 100, 'main 5': 83, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'marry1': 75, 'marry2': 100, 'rock': 43, 'sidefill2': 43, 'upfill2': 55, 'upfill3': 31, }

subs[('*2-06-0', 'white')]={ 'b22': 14, 'b23': 100, 'b24': 100, 'b32': 23, 'b34': 30, 'cycright': 100, 'desk2': 23, 'hotbox1': 49, 'hotbox2': 43, 'main 10': 55, 'main 11': 55, 'main 2': 30, 'main 7': 30, 'main 9': 30, 'marry1': 69, 'marry2': 34, 'rock': 17, 'side r': 30, 'upfill1': 48, 'upfill4': 48, }

subs['*2-06-1-patio right']={ 'patio2': 100, }

subs['*2-06-2 patio left']={ 'patio1': 100, }

subs[('*2-07-0', 'white')]={ 'b22': 100, 'b23': 100, 'b24': 100, 'b25': 100, 'b34': 100, 'cycleft': 41, 'cycright': 41, 'desk2': 78, 'edge': 63, 'hotbox1': 14, 'hotbox2': 5, 'main 10': 100, 'main 11': 100, 'main 2': 100, 'main 3': 83, 'main 4': 100, 'main 5': 100, 'main 7': 100, 'main 8': 100, 'main 9': 100, 'marry1': 100, 'marry2': 100, 'phone': 62, 'side l': 100, 'side r': 100, 'sidefill1': 83, 'sidefill2': 100, 'upfill1': 56, 'upfill2': 100, 'upfill3': 69, 'upfill4': 56, }

subs['*curtain']={ 'b22': 73, 'b24': 73, 'b25': 73, 'b34': 73, 'desk2': 57, 'edge': 58, 'hotbox2': 73, 'main 10': 73, 'main 11': 73, 'main 2': 73, 'main 3': 73, 'main 4': 73, 'main 5': 73, 'main 7': 73, 'main 8': 73, 'main 9': 73, 'marry1': 73, 'marry2': 73, 'phone': 58, 'side l': 73, 'side r': 73, 'sidefill1': 23, 'sidefill2': 23, 'upfill1': 9, 'upfill2': 68, 'upfill3': 18, 'upfill4': 9, }

subs['*phone booth']={ 'phone': 100, }

subs['*spare']={ }

subs['bank1ctr']={ 'b22': 100, 'b23': 100, 'b24': 100, 'b25': 100, }

subs['cyc']={ 'cycleft': 100, 'cycright': 100, }

subs['god']={ 'god': 100, }

subs['patio left']={ 'patio1': 100, }

subs['patio right']={ 'patio2': 100, }

subs['sidefill']={ 'sidefill1': 100, 'sidefill2': 100, }

subs['sidepost']={ 'side l': 100, 'side r': 100, }

subs['upfill sides']={ 'upfill1': 100, 'upfill4': 100, }

subs["*interscene"] = {}
subs["*interscene"] = { "blue1" : 49, "blue3" : 49, "blue2" : 49,
    "blue4" : 49,}
subs["*1-08-30-full"] = { "cycright" : 15, "main 11" : 38, "main 10" : 38,
    "upfill1" : 0, "sidefill2" : 38, "b25" : 100, "side l" : 38,
    "b23" : 100, "b22" : 100, "desk2" : 30, "oran3" : 82, "upfill4" : 0,
    "side r" : 38, "upfill3" : 0, "blue3" : 15, "upfill2" : 0, "gree2" : 15,
    "gree3" : 15, "cafe2" : 100, "gree1" : 15, "gree4" : 15, "marry2" : 38,
    "marry1" : 38, "cuba1" : 100, "cuba2" : 100, "red3" : 77, "red2" : 77,
    "sidefill1" : 38, "b24" : 100, "red4" : 95, "b34" : 54, "cycleft" : 15,
    "b32" : 43, "hotbox2" : 38, "hotbox1" : 38, "blue1" : 15, "oran2" : 82,
    "oran1" : 82, "blue2" : 15, "blue4" : 15, "oran4" : 82, "main 3" : 38,
    "main 2" : 38, "main 5" : 38, "main 4" : 38, "main 7" : 38, "phone" : 31,
    "main 9" : 38, "main 8" : 38, "edge" : 31, "cafe1" : 100, "red1" : 77,}
subs["*2-03-20-luck-c"] = { "hotbox2" : 0, "b23" : 100, "b24" : 100,
    "main 5" : 52, "marry2" : 37,}
subs["*2-07-0"] = { "sidefill2" : 100, "sidefill1" : 83, "cycright" : 41,
    "main 11" : 100, "main 10" : 100, "upfill1" : 56, "b34" : 100,
    "b25" : 100, "cycleft" : 41, "b23" : 100, "b22" : 100, "side l" : 100,
    "hotbox2" : 5, "hotbox1" : 14, "upfill4" : 56, "b24" : 100, "desk2" : 78,
    "upfill3" : 69, "upfill2" : 100, "main 3" : 83, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "phone" : 62,
    "main 9" : 100, "main 8" : 100, "edge" : 63, "marry2" : 100,
    "marry1" : 100, "xmas" : 80, "side r" : 100,}
subs["*1-01-0-sarah"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 60, "upfill2" : 91, "upfill1" : 56,
    "side l" : 100,  "b25" : 100, "cycleft" : 41, "b22" : 100,
    "desk2" : 78, "phone" : 80, "hotbox1" : 43, "upfill4" : 68, "b24" : 100,
    "side r" : 100, "main 11" : 100, "main 10" : 100, "main 3" : 100,
    "main 2" : 100, "main 5" : 100, "main 4" : 100, "main 7" : 100,
    "hotbox2" : 91, "main 9" : 100, "main 8" : 100, "b34" : 100,
    "edge" : 80, "marry2" : 100, "marry1" : 100,}
subs["*1-01-0-sarah"] = { "sidefill2" : 37, "sidefill1" : 39,
    "cycright" : 24, "upfill3" : 31, "upfill2" : 62, "upfill1" : 27,
    "b34" : 34, "b25" : 100, "side l" : 50, "b22" : 89,
    "desk2" : 30, "phone" : 80, "hotbox1" : 43, "upfill4" : 39, "b24" : 100,
    "side r" : 46, "main 11" : 100, "main 10" : 100, "main 3" : 5,
    "main 2" : 92, "main 5" : 100, "main 4" : 100, "main 7" : 100,
    "hotbox2" : 52, "main 9" : 58, "main 8" : 0, "cycleft" : 24,
    "edge" : 24, "marry2" : 71, "marry1" : 62,}
subs["*1-05-0-down"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 36, "upfill3" : 37, "upfill2" : 37, "upfill1" : 2,
    "side l" : 100,  "b25" : 100, "cycleft" : 18, "b23" : 100,
    "desk1" : 19, "desk2" : 31, "b22" : 100, "hotbox2" : 17, "upfill4" : 2,
    "b24" : 100, "side r" : 82, "main 11" : 89, "main 10" : 100,
    "main 3" : 85, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "b34" : 13, "edge" : 37,
    "b13" : 100,}
subs["*1-05-0"] = { "sidefill2" : 68, "sidefill1" : 65, "cycright" : 42,
    "main 11" : 11, "main 10" : 22, "b34" : 0, "b25" : 67, "side l" : 100,
    "b23" : 67, "b22" : 67, "desk2" : 31, "desk1" : 19, "hotbox2" : 0,
    "b24" : 67, "side r" : 82, "upfill3" : 37, "upfill2" : 37, "main 3" : 53,
    "main 2" : 68, "main 5" : 68, "main 4" : 68, "main 7" : 22, "main 9" : 22,
    "main 8" : 22, "cycleft" : 24, "edge" : 0, "b13" : 100,}
subs["*1-05-0"] = { "sidefill2" : 68, "sidefill1" : 65, "cycright" : 42,
    "main 11" : 11, "main 10" : 22, "b34" : 0, "b25" : 67, "side l" : 100,
    "b23" : 67, "b22" : 67, "desk2" : 31, "desk1" : 19, "hotbox2" : 91,
    "hotbox1" : 100, "b24" : 67, "side r" : 82, "upfill3" : 61, "upfill2" : 61,
    "main 3" : 53, "main 2" : 68, "main 5" : 68, "main 4" : 68, "main 7" : 22,
    "main 9" : 22, "main 8" : 20, "cycleft" : 24, "edge" : 0, "b13" : 100,
    "marry2" : 19,}
subs["*1-05-0-down"] = { "sidefill2" : 70, "sidefill1" : 70, "cycright" : 0,
    "upfill3" : 25, "upfill2" : 25, "upfill1" : 15, "b34" : 13, 
    "b25" : 100, "side l" : 100, "b23" : 100, "desk1" : 19, "desk2" : 31,
    "b22" : 100, "hotbox2" : 17, "upfill4" : 15, "b24" : 100, "side r" : 82,
    "main 11" : 89, "main 10" : 100, "main 3" : 85, "main 2" : 100,
    "main 5" : 100, "main 4" : 100, "main 7" : 100, "main 9" : 100,
    "main 8" : 100, "cycleft" : 0, "edge" : 37, "b13" : 100,}
subs["*1-08-30-full"] = { "cycright" : 10, "main 11" : 38, "main 10" : 36,
    "upfill1" : 0, "sidefill2" : 0, "b25" : 100, "side l" : 38, "b23" : 100,
    "b22" : 100, "desk2" : 0, "oran3" : 64, "upfill4" : 0, "side r" : 38,
    "upfill3" : 0, "blue3" : 100, "upfill2" : 0, "gree2" : 15, "gree3" : 15,
    "cafe2" : 100, "gree1" : 15, "gree4" : 15, "marry2" : 38, "marry1" : 38,
    "cuba1" : 23, "cuba2" : 0, "red3" : 27, "red2" : 27, "sidefill1" : 0,
    "b24" : 100, "red4" : 45, "b34" : 28, "cycleft" : 10, "b32" : 43,
    "hotbox2" : 38, "hotbox1" : 38, "blue1" : 100, "oran2" : 64,
    "oran1" : 64, "blue2" : 100, "blue4" : 100, "oran4" : 64, "main 3" : 38,
    "main 2" : 38, "main 5" : 0, "main 4" : 38, "main 7" : 0, "phone" : 31,
    "main 9" : 38, "main 8" : 38, "edge" : 0, "cafe1" : 100, "red1" : 27,}
subs["*2-02-0"] = { "main 2" : 53, "main 5" : 18, "main 10" : 53,
    "main 7" : 42, "main 9" : 60, "main 8" : 36, "b24" : 52, "b23" : 76,
    "side r" : 34, "blue1" : 63, "marry2" : 38, "blue3" : 63, "blue2" : 63,
    "blue4" : 63, "main 4" : 24,}
subs["*2-03-20-luck-c"] = { "main 5" : 0, "main 10" : 0, "main 7" : 0,
    "b24" : 100, "b23" : 100, "b32" : 0, "hotbox2" : 0, "hotback" : 0,
    "b13" : 31, "rock" : 0, "marry2" : 0, "main 4" : 78,}
subs["*2-05-2-boat"] = { "sidefill2" : 43, "cycright" : 0, "main 11" : 84,
    "main 10" : 84, "upfill1" : 0, "b24" : 100, "b23" : 100, "b22" : 100,
    "desk2" : 84, "desk1" : 44, "hotbox2" : 95, "hotbox1" : 21, "upfill4" : 0,
    "b32" : 52, "upfill3" : 34, "upfill2" : 0, "main 3" : 72, "main 5" : 83,
    "main 4" : 100, "main 7" : 100, "main 9" : 100, "main 8" : 100,
    "rock" : 43, "marry2" : 100, "marry1" : 75, "cuba2" : 65,}
subs["*2-06-0"] = { "cycright" : 100, "main 11" : 55, "main 10" : 55,
    "upfill1" : 48, "hotbox2" : 43, "b34" : 30, "b24" : 100, "b23" : 100,
    "main 7" : 30, "desk2" : 23, "b22" : 14, "main 9" : 30, "hotbox1" : 71,
    "main 2" : 30, "b32" : 23, "rock" : 17, "marry2" : 34, "marry1" : 69,
    "upfill4" : 48, "side r" : 30,}
subs["*1-01-0-justback"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 60, "upfill2" : 91, "upfill1" : 56,
    "side l" : 100,  "b25" : 100, "cycleft" : 41, "b22" : 100,
    "desk2" : 78, "hotbox2" : 91, "hotbox1" : 43, "upfill4" : 68,
    "b24" : 100, "side r" : 100, "main 11" : 100, "main 10" : 100,
    "main 3" : 100, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "b34" : 100,
    "edge" : 80, "marry2" : 100, "marry1" : 100,}
subs["*1-01-0-justleft"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 60, "upfill2" : 91, "upfill1" : 56,
    "side l" : 100,  "b25" : 100, "cycleft" : 41, "b22" : 100,
    "desk2" : 78, "hotbox2" : 91, "hotbox1" : 43, "upfill4" : 68,
    "b24" : 100, "side r" : 100, "main 11" : 100, "main 10" : 100,
    "main 3" : 100, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "b34" : 100,
    "edge" : 80, "marry2" : 100, "marry1" : 100,}
subs["*1-01-0-justleft"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 0, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "b34" : 7,  "b25" : 0, "side l" : 100, "b22" : 100,
    "desk2" : 78, "hotbox2" : 10, "hotbox1" : 43, "upfill4" : 0,
    "b24" : 0, "side r" : 100, "main 11" : 0, "main 10" : 100, "main 3" : 100,
    "main 2" : 100, "main 5" : 100, "main 4" : 100, "main 7" : 0,
    "main 9" : 0, "main 8" : 0, "cycleft" : 0, "edge" : 80, "marry2" : 100,
    "marry1" : 100,}
subs["*1-01-0-justback"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 60, "upfill2" : 91, "upfill1" : 56,
    "b34" : 100,  "b25" : 100, "side l" : 100, "b22" : 100,
    "desk2" : 78, "hotbox2" : 91, "hotbox1" : 43, "upfill4" : 68,
    "b24" : 100, "side r" : 100, "main 11" : 100, "main 10" : 100,
    "main 3" : 100, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "cycleft" : 41,
    "edge" : 80, "marry2" : 100, "marry1" : 100,}
subs["*1-01-0-justright"] = { "sidefill2" : 100, "sidefill1" : 100,
    "cycright" : 41, "upfill3" : 60, "upfill2" : 91, "upfill1" : 56,
    "side l" : 100,  "b25" : 100, "cycleft" : 41, "b22" : 100,
    "desk2" : 78, "hotbox2" : 91, "hotbox1" : 43, "upfill4" : 68,
    "b24" : 100, "side r" : 100, "main 11" : 100, "main 10" : 100,
    "main 3" : 100, "main 2" : 100, "main 5" : 100, "main 4" : 100,
    "main 7" : 100, "main 9" : 100, "main 8" : 100, "b34" : 100,
    "edge" : 80, "marry2" : 100, "marry1" : 100,}
subs["*1-01-0-justright"] = { "sidefill2" : 100, "sidefill1" : 0,
    "cycright" : 0, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "b34" : 100,  "b25" : 100, "side l" : 0, "b22" : 0,
    "desk2" : 0, "hotbox2" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100,
    "side r" : 100, "main 11" : 0, "main 10" : 0, "main 3" : 0, "main 2" : 100,
    "main 5" : 100, "main 4" : 0, "main 7" : 0, "main 9" : 100, "main 8" : 100,
    "cycleft" : 0, "edge" : 0, "marry2" : 7, "marry1" : 100,}
subs["*1-01-0-justleft"] = { "sidefill2" : 0, "sidefill1" : 100,
    "cycright" : 0, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "b34" : 7,  "b25" : 0, "side l" : 100, "b22" : 100,
    "desk2" : 78, "hotbox2" : 10, "hotbox1" : 0, "upfill4" : 0, "b24" : 0,
    "side r" : 0, "main 11" : 0, "main 10" : 100, "main 3" : 100,
    "main 2" : 100, "main 5" : 100, "main 4" : 100, "main 7" : 0,
    "main 9" : 0, "main 8" : 0, "cycleft" : 0, "edge" : 80, "marry2" : 100,
    "marry1" : 0,}
subs["*1-01-0-justback"] = { "b32" : 7, "sidefill2" : 47, "sidefill1" : 47,
    "cycright" : 41, "upfill3" : 60, "upfill2" : 91, "upfill1" : 56,
    "b34" : 16, "b25" : 16, "side l" : 0, "b23" : 16,
    "b22" : 16, "desk2" : 0, "desk1" : 0, "hotbox2" : 7, "hotbox1" : 0,
    "upfill4" : 68, "b24" : 16, "side r" : 0, "main 11" : 100, "main 10" : 100,
    "main 3" : 13, "main 2" : 13, "main 5" : 13, "main 4" : 100,
    "main 7" : 100, "phone" : 0, "main 9" : 14, "main 8" : 13, "cycleft" : 41,
    "edge" : 0, "b13" : 16, "rock" : 0, "marry2" : 16, "marry1" : 16,
    "cuba1" : 16, "cuba2" : 0,}
subs["*1-01-0-justright"] = { "sidefill2" : 100, "sidefill1" : 0,
    "cycright" : 0, "upfill3" : 0, "upfill2" : 0, "upfill1" : 0,
    "b34" : 100, "b25" : 100, "side l" : 0, "b22" : 0,
    "desk2" : 0, "hotbox2" : 0, "hotbox1" : 0, "upfill4" : 0, "b24" : 100,
    "side r" : 100, "main 11" : 0, "main 10" : 0, "main 3" : 0, "main 2" : 100,
    "main 5" : 100, "main 4" : 0, "main 7" : 0, "phone" : 100, "main 9" : 100,
    "main 8" : 100, "cycleft" : 0, "edge" : 0, "marry2" : 7, "marry1" : 100,}
