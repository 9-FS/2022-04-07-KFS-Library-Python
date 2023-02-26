import logging
import os
from . import log


def load_config(filepath: str, default_content: str="", empty_ok: bool=False) -> str|None:
    """
    Tries to load \"filepath\" and return text content.
    
    If file does not exist, create with \"default_content\" and return None.

    If empty_ok is false and file does exist but is empty, return None.

    If empty_ok is true and file does exist but is empty, return empty string.
    """

    file_content: str|None
    logger: logging.Logger  #logger
    
    if 1<=len(logging.getLogger("").handlers):  #if root logger defined handlers:
        logger=logging.getLogger("")            #also use root logger to match formats defined outside KFS
    else:                                       #if no root logger defined:
        logger=log.setup_logging("KFS")         #use KFS default format
        

    logger.info(f"Loading \"{filepath}\"...")
    try:
        with open(filepath, "rt") as file:  #read file
            file_content=file.read()
    except FileNotFoundError:   #if file does not exist:
        file_content=None
        logger.warning(f"Could not load \"{filepath}\", because file does not exist.")
        logger.info(f"Creating \"{filepath}\" and filling with default content...")
        try:
            if os.path.dirname(filepath)!="":
                os.makedirs(os.path.dirname(filepath), exist_ok=True)   #create folders
            with open(filepath, "wt") as file:                          #create file
                file.write(default_content)                             #fill with default content
        except OSError:
            logger.error(f"Could not create \"{filepath}\" and fill with default content.")
        else:
            logger.info(f"\rCreated \"{filepath}\" and filled with default content.")
    except PermissionError: #if filepath is actually a directory:
        file_content=None
        logger.error(f"Could not load \"{filepath}\", because permission was denied. It is likely a folder and not a file.")
    else:                                                                   #if loading successful:
        if file_content=="" and empty_ok==False:                            #but if content is empty and not allowed empty:
            logger.warning(f"\rLoaded \"{filepath}\", but it is empty.")    #warning
            file_content=None
        else:
            logger.info(f"\rLoaded \"{filepath}\".")
    
    return file_content