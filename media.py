# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import asyncio                          # concurrency
import concurrent.futures               # multithreading
import inspect
import logging
import PIL, PIL.Image, PIL.ImageFile    # conversion to PDF
import os
import requests
import time
import typing                           # function type hint
from . import exceptions, fstr, log


def convert_images_to_PDF(images_filepath: list, PDF_filepath: str="", if_success_delete_images: bool=True) -> list:    # convert list[str] with image filepaths to PDF, return PDF, upon failure exception will contain failure list
    conversion_failures_filepath=[] # conversion failures
    logger: logging.Logger          # logger
    PDF=[]                          # images converted for saving as pdf
    success=True                    # conversion successful?
    
    images_filepath=list(images_filepath)
    PDF_filepath=str(PDF_filepath)
    
    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=log.setup_logging("KFS")         # use KFS default format
    
    PIL.ImageFile.LOAD_TRUNCATED_IMAGES=True    # set true or raises unnecessary exception sometimes


    logger.info("Converting images to PDF...")
    for image_filepath in images_filepath:   # convert all saved images
        try:
            with PIL.Image.open(image_filepath) as image_file:          # open image
                PDF.append(image_file.convert("RGBA").convert("RGB"))   # convert, append to PDF
        
        except PIL.UnidentifiedImageError:                      # download earlier failed, image is corrupted
            success=False                                       # conversion not successful
            logger.error(f"\rConverting {image_filepath} to PDF failed.")
            conversion_failures_filepath.append(image_filepath) # append to failure list so parent function can retry downloading

            for i in range(3):
                logger.info(f"Deleting corrupted image {image_filepath}...")
                try:
                    os.remove(image_filepath)   # remove image, redownload later
                except PermissionError:         # if could not be removed: try again, give up after try 3
                    if i<2:
                        logger.error(f"\rDeleting corrupted image {image_filepath} failed. Retrying after waiting 1s...")
                        time.sleep(1)
                        continue
                    else:                       # if removing corrupted image failed after 10th try: give hentai up
                        logger.error(f"Deleting corrupted image {image_filepath} failed 3 times. Giving up.")
                else:
                    logger.info(f"\rDeleted corrupted image {image_filepath}.")
                    break                       # break out of inner loop, but keep trying to convert images to PDF to remove all other corrupt images in this function call and not later
            
        except FileNotFoundError:
            success=False   # conversion not successful
            logger.error(f"{image_filepath} not found, converting to PDF failed.")
            raise FileNotFoundError

        else:
            logger.info(f"\rConverted {image_filepath} to PDF.")

    
    if success==True and PDF_filepath!="":   # if successful and filepath given: save PDF
        logger.info("\rConverted images to PDF.")
        logger.info(f"Saving {PDF_filepath}...")
        PDF[0].save(PDF_filepath, save_all=True, append_images=PDF[1:])
        logger.info(f"\rSaved {PDF_filepath}.")
    else:
        logger.error(f"Converting to PDF failed, because 1 or more images could not be converted to PDF. Not saving any PDF.")

    if success==True and if_success_delete_images==True:    # try to delete all source images if desired
        logger.info(f"Deleting images...")
        for image_filepath in images_filepath:
            try:
                os.remove(image_filepath)
            except PermissionError:
                logger.error(f"Deleting {image_filepath} failed. Skipping image...")
            else:
                logger.info(f"\rDeleted {image_filepath}")
        logger.info("\rDeleted images.")

    if success==False:  # if unsuccessful: throw exception with failure list
        raise exceptions.ConversionError(conversion_failures_filepath)


    return PDF  # return PDF in case needed internally


def download_image_default(image_URL: str, image_filepath: str) -> None:    # from URL download image with requests, save in filepath, default worker for download_images(...)
    image=None                                                              # image downloaded


    page=requests.get(image_URL)    # download image, exception handling outside
    if page.status_code!=200:       # if something went wrong: exception handling outside
        raise requests.HTTPError(page)
    image=page.content

    with open(image_filepath, "wb") as image_file:  # save image
        image_file.write(image)

    return


