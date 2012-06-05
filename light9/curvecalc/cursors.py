
import logging
log = logging.getLogger("cursors")

# accept ascii images, read file images, add hotspots, read xbm as
# cursor with @filename form

_pushed = {} # widget : [old, .., newest]
def push(widget,new_cursor):
    global _pushed
    _pushed.setdefault(widget,[]).append(widget.cget("cursor"))

def pop(widget):
    global _pushed
    try:
        c = _pushed[widget].pop(-1)
    except IndexError:
        log.debug("cursor pop from empty stack")
        return
    widget.config(cursor=c)
    
    
