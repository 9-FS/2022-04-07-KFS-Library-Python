import math


def round_sig(x: float, significants: int) -> int: #gerundet auf Signifikante, gibt Zahl zurück
    try:
        x=float(x)
    except ValueError:
        raise TypeError("Error in KFS::math::round_sig(...): Type of \"x\" must be float or convertable to float.")
    if type(significants)!=int:
        raise TypeError("Error in KFS::math::round_sig(...): Type of \"significants\" must be int.")
    
    if x==0:
        return 0

    magnitude=math.floor(math.log10(abs(x)))
    return round(x, -1*magnitude+significants-1)  #runden