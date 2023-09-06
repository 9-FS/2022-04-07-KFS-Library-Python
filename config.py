# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import inspect
import logging
import os
from . import log


def load_config(filepath: str, default_content: str="", empty_ok: bool=False) -> str:
    """
    Tries to load from \"filepath\" and return text content.
    
    If file does not exist, creates with \"default_content\" and raises FileNotFoundError.

    If file does not exist because it is a directory, raises IsADirectoryError.

    If empty_ok is false and file does exist but is empty, returns ValueError.

    If empty_ok is true and file does exist but is empty, returns empty string.
    """

    filecontent: str
    logger: logging.Logger  # logger
    
    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=log.setup_logging("KFS")         # use KFS default format
        
    if os.path.isfile(filepath)==False and os.path.isdir(filepath)==False:  # if input configuration file does not exist yet: create a default one and print instructions
        logger.error(f"Loading \"{filepath}\" is not possible, because file does not exist.")
        logger.info(f"Creating default \"{filepath}\"...")
        try:
            if os.path.dirname(filepath)!="":
                os.makedirs(os.path.dirname(filepath), exist_ok=True)   # create folders
            with open(filepath, "wt") as file:                          # create file
                file.write(default_content)                             # fill with default content
        except OSError:
            logger.error(f"Creating default \"{filepath}\" failed.")
        else:
            logger.info(f"\rCreated default \"{filepath}\".")
        raise FileNotFoundError(f"Error in {load_config.__name__}{inspect.signature(load_config)}: Loading \"{filepath}\" is not possible, because file did not exist.")
    elif os.path.isfile(filepath)==False and os.path.isdir(filepath)==True:
        logger.error(f"Loading \"{filepath}\" is not possible, because it is a directory. Unable to create default file.")
        raise IsADirectoryError(f"Error in {load_config.__name__}{inspect.signature(load_config)}: Loading \"{filepath}\" is not possible, because it is a directory. Unable to create default file.")


    logger.info(f"Loading \"{filepath}\"...")
    try:
        with open(filepath, "rt") as file:  # read file
            filecontent=file.read()
    except OSError:                         # write to log, then forward exception
        logger.error(f"Loading \"{filepath}\" failed.")
        raise
    
    if filecontent=="" and empty_ok==False:                         # but if content is empty and not allowed empty:
        logger.error(f"\rLoaded \"{filepath}\", but it is empty.")  # error
        raise ValueError(f"Error in {load_config.__name__}{inspect.signature(load_config)}: Loaded \"{filepath}\", but it is empty.")
    
    logger.info(f"\rLoaded \"{filepath}\".")
    
    return filecontent