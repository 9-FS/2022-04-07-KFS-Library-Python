# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import copy                         # deep copy
import datetime as dt               # datetime
import enum                         # enum
import inspect                      # exception message with function header
import logging, logging.handlers    # standard logging
import math                         # math.ceil
import os
import sys                          # current system for colour enabling on windows
import typing                       # type hints
from . import fstr # notation technical


COLORAMA_IMPORTED: bool
try:
    import colorama         # coloured logs
except ModuleNotFoundError: # if colorama could not be imported:
    COLORAMA_IMPORTED=False # no colours
else:                       # if colorama could be imported:
    COLORAMA_IMPORTED=True  # coloured logs


def setup_logging(logger_name: str="",
                  logging_level: int=logging.INFO,
                  message_format: str="[%(asctime)s] %(levelname)s %(message)s",
                  timestamp_format: str="%Y-%m-%dT%H:%M:%S",
                  print_to_console: bool=True,
                  print_to_logfile: bool=True,
                  filepath_format: str="./log/%Y-%m-%d.log",
                  rotate_filepath_when: str="midnight") -> logging.Logger:
    """
    Setup logging to console and log file.
    - Timestamps are only printed if they changed from timestamp of previous line.
    - Messages with linebreaks are properly indented.
    - "\r" at the beginning of a message overwrites line in console.
    - Logging levels are colour-coded.
    - Log files have have a custom name format depending on the current datetime.

    Arguments:
    - logger_name: name for logging.Logger
    - logging_level: Every logging.LogRecord with lower logging level than specified here will be ignored.
    - message_format: basic structure on how to print a logging.LogRecord
    - timestamp_format: basic structure on how to print a timestamp (\"%(asctime)s\")
    - print_to_console: print to console or nah, can significantly speed up program
    - print_to_logfile: print to logfile or nah
    - filepath_format: basic structure of a logfile name
    - rotate_filepath_when: when to refresh logfile name with current datetime, read more at https://docs.python.org/3/library/logging.handlers.html# timedrotatingfilehandler
    """

    logger=logging.getLogger(logger_name)   # create logger with name
    logger.setLevel(logging_level)          # set logging level
    logger.handlers=[]                      # remove all already existing handlers to avoid duplicates
    
    if print_to_console==True:
        console_handler=logging.StreamHandler()
        console_handler.setFormatter(_Console_File_Formatter(_Console_File_Formatter.Output.console, message_format, datefmt=timestamp_format))
        console_handler.terminator=""       # no automatic newline at the end, custom formatter handles newlines
        logger.addHandler(console_handler)

    if print_to_logfile==True:
        file_handler=_TimedFileHandler(filepath_format, when=rotate_filepath_when, encoding="utf-8", utc=True)
        file_handler.setFormatter(_Console_File_Formatter(_Console_File_Formatter.Output.file, message_format, datefmt=timestamp_format))
        file_handler.terminator=""          # no automatic newline at the end, custom formatter handles newlines
        logger.addHandler(file_handler)

    if COLORAMA_IMPORTED==False:    # if colorama could not be imported: first record of logger will be this warning
        logger.warning("Package \"colorama\" is not installed, logging levels will not be coloured. Fix this with `pip install colorama`.")
    
    return logger   # return logger in case needed


