import asyncio                          #concurrency
import concurrent.futures               #multithreading
import PIL, PIL.Image, PIL.ImageFile    #conversion to PDF
import os
import requests
import time
import typing                           #function type hint
from . import log, types


def convert_images_to_PDF(images_filepath: list, PDF_filepath: str, if_success_delete_images: bool=False) -> list:  #convert list[str] with image filepaths to PDF, return conversion failures
    conversion_failures_filepath=[] #conversion failures
    PDF=[]                          #images converted for saving as pdf
    success=True                    #conversion successful?

    
    types.check(convert_images_to_PDF, locals(), types.Mode.convertable, types.Mode.convertable, types.Mode.instance)
    images_filepath=list(images_filepath)
    

    PIL.ImageFile.LOAD_TRUNCATED_IMAGES=True    #set true or raises unnecessary exception sometimes


    log.write("Converting images to PDF...")
    for image_filepath in images_filepath:   #convert all saved images
        try:
            with PIL.Image.open(image_filepath) as image_file:          #open image
                PDF.append(image_file.convert("RGBA").convert("RGB"))   #convert, append to PDF
        
        except PIL.UnidentifiedImageError:  #download earlier failed, image is corrupted
            success=False   #conversion not successful
            log.write(f"\rConverting {image_filepath} to PDF failed.")
            conversion_failures_filepath.append(image_filepath) #append to failure list so parent function can retry downloading

            for i in range(3):
                log.write(f"Deleting corrupted image {image_filepath}...")
                try:
                    os.remove(image_filepath)   #remove image, redownload later
                except PermissionError: #if could not be removed: try again, give up after try 3
                    if i<2:
                        log.write(f"\rDeleting corrupted image {image_filepath} failed. Retrying after waiting 1s...")
                        time.sleep(1)
                        continue
                    else:   #if removing corrupted image failed after 10th try: give hentai up
                        log.write(f"Deleting corrupted image {image_filepath} failed 3 times. Giving up.")
                else:
                    log.write(f"\rDeleted corrupted image {image_filepath}.")
                    break   #break out of inner loop, but keep trying to convert images to PDF to remove all other corrupt images in this function call and not later
            
        except FileNotFoundError:
            success=False   #conversion not successful
            log.write(f"{image_filepath} not found, converting to PDF failed.")
            raise FileNotFoundError

        else:
            log.write(f"\rConverted {image_filepath} to PDF.")

    
    if success==True:   #if successful: save PDF
        log.write("\rConverted images to PDF.")
        log.write(f"Saving {PDF_filepath}...")
        PDF[0].save(PDF_filepath, save_all=True, append_images=PDF[1:])
        log.write(f"\rSaved {PDF_filepath}.")
    else:
        log.write(f"Converting to PDF failed, because 1 or more images could not be converted to PDF. Not saving any PDF.")

    
    if success==True and if_success_delete_images==True:    #try to delete all source images if desired
        log.write(f"Deleting images...")
        for image_filepath in images_filepath:
            try:
                os.remove(image_filepath)
            except PermissionError:
                log.write(f"Deleting {image_filepath} failed. Skipping image...")
            else:
                log.write(f"\rDeleted {image_filepath}")
        log.write("\rDeleted images.")


    return conversion_failures_filepath


def download_image_default(image_URL: str, image_filepath: str) -> None:    #from URL download image with requests, save in filepath, default worker for download_images(...)
    image=None  #image downloaded

    
    types.check(download_image_default, locals(), types.Mode.instance, types.Mode.instance)


    page=requests.get(image_URL)    #download image, exception handling outside
    if page.status_code!=200:       #if something went wrong: exception handling outside
        raise requests.HTTPError(page)
    image=page.content

    os.makedirs(os.path.dirname(image_filepath), exist_ok=True) #create necessary folders for image file
    with open(image_filepath, "wb") as image_file:  #save image
        image_file.write(image)

    return


