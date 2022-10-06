from enum import Enum
import inspect
import typing


class Mode(Enum):   #Typcheckmodi
    strict=0        #Argumenttyp muss Typtipp sein
    convertable=1   #Argumenttyp muss konvertierbar zu Typtipp sein
    whatever=2      #Argumenttyp ist egal


def check(f: typing.Callable, locals: dict, *modes: Mode) -> None:
    type_hints=typing.get_type_hints(f) #Datentyptipps verwendet
    

    try:
        del type_hints["return"]    #Rückgabedatentyptipp ignorieren
    except KeyError:                #wenn vorher schon nicht existiert: okay subba, nix tun
        pass
    
    if len(type_hints)!=len(modes): #Modusanzahl muss passen zu Datentippanzahl
        raise ValueError("Error in KFS::typecheck::check(...): Number of given modes does not match number of used type hints.")

    
    for i, parameter in enumerate(type_hints):  #alle Datentyptipps durchgehen und schauen, ob Parameter Anforderung entspricht
        if modes[i]==Mode.strict:                               #wenn Modus streng:
            if type(locals[parameter])!=type_hints[parameter]:  #Parametertyp muss Datentipptyp sein
                raise TypeError(f"Error in {f.__name__}{inspect.signature(f)}: {parameter} must be of type {type_hints[parameter]}, but {type(locals[parameter])} was given.")
        
        elif modes[i]==Mode.convertable:    #wenn Modus Parametertyp muss konvertierbar sein zu Datentipptyp:
            try:
                type_hints[parameter](locals[parameter])    #Konvertierung versuchen von Parametertyp zu Datentipptyp
            except ValueError:
                raise TypeError(f"Error in {f.__name__}{inspect.signature(f)}: {parameter} must be convertable to type {type_hints[parameter]}, but {type(locals[parameter])} was given.")
        
        elif modes[i]==Mode.whatever:   #wenn Modus egal: ignorieren
            pass
        else:                           #wenn Modus unmöglich: wtf
            raise RuntimeError("Error in KFS::typecheck::check(...): Unknown mode.")
    
    return