import math


def notation_tech(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True, add_decimal_prefix: bool=True) -> str: #Notation technisch, gibt String zurück
    try:
        x=float(x)
    except ValueError:
        raise TypeError("Error in KFS::fstr::notation_tech(...): Type of \"x\" must be float or convertable to float.")
    if type(precision)!=int:
        raise TypeError("Error in KFS::fstr::notation_tech(...): Type of \"precision\" must be int.")
    if type(round_static)!=bool:
        raise TypeError("Error in KFS::fstr::notation_tech(...): Type of \"round_static\" must be bool.")
    if type(trailing_zeros)!=bool:
        raise TypeError("Error in KFS::fstr::notation_tech(...): Type of \"add_decimal_prefix\" must be bool.")
    if type(add_decimal_prefix)!=bool:
        raise TypeError("Error in KFS::fstr::notation_tech(...): Type of \"add_decimal_prefix\" must be bool.")
    

    if x!=0:
        magnitude=math.floor(math.log10(abs(x)))    #x Größenordnung, abgerundet
    else:
        magnitude=0                                 #für 0 Größenordnung 0 sinnvoll wegen Dezimalpräfix
    
    if round_static==False:
        x=math.round_sig(x, precision)           #runden auf Signifikante
        dec_places=magnitude%3*-1+precision-1       #Nachkommastellen benötigt
    else:
        x=round(x, precision)                       #runden auf Nachkommastelle statisch
        dec_places=magnitude-magnitude%3+precision  #Nachkommastellen benötigt
    if dec_places<0:                                #0 Nachkommastellen mindestens
        dec_places=0


    x=f"{x/math.pow(10, magnitude-magnitude%3):.{dec_places}f}".replace(".", ",")   #int zu str, auf richtige Dezimalmagnitude und Nachkommastellen, Komma als Dezimalseperator
    
    if trailing_zeros==False and "," in x:  #wenn Trailing Zeros unerwünscht und Nachkommabereich vorhanden:
        x=x.rstrip("0")                     #Trailing Zeros entfernen
        if x[-1]==",":                      #wenn dadurch Zeichen letztes Komma:
            x=x[:-1]                        #Komma entfernen
    
    if add_decimal_prefix==True:    #wenn Dezimalpräfix erwünscht: anhängen
        if    24<=magnitude and magnitude< 27:
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
        else:
            raise ValueError(f"Error in KFS::fstr::notation_tech(...): There are only decimal prefixes for magnitudes [-24; 27[. There is no decimal prefix for given magnitude {magnitude}.")
        

    return x