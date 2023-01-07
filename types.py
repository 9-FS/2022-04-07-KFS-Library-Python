from enum import Enum
import inspect
import typing


class Mode(Enum):   #type check modes
    strict=0        #argument type must be like type hint
    instance=1      #argument type must be instance (like type hint or inherited), default
    convertable=2   #argument type must be convertable to type hint type
    whatever=3      #argument type does not matter


def check(f: typing.Callable, locals: dict, *modes: Mode) -> None:
    if isinstance(f, typing.Callable)==False:
        raise ValueError("Error in KFS::typecheck::check(...): Argument f must be callable, use your local function.")
    if isinstance(locals, dict)==False:
        raise ValueError("Error in KFS::typecheck::check(...): Argument locals must be instance of type dict, use the locals() function.")
    for mode in modes:
        if type(mode)!=Mode:
            raise ValueError("Error in KFS::typecheck::check(...): Given modes must be of type KFS::typecheck::Mode.")
    #ValueError and not TypeError, because TypeError is expected when an argument of f has wrong type


    type_hints=typing.get_type_hints(f) #type hints used by f, dict with name: type
    try:
        del type_hints["return"]    #ignore type hint for return value
    except KeyError:                #if didn't exist in the first place: okay weird, but do nothing
        pass
    
    if len(type_hints)!=len(modes): #number of given modes must be equal to number of given type hints, otherwise don't know which mode refers to which parameter
        raise ValueError(f"Error in KFS::typecheck::check(...): Number of given modes ({len(modes)}) does not match number of used type hints ({len(type_hints)}).")

    
    for i, parameter in enumerate(type_hints):  #loop through all type hints and check whether parameter has correct type
        if modes[i]==Mode.strict:                               #if mode strict:
            if type(locals[parameter])!=type_hints[parameter]:  #parameter type must be type hint type
                raise TypeError(f"Error in {f.__name__}{inspect.signature(f)}: {parameter} must be of type {type_hints[parameter]}, but {type(locals[parameter])}={locals[parameter]} was given.")
        
        elif modes[i]==Mode.instance:                                       #if mode instance:
            if isinstance(locals[parameter], type_hints[parameter])==False: #parameter type must be type hint type or subclass
                raise TypeError(f"Error in {f.__name__}{inspect.signature(f)}: {parameter} must be instance of type {type_hints[parameter]}, but {type(locals[parameter])}={locals[parameter]} was given.")
        
        elif modes[i]==Mode.convertable:                    #if mode conversion:
            try:
                type_hints[parameter](locals[parameter])    #try conversion from parameter type to type hint type
            except (TypeError, ValueError):
                raise TypeError(f"Error in {f.__name__}{inspect.signature(f)}: {parameter} must be convertable to type {type_hints[parameter]}, but {type(locals[parameter])}={locals[parameter]} was given.")
        
        elif modes[i]==Mode.whatever:   #if mode whatever: ignore
            pass
        else:                           #if mode impossible: wtf
            raise RuntimeError("Error in KFS::typecheck::check(...): Unknown mode.")
    
    return

#TODO typecheck nested types
#TODO make compatible with decorators
#TODO inspect contents of *args **kwargs