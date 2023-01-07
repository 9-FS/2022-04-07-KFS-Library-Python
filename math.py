import math
from . import types


def round_sig(x: float, significants: int) -> int: #round to significant number, returns number not string
    types.check(round_sig, locals(), types.Mode.convertable, types.Mode.instance)
    x=float(x)

    if x==0:
        return 0

    magnitude=math.floor(math.log10(abs(x)))        #determine magnitude floored
    return round(x, -1*magnitude+significants-1)    #round