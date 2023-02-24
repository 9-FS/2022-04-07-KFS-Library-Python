import os
from . import log


def load_config(filepath: str, default_content: str="") -> str|None:
    """
    Tries to load \"filepath\" and return text content. If file does not exist, create with \"default_content\" and return None.
    """

    file_content: str|None
    logger=log.setup_logging("KFS") #logger

    logger.info(f"Loading \"{filepath}\"...")
    try:
        with open(filepath, "rt") as file:
            file_content=file.read()
    except FileNotFoundError:
        file_content=None
        logger.warning(f"Could not load \"{filepath}\", because file does not exist.")
        logger.info(f"Creating \"{filepath}\" and filling with default content...")
        try:
            if os.path.dirname(filepath)!="":
                os.makedirs(os.path.dirname(filepath), exist_ok=True)   #create folders
            with open(filepath, "wt") as file:                          #create file
                file.write(default_content)
        except OSError:
            logger.error(f"Could not create \"{filepath}\" and fill with default content.")
        else:
            logger.info(f"\rCreated \"{filepath}\" and filled with default content.")
    except PermissionError:
        file_content=None
        logger.error(f"Could not load \"{filepath}\", because permission was denied. It is likely a folder and not a file.")
    else:
        logger.info(f"\rLoaded \"{filepath}\".")
    
    return file_content