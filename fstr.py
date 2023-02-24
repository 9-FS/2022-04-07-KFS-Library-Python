import inspect
import math
from . import math as KFSmath   #for round_sig, must "as KFSmath" because otherwise name conflict with math


def notation_abs(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True) -> str: #converts to formatted rounded number (notation absolute) as string, no changing of magnitude for decimal prefixes
    x=float(x)

    
    if round_static==False:
        x=KFSmath.round_sig(x, precision)           #round to signifcant number
    else:
        x=round(x, precision)                       #round to decimal place static
        
    if x!=0:                                        #determine magnitude after rounding in case rounding changes magnitude
        magnitude=math.floor(math.log10(abs(x)))    #x magnitude floored
    else:
        magnitude=0                                 #for number 0 magnitude 0, practical for decimal prefix
    
    if round_static==False:
        dec_places=magnitude*-1+precision-1         #decimal places required
    else:
        dec_places=precision                        #decimal places required
    if dec_places<0:                                #at least 0 decimal places
        dec_places=0


    x=f"{x:,.{dec_places}f}".replace(".", "%TEMP%").replace(",", ".").replace("%TEMP%", ",")   #int to str, comma as decimal separator #type:ignore
    
    if trailing_zeros==False and "," in x:  #if trailing zeros undesired and decimal places existing: #type:ignore
        x=x.rstrip("0")                     #remove trailing zeros #type:ignore
        if x[-1]==",":                      #if because of that last character comma: #type:ignore
            x=x[:-1]                        #remove comma #type:ignore


    return x #type:ignore


def notation_tech(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True, add_decimal_prefix: bool=True) -> str: #converts to notation technical as string
    x=float(x)

    
    if round_static==False:
        x=KFSmath.round_sig(x, precision)           #round to signifcant number
    else:
        x=round(x, precision)                       #round to decimal place static
        
    if x!=0:                                        #determine magnitude after rounding in case rounding changes magnitude
        magnitude=math.floor(math.log10(abs(x)))    #x magnitude floored
    else:
        magnitude=0                                 #for number 0 magnitude 0, practical for decimal prefix
    
    if round_static==False:
        dec_places=magnitude%3*-1+precision-1       #decimal places required
    else:
        dec_places=magnitude-magnitude%3+precision  #decimal places required
    if dec_places<0:                                #at least 0 decimal places
        dec_places=0

    x=f"{x/math.pow(10, magnitude-magnitude%3):.{dec_places}f}".replace(".", ",")   #int to str, to correct magnitude and number of decimal places, comma as decimal separator #type:ignore
    
    if trailing_zeros==False and "," in x:  #if trailing zeros undesired and decimal places existing: #type:ignore
        x=x.rstrip("0")                     #remove trailing zeros #type:ignore
        if x[-1]==",":                      #if because of that last character comma: #type:ignore
            x=x[:-1]                        #remove comma #type:ignore
    
    if add_decimal_prefix==True:    #if decimal prefix desired: append
        if    30<=magnitude and magnitude< 33:
            x+="Q" #type:ignore
        elif  27<=magnitude and magnitude< 30:
            x+="R" #type:ignore
        elif  24<=magnitude and magnitude< 27:
            x+="Y" #type:ignore
        elif  21<=magnitude and magnitude< 24:
            x+="Z" #type:ignore
        elif  18<=magnitude and magnitude< 21:
            x+="E" #type:ignore
        elif  15<=magnitude and magnitude< 18:
            x+="P" #type:ignore
        elif  12<=magnitude and magnitude< 15:
            x+="T" #type:ignore
        elif   9<=magnitude and magnitude< 12:
            x+="G" #type:ignore
        elif   6<=magnitude and magnitude<  9:
            x+="M" #type:ignore
        elif   3<=magnitude and magnitude<  6:
            x+="k" #type:ignore
        elif   0<=magnitude and magnitude<  3:
            x+="" #type:ignore
        elif  -3<=magnitude and magnitude<  0:
            x+="m" #type:ignore
        elif  -6<=magnitude and magnitude< -3:
            x+="µ" #type:ignore
        elif  -9<=magnitude and magnitude< -6:
            x+="n" #type:ignore
        elif -12<=magnitude and magnitude< -9:
            x+="p" #type:ignore
        elif -15<=magnitude and magnitude<-12:
            x+="f" #type:ignore
        elif -18<=magnitude and magnitude<-15:
            x+="a" #type:ignore
        elif -21<=magnitude and magnitude<-18:
            x+="z" #type:ignore
        elif -24<=magnitude and magnitude<-21:
            x+="y" #type:ignore
        elif -27<=magnitude and magnitude<-24:
            x+="r" #type:ignore
        elif -30<=magnitude and magnitude<-27:
            x+="q" #type:ignore
        else:
            raise ValueError(f"Error in {notation_tech.__name__}{inspect.signature(notation_tech)}: There are only decimal prefixes for magnitudes [-24; 27[. There is no decimal prefix for given magnitude {magnitude}.")
        

    return x #type:ignore