def download_images(images_URL: list, images_filepath: list,
                    multithreading: bool=True,
                    worker_function: typing.Callable=download_image_default, workers_max=None,
                    **kwargs) -> None:  # download images from URL list, save as specified in filepath, exceptions from worker function will not be catched
    images_downloaded=0     # how many images already downloaded counter
    logger: logging.Logger  # logger
    threads=[]              # worker threads for download
    
    images_URL=list(images_URL)
    images_filepath=list(images_filepath)

    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=log.setup_logging("KFS")         # use KFS default format

    if len(images_URL)!=len(images_filepath):   # check if every image to download has exactly 1 filepath to save to
        raise ValueError(f"Error in {download_images.__name__}{inspect.signature(download_images)}: Length of images_URL and images_filepath must be the same.")


    logger.info(f"Downloading images...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_max) as thread_manager:
        for i in range(len(images_URL)):                    # download missing images and save as specified
            if os.path.isfile(images_filepath[i])==True:    # if image already exists: skip
                continue
            else:
                os.makedirs(os.path.dirname(images_filepath[i]), exist_ok=True) # create necessary folders for image file
            
            if multithreading==True:
                threads.append(thread_manager.submit(worker_function, image_URL=images_URL[i], image_filepath=images_filepath[i], **kwargs))                # download and save image in worker thread
            else:
                worker_function(image_URL=images_URL[i], image_filepath=images_filepath[i], **kwargs)                                                       # no *args so user is forced to accept image_URL and image_filepath and no confusion ensues because of unexpected parameter passing
                logger.info(f"\rDownloaded image {fstr.notation_abs(i+1, 0, True)}/{fstr.notation_abs(len(images_URL), 0, True)}. "+f"({images_URL[i]})")   # refresh images downloaded display

        while _all_threads_done(threads)==False:                        # progess display in multithreaded mode, as long as threads still running:
            images_downloaded_new=_images_downloaded(images_filepath)   # how many images already downloaded
            if(images_downloaded==images_downloaded_new):               # if number hasn't changed: don't write on console
                time.sleep(0.1)
                continue
            images_downloaded=images_downloaded_new             # refresh images downloaded
            logger.info(f"\rDownloaded image {fstr.notation_abs(images_downloaded, 0, True)}/{fstr.notation_abs(len(images_URL), 0, True)}.")
        images_downloaded=_images_downloaded(images_filepath)   # refresh images downloaded 1 last time after threads are finished and in case of everything already downloaded progress display loop will not be executed
        logger.info(f"\rDownloaded image {fstr.notation_abs(images_downloaded, 0, True)}/{fstr.notation_abs(len(images_URL), 0, True)}.")

    return

async def download_images_async(images_URL: list, images_filepaths: list,
                                worker_function: typing.Callable=download_image_default,
                                **kwargs) -> None:  # download images from URL list, save as specified in filepath, exceptions from worker function will not be catched
    images_downloaded=0     # how many images already downloaded counter
    logger: logging.Logger  # logger
    tasks=[]                # worker tasks for download
    
    images_URL=list(images_URL)
    images_filepaths=list(images_filepaths)

    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=log.setup_logging("KFS")         # use KFS default format
    
    if len(images_URL)!=len(images_filepaths):  # check if every image to download has exactly 1 filepath to save to
        raise ValueError(f"Error in {download_images_async.__name__}{inspect.signature(download_images_async)}: Length of images_URL and images_filepath must be the same.")

    
    logger.info(f"Downloading images...")
    async with asyncio.TaskGroup() as task_manager: 
        for i in range(len(images_URL)):                    # download missing images and save as specified
            if os.path.isfile(images_filepaths[i])==True:   # if image already exists: skip
                continue
            
            tasks.append(task_manager.create_task(worker_function(image_URL=images_URL[i], image_filepath=images_filepaths[i], **kwargs)))   # no *args so user is forced to accept image_URL and image_filepath and no confusion ensues because of unexpected parameter passing

        while await _all_tasks_done(tasks)==False:                      # progess display in multithreaded mode, as long as threads still running:
            images_downloaded_new=_images_downloaded(images_filepaths)  # how many images already downloaded
            if(images_downloaded==images_downloaded_new):               # if number hasn't changed: don't write on console
                await asyncio.sleep(0.1)                                # release lock so worker get ressources too
                continue
            images_downloaded=images_downloaded_new                     # refresh images downloaded
            logger.info(f"\rDownloaded image {fstr.notation_abs(images_downloaded, 0, True)}/{fstr.notation_abs(len(images_URL), 0, True)}.")
        images_downloaded=_images_downloaded(images_filepaths)          # refresh images downloaded 1 last time after threads are finished and in case of everything already downloaded progress display loop will not be executed
        logger.info(f"\rDownloaded image {fstr.notation_abs(images_downloaded, 0, True)}/{fstr.notation_abs(len(images_URL), 0, True)}.")

    return
    

async def _all_tasks_done(tasks: list) -> bool: # takes list of tasks and looks if everything is done
    for task in tasks:
        if task.done()==False:
            return False
    
    return True
    

def _all_threads_done(threads: list) -> bool:   # takes list of threads and looks if everything is done
    for thread in threads:
        if thread.done()==False:
            return False
    
    return True


def _images_downloaded(images_filepaths: list) -> int:  # takes list of image filepaths and counts how many exist already
    count=0


    for image_filepath in images_filepaths:
        if os.path.isfile(image_filepath)==True:    # if image already exists: increment count
            count+=1
    
    return count