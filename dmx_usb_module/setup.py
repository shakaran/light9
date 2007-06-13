from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(name="dmx",
      ext_modules=[
        Extension("dmx",
                  ["dmx.pyx"],
#                  library_dirs=['/usr/X11R6/lib'],
#                  libraries=["X11","Xtst"]
                  ),
        ],  
      cmdclass={'build_ext':build_ext})