def download_images(images_URL: list, images_filepath: list,
                    multithreading: bool=True,
                    worker_function: typing.Callable=download_image_default, **kwargs) -> None:  #download images from URL list, save as specified in filepath
    images_downloaded=0 #how many images already downloaded counter
    threads=[]          #worker threads for download
    
    
    types.check(download_images, locals(), types.Mode.convertable, types.Mode.convertable, types.Mode.instance, types.Mode.whatever)
    

    if len(images_URL)!=len(images_filepath):   #check if every image to download has exactly 1 filepath to save to
        raise ValueError("Error in KFS::media::download_images(...): Length of images_URL and images_filepath must be the same.")


    log.write(f"Downloading images...")
    with concurrent.futures.ThreadPoolExecutor() as thread_manager:
        for i in range(len(images_URL)):                    #download missing images and save as specified
            if os.path.isfile(images_filepath[i])==True:    #if image already exists: skip
                continue
            
            if multithreading==True:
                threads.append(thread_manager.submit(worker_function, image_URL=images_URL[i], image_filepath=images_filepath[i], **kwargs)) #download and save image in worker thread
            else:
                worker_function(image_URL=images_URL[i], image_filepath=images_filepath[i], **kwargs)   #no *args so user is forced to accept image_URL and image_filepath and no confusion ensues because of unexpected parameter passing
                log.write(f"\rDownloaded image {i+1:,.0f}/{len(images_URL):,.0f}. ".replace(",", ".")+f"({images_URL[i]})") #refresh images downloaded display

        while _all_threads_done(threads)==False:                        #progess display in multithreaded mode, as long as threads still running:
            images_downloaded_new=_images_downloaded(images_filepath)   #how many images already downloaded
            if(images_downloaded==images_downloaded_new):               #if number hasn't changed: don't write on console
                time.sleep(0.1)
                continue
            
            images_downloaded=images_downloaded_new   #refresh images downloaded
            log.write(f"\rDownloaded image {images_downloaded:,.0f}/{len(images_URL):,.0f}.".replace(",", "."))
        images_downloaded=_images_downloaded(images_filepath)   #refresh images downloaded 1 last time after threads are finished and in case of everything already downloaded progress display loop will not be executed
        log.write(f"\rDownloaded image {images_downloaded:,.0f}/{len(images_URL):,.0f}.".replace(",", "."))

    return

async def download_images_async(images_URL: list, images_filepath: list,
                                worker_function: typing.Callable=download_image_default, **kwargs) -> None: #download images from URL list, save as specified in filepath
    images_downloaded=0 #how many images already downloaded counter
    tasks=[]            #worker tasks for download
    
    
    types.check(download_images_async, locals(), types.Mode.convertable, types.Mode.convertable, types.Mode.whatever)
    

    if len(images_URL)!=len(images_filepath):   #check if every image to download has exactly 1 filepath to save to
        raise ValueError("Error in KFS::media::download_images_async(...): Length of images_URL and images_filepath must be the same.")


    log.write(f"Downloading images...")
    async with asyncio.TaskGroup() as task_manager: 
        for i in range(len(images_URL)):                    #download missing images and save as specified
            if os.path.isfile(images_filepath[i])==True:    #if image already exists: skip
                continue
            
            tasks.append(task_manager.create_task(worker_function(image_URL=images_URL[i], image_filepath=images_filepath[i], **kwargs)))   #no *args so user is forced to accept image_URL and image_filepath and no confusion ensues because of unexpected parameter passing

        while await _all_tasks_done(tasks)==False:                      #progess display in multithreaded mode, as long as threads still running:
            images_downloaded_new=_images_downloaded(images_filepath)   #how many images already downloaded
            if(images_downloaded==images_downloaded_new):               #if number hasn't changed: don't write on console
                await asyncio.sleep(0.1)                                #release lock so worker get ressources too
                continue
            
            images_downloaded=images_downloaded_new   #refresh images downloaded
            log.write(f"\rDownloaded image {images_downloaded:,.0f}/{len(images_URL):,.0f}.".replace(",", "."))
        images_downloaded=_images_downloaded(images_filepath)   #refresh images downloaded 1 last time after threads are finished and in case of everything already downloaded progress display loop will not be executed
        log.write(f"\rDownloaded image {images_downloaded:,.0f}/{len(images_URL):,.0f}.".replace(",", "."))

    return
    

async def _all_tasks_done(tasks: list) -> bool: #takes list of tasks and looks if everything is done
    for task in tasks:
        if task.done()==False:
            return False
    
    return True
    

def _all_threads_done(threads: list) -> bool:   #takes list of threads and looks if everything is done
    for thread in threads:
        if thread.done()==False:
            return False
    
    return True


def _images_downloaded(images_filepath: list) -> int:   #takes list of image filepaths and counts how many exist already
    count=0


    for image_filepath in images_filepath:
        if os.path.isfile(image_filepath)==True:    #if image already exists: inkrement count
            count+=1
    
    return count