import hotshot, hotshot.stats
import sys, traceback

def run(main, profile=False):
    if not profile:
        main()
        return
    
    p = hotshot.Profile("/tmp/pro")
    p.runcall(main)
    p.close()
    hotshot.stats.load("/tmp/pro").sort_stats('time').print_stats()
    
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
