import datetime as dt
import math                 #floor
import os
from threading import Lock  #mutex
import typing               #type hints
from . import fstr          #notation technical
from . import typecheck     #typecheck


line_last_len=0                 #line previous length, if override desired
timestamp_old=""                #timestamp previously used
timestamp_old_line_previous=""  #timestamp previously  used on line previous
write_mutex=Lock()              #make everything thread safe


def write(text: str,
          append_to_line_current: bool=False,
          UNIX_time: bool=False,
          write_on_console: bool=True,
          write_in_file: bool=True) -> None:    #writes log
    global line_last_len
    global timestamp_old
    global timestamp_old_line_previous
    newline_replacement="\n"        #what should replace normal linebreaks? linebreak + indentation
    overwrite_line_current=False    #overwrite line previously written?
    timestamp=""                    #timestamp in front of log entry, either timestamp or spaces if timestamp would be same as previous
    timestamp_in_console=""         #add timestamp in console log ("none", "just spaces", "full")
    timestamp_in_file=""            #add timestamp in log file ("none", "just spaces", "full")
    timestamp_new=""                #timestamp current, only use with mode "full"


    typecheck.check(write, locals(), typecheck.Mode.convertable, typecheck.Mode.instance, typecheck.Mode.instance, typecheck.Mode.instance, typecheck.Mode.instance)
    text=str(text)


    DT_now=dt.datetime.now(dt.timezone.utc)                                         #datetime now
    if UNIX_time==False:                                                            #if not unix time:
        timestamp_new=f"[{DT_now.strftime('%Y-%m-%dT%H:%M:%SZ')}]"                  #timestamp new according ISO8601
    else:
        timestamp_new=f"[{math.floor(DT_now.timestamp()):,.0f}]".replace(",", ".")  #timestamp new in unix time
    
    os.makedirs("./Log/", exist_ok=True)    #create log folder

    with write_mutex:                   #from now on lock other threads out because now working with variables global
        if text[0:1]=="\r":             #if character [0] carriage return: clear and overwrite line previous
            overwrite_line_current=True #overwrite
            if write_on_console==True:
                print("\r", end="", flush=True)
                for i in range(math.ceil(line_last_len/100)):
                    print("                                                                                                    ", end="")
            text=text[1:]               #remove carriage return

        for i in range(len(timestamp_new)+1):           #add indentation
            newline_replacement+=" " 
        text=text.replace("\n", newline_replacement)    #replace all linebreaks with linebreaks + indentation

        line_last_len=len(timestamp_new)+1+len(text)    #memorise line length for clean possible override later
        
        if overwrite_line_current==False and append_to_line_current==False and timestamp_old!="":   #if line new:
            timestamp_old_line_previous=timestamp_old                                               #update timestamp to line previous
        if timestamp_old_line_previous!=timestamp_new:  #if timestamp different than from line previous:
            timestamp_in_console="full"                 #in console show timestamp
        else:                                           #if timestamp equal to line previous
            timestamp_in_console="just spaces"          #no timestamp, only indentation
        if timestamp_old!=timestamp_new:        #if timestamp different than before:
            timestamp_in_file="full"            #in logfile write timestamp
        else:                                   #if timestamp equal to before:
            timestamp_in_file="just spaces"     #no timestamp, only indentation

        if overwrite_line_current==True:    #if overwrite line current:
            if write_on_console==True:
                print("\r", end="")         #in console carriage return
            if write_in_file==True:
                with open(f"./Log/{DT_now.strftime('%Y-%m-%d Log.txt')}", "at", encoding="utf-8") as log_file:    
                    log_file.write(f"\n")   #but in log file line break
            timestamp_old=timestamp_new     #update timestamp previous
        elif append_to_line_current==True:  #if append to line current:
            timestamp_in_console="none"     #ignore default timestamp settings, never any timestamp, never any indentation
            timestamp_in_file="none"
        else:                           #if line new:
            if write_on_console==True:
                print("\n", end="")         #in console line break
            if write_in_file==True:
                with open(f"./Log/{DT_now.strftime('%Y-%m-%d Log.txt')}", "at", encoding="utf-8") as log_file:
                    log_file.write(f"\n")   #in log file line break
            timestamp_old=timestamp_new     #update timestamp previous
    

        if write_on_console==True:
            if timestamp_in_console=="full":            #if timestamp desired:
                timestamp=f"{timestamp_new} "
            elif timestamp_in_console=="just spaces":   #if indentation desired:
                for i in range(len(timestamp_old)+1):
                    timestamp+=" "                      #no timestamp, only indentation
            elif timestamp_in_console=="none":          #if nothing desired:
                timestamp=""
            else:
                raise RuntimeError(f"Error in KFS::log::write(...): timestamp_in_console has invalid value which should not occur (\"{timestamp_in_console}\").")
            print(f"{timestamp}{text}", end="", flush=True)
            timestamp=""    #before determining timestamp for log file: reset
        
        if write_in_file==True:
            if timestamp_in_file=="full":               #if timestamp desired:
                timestamp=f"{timestamp_new} "
            elif timestamp_in_file=="just spaces":      #if indentation desired:
                for i in range(len(timestamp_old)+1):
                    timestamp+=" "                      #no timestamp, only indentation
            elif timestamp_in_file=="none":             #if nothing desired:
                timestamp=""
            else:
                raise RuntimeError(f"Error in KFS::log::write(...): timestamp_in_file has invalid value which should not occur (\"{timestamp_in_file}\").")
            with open(f"./Log/{DT_now.strftime('%Y-%m-%d Log.txt')}", "at", encoding="utf-8") as log_file:
                log_file.write(f"{timestamp}{text}")

    return


T=typing.TypeVar("T", bound=typing.Callable)    #pass type hints through decorator, so static type checkers in IDE still work
def timeit(f: T) -> T:                          #decorates function with "Executing...", "Executed, took t seconds"
    def function_new(*args, **kwargs):          #function modified to return
        function_signature=""                   #function(parameters)
        y=None                                  #function return value


        function_signature=f"{f.__name__}("     #function(
        
        for i, arg in enumerate(args):          #paramters unnamed args
            function_signature+=str(arg)
            if i<len(args)-1 or 0<len(kwargs):
                function_signature+=", "
        
        for i, kwarg in enumerate(kwargs):      #parameters named kwargs
            function_signature+=f"{kwarg}={str(kwargs[kwarg])}"
            if i<len(kwargs)-1:
                function_signature+=", "
        
        function_signature+=")"
        

        write(f"Executing {function_signature}...")
        t0=dt.datetime.now(dt.timezone.utc)
        try:
            y=f(*args, **kwargs)    #execute function to decorate
        except:                     #crashes
            t1=dt.datetime.now(dt.timezone.utc)
            execution_time=(t1-t0).total_seconds()
            write(f"Tried to execute {function_signature}, but crashed. Duration: {fstr.notation_tech(execution_time, 4)}s.")
            raise   #forward exception
               
        t1=dt.datetime.now(dt.timezone.utc)
        execution_time=(t1-t0).total_seconds()
        write(f"Executed {function_signature}={str(y)}. Duration: {fstr.notation_tech(execution_time, 4)}s.")
        
        return y
    
    return typing.cast(T, function_new)