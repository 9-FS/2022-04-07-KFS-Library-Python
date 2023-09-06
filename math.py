# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import math


def round_sig(x: float, significants: int) -> int:  # round to significant number, returns number not string
    x=float(x)


    if x==0:
        return 0

    magnitude=math.floor(math.log10(abs(x)))        # determine magnitude floored
    return round(x, -1*magnitude+significants-1)    # round #type:ignore