from __future__ import division
import wave, audioop

def simp(filename, seconds_per_average=0.001):
    """smaller seconds_per_average means fewer data points"""
    wavefile = wave.open(filename, 'rb')
    print "# gnuplot data for %s, seconds_per_average=%s" % \
        (filename, seconds_per_average)
    print "# %d channels, samplewidth: %d, framerate: %s, frames: %d\n# Compression type: %s (%s)" % wavefile.getparams()

    framerate = wavefile.getframerate() # frames / second
    frames_to_read = int(framerate * seconds_per_average)
    print "# frames_to_read=%s" % frames_to_read

    time_and_max = []
    values = []
    count = 0
    while 1:
        fragment = wavefile.readframes(frames_to_read)
        if not fragment:
            break

        # other possibilities:
        # m = audioop.avg(fragment, 2)
        # print count, "%s %s" % audioop.minmax(fragment, 2)

        m = audioop.rms(fragment, wavefile._framesize)
        time_and_max.append((count, m))
        values.append(m)
        count += frames_to_read
        # if count>1000000:
            # break

    # find the min and max
    min_value, max_value = min(values), max(values)
    points = [] # (secs,height)
    for count, value in time_and_max:
        points.append((count/framerate,
                       (value - min_value) / (max_value - min_value)))
    return points
