

from Config import subs
import Patch

Patch.reload_data(0)

def print_tsv(filename,allchans,subs):
    f=open(filename,"w")
    print >>f,"\t"+"\t".join(allchans)

    for name,levels in subs.items():
        normd={}
        # nrmalize the names in the sub
        for k,v in levels.items():
            normd[Patch.resolve_name(k)]=v

        print >>f,"%s\t%s" % (name, "\t".join([str(normd.get(c,"")) for c in allchans]))


def read_tsv(filename,outname):
    """converts from tsv filename to a config file (python) named outname"""
    f=open(filename,'r')
    out=open(outname,'w')
    allchans=f.readline().split("\t")[1:]
    for line in f.xreadlines():
        spl=line.split("\t")
        subname=spl[0]
        print >>out,"subs['%s']={" % subname,
        for channame,level in zip(allchans,spl[1:]):
            try:
                if level!="" and int(level)>0:
                    print >>out,"'%s': %s," %(channame,level),
            except ValueError:
                pass
        print >>out,"}\n"
        

print_tsv(filename="sublevs.txt",allchans=Patch.get_all_channels(),subs=subs)
read_tsv(filename="sublevs.txt",outname="Configsubs2.py")

                    
