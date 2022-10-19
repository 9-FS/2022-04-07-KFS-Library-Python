import math
from . import typecheck


def round_sig(x: float, significants: int) -> int: #round to significant number, returns number not string
    typecheck.check(round_sig, locals(), typecheck.Mode.convertable, typecheck.Mode.instance)
    
    if x==0:
        return 0

    magnitude=math.floor(math.log10(abs(x)))        #determine magnitude floored
    return round(x, -1*magnitude+significants-1)    #round