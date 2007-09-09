def light9_presentation():
    """
    Drew Perttula

    drewp@bigasterisk.com

    http://light9.bigasterisk.com


    Goals of light9:

    - control the brightness of many lights while playing music

    - allow easy editing of the show

    - allow easy maintenance of the code, even while the show is running








    """









def dependencies():
    """
    Twisted - event loop and networking
    TwistedWeb - xmlrpc protocol
    tk, tix
    pympd - my twisted interface to mpd
    pydispatcher - signals

    mpd - music player daemon

    swig - interface to C code
    darcs

*






    """





def connections():
    """
               (play cmds)
    ascoltami --------------> mpd ----------> audio out
        | (timing)
        v
    curvecalc    subcomposer    keyboardcomposer
        |            |                 |
        +---         |             ----+
            \-----   |    --------/
                  \--+---/
                     | (light levels)
                     v
*                dmxserver
                    | (dmx levels)
          ......... v ....................
          .      chippy                  .
          .         | (dmx)              . external hardware
          .         v                    .
          .      dmx dimmer              .
          .         | (juice)            .
          .         v                    .
          .      light                   .
          ................................
    """


def metrics():
    """
    selected linecounts:
      356 ascoltami              (music player)
      318 curvecalc              (curve and expression editor)
      279 keyboardcomposer
      189 dmxserver              (hardware output)
      153 subcomposer
       17 wavecurve              (create smoothed waveforms from .wav)

      311 light9/curve.py        (curve widgets)
      191 light9/FlyingFader.py  (enhanced tk.Scale)
      168 light9/Submaster.py
*     151 light9/zoomcontrol.py
      137 light9/dmxchanedit.py
       40 light9/wavepoints.py

       65 light9/io/parport.c    (dmx interface protocol)
       50 light9/io/serport.i    (i2c interface to sliders)

    total in project: about 3200 in about 30 files

    """



def future_projects():
    """
    A submaster server that talks with the other programs and
    eliminates all the explicit saving and reloading of subs

    More abstract output layer, to which I can add home lighting, for
    example

    Small timed 'clips' that can be triggered

    Generalize to a whizzy, distributed real-time circuit simulator
    node network with a 5GL editor and failsafe checkpointing and
    redundancy
*



    """






