class _Console_File_Formatter(logging.Formatter):
    """
    Formats logging.LogRecord to my personal preferences.
    - Timestamps are only printed if they changed from timestamp of previous line.
    - Messages with linebreaks are properly indented.
    - "\\r" at the beginning of a message overwrites line.
    - Logging levels are colour-coded.
    """

    class Output(enum.Enum):    # is this a formatter for console or log file?
        console=enum.auto()
        file   =enum.auto()
    

    def __init__(self, output: Output, fmt: str|None=None, datefmt: str|None=None, style: str="%", validate: bool=True, defaults: str|None=None) -> None:
        self.init_args={    # save arguments to forward to actual logging.Formatter later
            "output": output,
            "fmt": fmt,
            "datefmt": datefmt,
            "style": style,
            "validate": validate,
            "defaults": defaults
        }

        self.line_previous_len=100      # line previous length, so can be overwritten cleanly if desired
        self.timestamp_previous=""      # timestamp used in previous logging call
        self.timestamp_previous_line="" # timestamp used in previous line
        return
    
    
    @staticmethod
    def _dye_logging_level(format: str, logging_level: int) -> str:
        """
        Dyes the logging level part of the format string.
        """
        LEVEL_COLOURS={    # which level gets which colour?
            logging.DEBUG:    colorama.Fore.WHITE,
            logging.INFO:     colorama.Fore.GREEN+colorama.Style.BRIGHT,
            logging.WARNING:  colorama.Back.YELLOW+colorama.Fore.BLACK,
            logging.ERROR:    colorama.Back.RED+colorama.Fore.BLACK,
            logging.CRITICAL: colorama.Back.RED+colorama.Fore.WHITE+colorama.Style.BRIGHT
        }
        if sys.platform=="win32" or sys.platform=="cygwin": # if windows:
            colorama.just_fix_windows_console()             # enable colours on windows console
        return format.replace("%(levelname)s", LEVEL_COLOURS[logging_level]+"%(levelname)s"+colorama.Style.RESET_ALL)


    def format(self, record):
        """
        Implements personal preferences by changing message and format. Creates custom formatter, then formats record.
        """

        overwrite_line_current: bool                                                            # overwrite line previously written?
        timestamp_current=dt.datetime.now(dt.timezone.utc).strftime(self.init_args["datefmt"])  # timestamp current

        fmt=self.init_args["fmt"]       # get original format
        record=copy.deepcopy(record)    # deep copy record so changes here don't affect other formatters
        record.msg=str(record.msg)      # convert msg to str, looses the additional data of the original object but is not needed anyways, just used as string here
        

        if "\n" in record.msg:          # if newline in message: indent coming lines
            newline_replacement="\n"    # initialise with newline, add preceding spaces next
            number_of_spaces=0          # number of spaces needed for indentation
            
            number_of_spaces+=len(fmt.split(r"%(message)s", 1)[0].replace(r"%(asctime)s", "").replace(r"%(levelname)s", ""))    # static format length without variables, for indentation only consider what is left of first %(message)s
            if r"%(asctime)s" in fmt:                                   # if timestamp in format: determine length
                number_of_spaces+=len(timestamp_current)
            if r"%(levelname)s" in fmt:                                 # if logging level in format: determine length
                number_of_spaces+=len(record.levelname)
            for i in range(number_of_spaces):                           # add indentation
                newline_replacement+=" " 
            record.msg=record.msg.replace("\n", newline_replacement)    # replace all linebreaks with linebreak + indentation
        
        match self.init_args["output"]:
            case self.Output.console:                                       # if output console:
                if record.msg.startswith("\r"):                             # if record.msg starts with carriage return: prepare everything for overwriting line previous later
                    overwrite_line_current=True                             # overwrite line later
                    print("\x1b[1A\r", end="")                              # jump to line previous, then to beginning
                    for i in range(math.ceil(self.line_previous_len/10)):   # clear line previous
                        print("          ", end="")
                    print("", end="", flush=True)
                    fmt=f"\r{fmt}\n"                                        # change format to write carriage return first and write newline at end
                    record.msg=record.msg[1:]                               # remove carriage return from message
                else:                                                       # if writing in new line:
                    overwrite_line_current=False                            # don't overwrite line later
                    fmt=f"{fmt}\n"                                          # change format to just write newline at end
            case self.Output.file:              # if output log file:
                overwrite_line_current=False    # don't overwrite line later
                fmt=f"{fmt}\n"                  # change format to write newline at end
                if record.msg[0:1]=="\r":
                    record.msg=record.msg[1:]   # remove carriage return from message
            case _: # if invalid formatter output
                raise RuntimeError(f"Error in {format.__name__}{inspect.signature(format)}: Invalid formatter output \"{self.init_args['output'].name}\".")
        
        if overwrite_line_current==False:                           # if we write in line new:
            self.timestamp_previous_line=self.timestamp_previous    # update timestamp previous line to timestamp previously used

        if self.timestamp_previous_line==timestamp_current: # if timestamp of line previous same as current: replace timestamp with indentation
            timestamp_replacement=""
            for i in range(+len(f"[{self.timestamp_previous_line}]")):
                timestamp_replacement+=" "
            fmt=fmt.replace(r"[%(asctime)s]", timestamp_replacement)

        
        if self.init_args["output"]==self.Output.console and COLORAMA_IMPORTED==True:                                       # if in console output and colorama imported:
            fmt=_Console_File_Formatter._dye_logging_level(fmt, record.levelno)                                             # dye logging level
        formatter=logging.Formatter(fmt, self.init_args["datefmt"], self.init_args["style"], self.init_args["validate"])    # create custom formatter 
        record.msg=formatter.format(record)                                                                                 # finally format message
        
        self.line_previous_len=len(record.msg)      # save line length, so can be overwritten cleanly next call if desired
        self.timestamp_previous=timestamp_current   # timestamp current becomes timestamp previously used for next logging call
        return record.msg                           # return formatted message

