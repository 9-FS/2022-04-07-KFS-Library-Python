# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import datetime as dt
import math
import time


def sleep_mod(sleep_modulus: int) -> None:
    """
    Blockingly sleeps until the current unix time modulus sleep_modulus equals 0.
    """

    now_DT: dt.datetime     # now
    return_DT: dt.datetime  # when to return

    now_DT=dt.datetime.now(dt.timezone.utc)
    return_DT=now_DT-dt.timedelta(seconds=now_DT.timestamp()%sleep_modulus)+dt.timedelta(seconds=sleep_modulus)


    sleep_until(return_DT)  # sleep until calculated return time

    return


def sleep_until(return_DT: dt.datetime) -> None:
    """
    Blockingly sleeps until the specified datetime and then returns. Expects timezone-aware datetime object.
    """

    now_DT: dt.datetime             # now
    time_until_return: dt.timedelta # how long still until return
    time_to_sleep: float            # how many seconds is next sleep? depends on time_until_return magnitude


    while (now_DT:=dt.datetime.now(dt.timezone.utc))<return_DT:                             # as long as return datetime not reached yet: sleep
        time_until_return=return_DT-now_DT                                                  # update time until return
        try:
            time_to_sleep=10**(math.floor(math.log10(time_until_return.total_seconds()))-1) # time to sleep is 1 magnitude smaller than time until return
        except ValueError:                                                                  # in case time until return is exactly 0: log10 crashes, give time to sleep 0
            time_to_sleep=0
        if time_to_sleep<1e-3:
            time_to_sleep=1e-3                                                              # sleep at least 1ms, otherwise needlessly computing for anyways inaccurate result

        time.sleep(time_to_sleep)

    return