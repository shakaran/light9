import shutil
import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))

os.environ['LIGHT9_SHOW'] = "_test_show"
try:
    shutil.rmtree("_test_show")
except OSError:
    pass
os.mkdir("_test_show")
f = open("_test_show/config.n3", "w")
f.write("""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://light9.bigasterisk.com/> .
@prefix ch: <http://light9.bigasterisk.com/theater/skyline/channel/> .
@prefix dmx: <http://light9.bigasterisk.com/dmx/> .

ch:frontLeft a :Channel; rdfs:label "frontLeft"; :altName "b1"; :output dmx:c1 .
ch:frontRight a :Channel; rdfs:label "frontRight"; :output dmx:c2 . 

dmx:c1 :dmxAddress 1 .
dmx:c2 :dmxAddress 2 .

""")
f.close()