class _TimedFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Instead of having a static baseFilename and then adding suffixes during rotation, this file handler takes a **datetime format filepath** and changes baseFilename according to the given datetime format and the current datetime.
    Rotating is just redoing this process with the new current datetime.
    """

    def __init__(self, filepath_format: str, when: str="h", interval: int=1, backupCount: int=0, encoding: str|None=None, delay: bool=False, utc: bool=False, atTime: dt.time|None=None, errors: str|None=None) -> None:
        os.makedirs(os.path.dirname(filepath_format), exist_ok=True)    # create necessary directories
        super(_TimedFileHandler, self).__init__(filepath_format, when, interval, backupCount, encoding, delay, utc, atTime, errors) # execute base class constructor
        self.close()                                                    # base class already opens file with wrong name, close again
        try:
            os.remove(self.baseFilename)                                # try to remove wrong file
        except OSError:
            pass
        self.baseFilename_format=self.baseFilename                      # user argument is interpreted as filepath with datetime format, not static filepath
        
        if self.utc==False:
            self.baseFilename=dt.datetime.now().strftime(self.baseFilename_format)  # set filepath with format and current datetime
        else:
            self.baseFilename=dt.datetime.now(dt.timezone.utc).strftime(self.baseFilename_format)
        return

    def rotator(self, source, dest) -> None:    # rotate by setting new self.baseFilename with format and current datetime
        if self.utc==False:
            self.baseFilename=dt.datetime.now().strftime(self.baseFilename_format)
        else:
            self.baseFilename=dt.datetime.now(dt.timezone.utc).strftime(self.baseFilename_format)
        return


T=typing.TypeVar("T", bound=typing.Callable)    # pass type hints through decorator, so static type checkers in IDE still work
def timeit(f: T) -> T:
    """
    Decorates function with "Executing function()...", "Executed function()=result.\\nDuration: t"
    """

    def function_new(*args, **kwargs):          # function modified to return
        logger: logging.Logger                  # logger
        y=None                                  # function return value

        if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
            logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
        else:                                       # if no root logger defined:
            logger=setup_logging("KFS")             # use KFS default format


        logger.info(f"Executing {f.__name__}{inspect.signature(f)}...")
        t0=dt.datetime.now(dt.timezone.utc)
        try:
            y=f(*args, **kwargs)    # execute function to decorate
        except:                     # crashes
            t1=dt.datetime.now(dt.timezone.utc)
            execution_time=(t1-t0).total_seconds()
            if f.__name__!="main":  # if not main crashed: error
                logger.error(f"Tried to execute {f.__name__}{inspect.signature(f)}, but crashed.\nDuration: {fstr.notation_tech(execution_time, 4)}s")
            else:                   # if main crashed: critical
                logger.critical(f"Tried to execute {f.__name__}{inspect.signature(f)}, but crashed.\nDuration: {fstr.notation_tech(execution_time, 4)}s")
            raise                   # forward exception
               
        t1=dt.datetime.now(dt.timezone.utc)
        execution_time=(t1-t0).total_seconds()
        logger.info(f"Executed {f.__name__}{inspect.signature(f)} = {str(y)}.\nDuration: {fstr.notation_tech(execution_time, 4)}s")
        
        return y
    
    return typing.cast(T, function_new)


T=typing.TypeVar("T", bound=typing.Callable)    # pass type hints through decorator, so static type checkers in IDE still work
def timeit_async(f: T) -> T:
    """
    Decorates function with "Executing function()...", "Executed function()=result.\\nDuration: t"
    """

    async def function_new(*args, **kwargs):    # function modified to return
        logger: logging.Logger                  # logger
        y=None                                  # function return value

        if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
            logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
        else:                                       # if no root logger defined:
            logger=setup_logging("KFS")             # use KFS default format


        logger.info(f"Executing {f.__name__}{inspect.signature(f)}...")
        t0=dt.datetime.now(dt.timezone.utc)
        try:
            y=await f(*args, **kwargs)  # execute function to decorate
        except:                         # crashes
            t1=dt.datetime.now(dt.timezone.utc)
            execution_time=(t1-t0).total_seconds()
            if f.__name__!="main":      # if not main crashed: error
                logger.error(f"Tried to execute {f.__name__}{inspect.signature(f)}, but crashed.\nDuration: {fstr.notation_tech(execution_time, 4)}s")
            else:                       # if main crashed: critical
                logger.critical(f"Tried to execute {f.__name__}{inspect.signature(f)}, but crashed.\nDuration: {fstr.notation_tech(execution_time, 4)}s")
            raise                       # forward exception
               
        t1=dt.datetime.now(dt.timezone.utc)
        execution_time=(t1-t0).total_seconds()
        logger.info(f"Executed {f.__name__}{inspect.signature(f)} = {str(y)}.\nDuration: {fstr.notation_tech(execution_time, 4)}s")
        
        return y
    
    return typing.cast(T, function_new)