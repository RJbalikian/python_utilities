def map_diff(xIn, x1,x2,y1,y2):
    """Simple, linear interpolation between two points

    Parameters
    ----------
    xIn : float, int, or numeric
        X Location at which y-value is desired. This should fall between (or be equal to) x1 and x2
    x1 : float, int, or numeric
        Initial X location, with known y-value y1 
    x2 : float, int, or numeric
        Second X location, with known y-value y2
    y1 : float, int, or numeric
        Known y-value at x1
    y2 : float, int, or numeric
        Known y-value at x2

    Returns
    -------
    float
        Y-value that is proportionally scaled based on the xIn relative distance to x1 and x2
    """
    if x1==xIn:
        yOut=y1
    elif x2==xIn:
        yOut = y2
    else:
        totXDiff = x2-x1
        percXDiff = (xIn-x1)/totXDiff
        totYDiff = y2-y1
        yOut = y1 + totYDiff*percXDiff
    return yOut
