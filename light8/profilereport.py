"""
tweak rsn.py to run the profile module, and write the output to files
in profile/ with names that describe how you exercised the
program. then run this program to make files in profile/html/ for
easier viewing.
"""

import pstats,glob,os,time,sys

allfiles = glob.glob("profile/*")
allfiles.remove('profile/html')
allfiles.sort()

header = "profile output from %s<p>" % (time.ctime())
for f in allfiles:
    f=f[8:]
    header = header+"<a href=%(f)s.html>%(f)s</a> | " % locals()

for profileoutput in allfiles:


    
    s=pstats.Stats(profileoutput)

    f=open("profile/html/%s.html" % profileoutput[8:],'w')
    sys.stdout=f
    print header,"<pre>"
    s.sort_stats('cumulative').print_stats(15).print_callers(15)
    print "</pre>"

