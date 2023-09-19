# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import inspect
import math
import sys
from . import math as KFSmath   # for round_sig, must "as KFSmath" because otherwise name conflict with math


def notation_abs(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True, width: int=0) -> str:   #type:ignore
    """
    Formats rounded number as string, no changing of magnitude for decimal prefixes (notation absolute).

    Arguments:
    - x: number to format
    - precision:
        - if round_static==False: Round to significant digits.
        - if round_static==True: Round to magnitude 10^(-precision), like built-in round().
    - trailing_zeros: Append zeros until reached precision.
    - width: After appending trailing zeros, prepend zeros until reaching width. Width includes decimal separator.

    Returns:
    - x: formatted number
    """

    x: float|str

    
    if round_static==False:
        x=KFSmath.round_sig(x, precision)           # round to signifcant number
    else:
        x=round(x, precision)                       # round to decimal place static
        
    if x!=0:                                        # determine magnitude after rounding in case rounding changes magnitude
        magnitude=math.floor(math.log10(abs(x)))    # x magnitude floored
    else:
        magnitude=0                                 # for number 0 magnitude 0, practical for decimal prefix
    
    if round_static==False:
        dec_places=magnitude*-1+precision-1         # decimal places required
    else:
        dec_places=precision                        # decimal places required
    if dec_places<0:                                # at least 0 decimal places
        dec_places=0


    x=f"{x:0{width},.{dec_places}f}".replace(".", "%TEMP%").replace(",", ".").replace("%TEMP%", ",")    # int to str, comma as decimal separator
    
    if trailing_zeros==False and "," in x:  # if trailing zeros undesired and decimal places existing:
        x=x.rstrip("0")                     # remove trailing zeros
        if x[-1]==",":                      # if because of that last character comma:
            x=x[:-1]                        # remove comma


    return x


def notation_tech(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True, add_decimal_prefix: bool=True, width: int=0) -> str:   # converts to notation technical as string #type:ignore
    """
    Formats rounded number as string, changes magnitude for decimal prefixes (notation technical).

    Arguments:
    - x: number to format
    - precision:
        - if round_static==False: Round to significant digits.
        - if round_static==True: Round to magnitude 10^(-precision), like built-in round().
    - trailing_zeros: Append zeros until reached precision.
    - add_decimal_prefix: Append decimal prefix for units.
    - width: After appending trailing zeros, prepend zeros until reaching width. Width includes decimal separator.

    Returns:
    - x: formatted number

    Raises:
    - ValueError: There are only decimal prefixes for magnitudes [-30; 33[. There is no decimal prefix for given magnitude.
    """

    x: float|str

    
    if round_static==False:
        x=KFSmath.round_sig(x, precision)           # round to signifcant number
    else:
        x=round(x, precision)                       # round to decimal place static
        
    if x!=0:                                        # determine magnitude after rounding in case rounding changes magnitude
        magnitude=math.floor(math.log10(abs(x)))    # x magnitude floored
    else:
        magnitude=0                                 # for number 0 magnitude 0, practical for decimal prefix
    
    if round_static==False:
        dec_places=magnitude%3*-1+precision-1       # decimal places required
    else:
        dec_places=magnitude-magnitude%3+precision  # decimal places required
    if dec_places<0:                                # at least 0 decimal places
        dec_places=0

    x=f"{x/math.pow(10, magnitude-magnitude%3):0{width}.{dec_places}f}".replace(".", ",")   # int to str, to correct magnitude and number of decimal places, comma as decimal separator
    
    if trailing_zeros==False and "," in x:  # if trailing zeros undesired and decimal places existing:
        x=x.rstrip("0")                     # remove trailing zeros
        if x[-1]==",":                      # if because of that last character comma:
            x=x[:-1]                        # remove comma
    
    if add_decimal_prefix==True:    # if decimal prefix desired: append
        if    30<=magnitude and magnitude< 33:
            x+="Q"
        elif  27<=magnitude and magnitude< 30:
            x+="R"
        elif  24<=magnitude and magnitude< 27:
            x+="Y"
        elif  21<=magnitude and magnitude< 24:
            x+="Z"
        elif  18<=magnitude and magnitude< 21:
            x+="E"
        elif  15<=magnitude and magnitude< 18:
            x+="P"
        elif  12<=magnitude and magnitude< 15:
            x+="T"
        elif   9<=magnitude and magnitude< 12:
            x+="G"
        elif   6<=magnitude and magnitude<  9:
            x+="M"
        elif   3<=magnitude and magnitude<  6:
            x+="k"
        elif   0<=magnitude and magnitude<  3:
            x+=""
        elif  -3<=magnitude and magnitude<  0:
            x+="m"
        elif  -6<=magnitude and magnitude< -3:
            x+="µ"
        elif  -9<=magnitude and magnitude< -6:
            x+="n"
        elif -12<=magnitude and magnitude< -9:
            x+="p"
        elif -15<=magnitude and magnitude<-12:
            x+="f"
        elif -18<=magnitude and magnitude<-15:
            x+="a"
        elif -21<=magnitude and magnitude<-18:
            x+="z"
        elif -24<=magnitude and magnitude<-21:
            x+="y"
        elif -27<=magnitude and magnitude<-24:
            x+="r"
        elif -30<=magnitude and magnitude<-27:
            x+="q"
        else:
            raise ValueError(f"Error in {notation_tech.__name__}{inspect.signature(notation_tech)}: There are only decimal prefixes for magnitudes [-30; 33[. There is no decimal prefix for given magnitude {magnitude}.")
        

    return x


colour_i=0  # which colour currently? memorise for continueing at next function call
def rainbowify(string_in: str) -> str:
    """
    Dyes input string to rainbow.

    Arguments:
    - string_in: string that should be rainbowified

    Returns:
    - string_out: rainbowified string
    """
    import colorama
    global colour_i
    string_out: str=""          # result
    RAINBOW_COLOURS: list=[     # dye definition
        colorama.Fore.MAGENTA,
        colorama.Fore.RED,
        colorama.Fore.YELLOW,
        colorama.Fore.GREEN,
        colorama.Fore.CYAN,
        colorama.Fore.BLUE,
    ]

    if sys.platform=="win32" or sys.platform=="cygwin": # if windows:
        colorama.just_fix_windows_console()             # enable colours on windows console


    for char in string_in:
        string_out+=RAINBOW_COLOURS[colour_i]           # dye
        string_out+=char                                # append character
        if char!=" ":                                   # if no space:
            colour_i=(colour_i+1)%len(RAINBOW_COLOURS)  # colour next
    string_out+=colorama.Style.RESET_ALL                # reset colours

    return string_out