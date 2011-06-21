import sys, traceback, time, logging
log = logging.getLogger()

def run(main, profile=False):
    if not profile:
        main()
        return
    
    import hotshot, hotshot.stats
    p = hotshot.Profile("/tmp/pro")
    p.runcall(main)
    p.close()
    hotshot.stats.load("/tmp/pro").sort_stats('cumulative').print_stats()
    
def watchPoint(filename, lineno, event="call"):
    """whenever we hit this line, print a stack trace. event='call'
    for lines that are function definitions, like what a profiler
    gives you.

    Switch to 'line' to match lines inside functions. Execution speed
    will be much slower."""
    seenTraces = {} # trace contents : count
    def trace(frame, ev, arg):
        if ev == event:
            if (frame.f_code.co_filename, frame.f_lineno) == (filename, lineno):
                stack = ''.join(traceback.format_stack(frame))
                if stack not in seenTraces:
                    print "watchPoint hit"
                    print stack
                    seenTraces[stack] = 1
                else:
                    seenTraces[stack] += 1

        return trace
    sys.settrace(trace)

    # atexit, print the frequencies?

def logTime(func):
    def inner(*args, **kw):
        t1 = time.time()
        try:
            ret = func(*args, **kw)
        finally:
            log.info("Call to %s took %.1f ms" % (
                func.__name__, 1000 * (time.time() - t1)))
        return ret
    return inner
