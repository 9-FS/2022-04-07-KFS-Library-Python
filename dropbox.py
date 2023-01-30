import dropbox
import os
import requests
import time
from . import log, types


def create_dbx(dropbox_API_token_filepath: str="./dropbox_API_token.txt"):  #create dbx instance with saved API token
    types.check(create_dbx, locals(), types.Mode.instance)
    
    try:
        with open(dropbox_API_token_filepath, "rt") as dropbox_API_token_file:
            dropbox_API_token=dropbox_API_token_file.read()                         #read API access token
    except FileNotFoundError:                                                       #if token file does not exist yet: create empty for user to paste token into
        log.write(f"Dropbox API token could not be loaded because given filepath {dropbox_API_token_filepath} does not exist yet. Creating empty file...")
        if os.path.dirname(dropbox_API_token_filepath)!="":
            os.makedirs(os.path.dirname(dropbox_API_token_filepath), exist_ok=True) #create folders
        open(dropbox_API_token_filepath, "wt")                                      #create empty file
        log.write(f"\rDropbox API token could not be loaded because given filepath {dropbox_API_token_filepath} does not exist yet. Created empty file for user to paste the dropbox API token into.")
        raise FileNotFoundError(f"Error in KFS::dropbox::create_dbx(...): Dropbox API token could not be loaded because given filepath {dropbox_API_token_filepath} does not exist yet. Created empty file for user to paste the dropbox API token into.")

    dbx=dropbox.Dropbox(dropbox_API_token)  #create dropbox instance
    return dbx


def list_files(dbx: dropbox.Dropbox, dir: str, not_exist_ok=True) -> list: #list all files in path, returns list[str]
    file_names=[]   #file names to return

    types.check(list_files, locals(), types.Mode.instance, types.Mode.instance)
    while True:
        try:
            result=dbx.files_list_folder(dir)   #read first batch of file names
        except dropbox.exceptions.ApiError:     #folder does not exist
            if not_exist_ok==True:              #if folder not existing is ok:
                return []                       #return empty list
            else:                               #otherwise forward dropbox exception
                raise
        except requests.exceptions.ConnectionError: #connection unexpectedly failed: try again
            time.sleep(1)
            continue
        else:
            break

    file_names+=[entry.name for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)==True] #append file names, exclude all non-files

    while result.has_more==True:    #as long as more file names still unread: continue
        result=dbx.files_list_folder_continue(result.cursor)
        file_names+=[entry.name for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)==True] #append file names, exclude all non-files

    file_names.sort()   #sort file names before returning

    return file_names


def upload_file(dbx: dropbox.Dropbox, source_filepath: str, destination_filepath: str) -> None: #upload specified to dropbox, create folders as necessary, if file exists already replace
    CHUNK_SIZE=pow(2, 22)   #≈4,2MB
    
    types.check(upload_file, locals(), types.Mode.instance, types.Mode.instance, types.Mode.instance)
    

    file_size=os.path.getsize(source_filepath)  #source file size [B]

    with open(source_filepath, "rb") as file:
        if file_size<=CHUNK_SIZE:   #if smaller than chunk size: upload everything at once
            dbx.files_upload(file.read(), destination_filepath, dropbox.files.WriteMode.overwrite)
            return  #job done
        
        while True:
            try:
                upload_session_start_result=dbx.files_upload_session_start(file.read(CHUNK_SIZE))    #if file larger: start upload session
            except requests.exceptions.SSLError:    #if SSLError because max retries exceeded or something: retry lol
                time.sleep(1)
                continue
            else:
                break
        cursor=dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=file.tell())
        commit=dropbox.files.CommitInfo(path=destination_filepath)
        
        while file.tell()<file_size:             #keep uploading as long as not reached file end
            if CHUNK_SIZE<file_size-file.tell(): #if regular upload call:
                dbx.files_upload_session_append(file.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                cursor.offset=file.tell()
            else:                                #if last upload call
                dbx.files_upload_session_finish(file.read(CHUNK_SIZE), cursor, commit)

    return
#source: https://stackoverflow.com/questions/37397966/dropbox-api-v2-upload-large-files-using-python