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
        
    if os.path.isfile(filepath)==False and os.path.isdir(filepath)==False:  #if input configuration file does not exist yet: create a default one and print instructions
        logger.warning(f"Did not load \"{filepath}\", because file does not exist.")
        file_content=None
        logger.info(f"Creating default \"{filepath}\"...")
        try:
            if os.path.dirname(filepath)!="":
                os.makedirs(os.path.dirname(filepath), exist_ok=True)   #create folders
            with open(filepath, "wt") as file:                          #create file
                file.write(default_content)                             #fill with default content
        except OSError:
            logger.error(f"Creating default \"{filepath}\" failed.")
        else:
            logger.info(f"\rCreated default \"{filepath}\".")
        return file_content
    elif os.path.isfile(filepath)==False and os.path.isdir(filepath)==True:
        logger.error(f"Did not load \"{filepath}\", because it is a directory. Unable to create default file.")
        file_content=None
        return file_content


    logger.info(f"Loading \"{filepath}\"...")
    try:
        with open(filepath, "rt") as file:  #read file
            file_content=file.read()
    except OSError: #if filepath is actually a directory:
        logger.error(f"Loading \"{filepath}\" failed.")
        file_content=None
        return file_content
    
    if file_content=="" and empty_ok==False:                        #but if content is empty and not allowed empty:
        logger.error(f"\rLoaded \"{filepath}\", but it is empty.")  #error
        file_content=None
    else:
        logger.info(f"\rLoaded \"{filepath}\".")
    
    return file_content