
class Stage(Canvas):
    
    """a fancy widget that shows light locations (and optionally their
    aim locations on an image of the stage. you can select or
    multiselect lights and drag them up or down to change their
    brightness.

    ctrl-a is select all,
    ctrl-shift-a or clicking on no light deselects all,
    re-clicking a light with shift key down toggles whether it's in the selection.
    ctrl-drag-rectangle deselects the lights in the rectangle,
    shift-drag-rectangle selects the lights in the rectangle,
    drag-rectangle selects only the lights in the rectangle.

    a light can be selected on its location point, it's aim point
    (which may or may not be present), or its name.

    lights should be able to be interactively 'locked', which blocks
    them from being selected. 

    """
    def __init__(self,parent,**kw):
        Canvas.__init__(self,parent,**kw)
        if 'stageimage' in kw:
            
