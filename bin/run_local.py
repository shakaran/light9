# allows bin/* to work without installation

# this should be turned off when the programs are installed

import sys,os
sys.path.insert(0,os.path.join(os.path.dirname(sys.argv[0]),".."))


