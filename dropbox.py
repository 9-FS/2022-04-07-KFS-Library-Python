import dropbox
import os
from . import types


def create_dbx(dropbox_API_token_filepath: str="./dropbox_API_token.txt"):  #create dbx instance with saved API token
    types.check(create_dbx, locals(), types.Mode.instance)
    
    try:
        with open(dropbox_API_token_filepath, "rt") as dropbox_API_token_file:
            dropbox_API_token=dropbox_API_token_file.read() #read API access token
    except FileNotFoundError:   #if token file does not exist yet: create empty for user to paste token into
        os.makedirs(os.path.dirname(dropbox_API_token_filepath), exist_ok=True) #create folders
        open(dropbox_API_token_filepath, "wt")                                  #create file
        raise FileNotFoundError(f"Error in KFS::dropbox::create_dbx(...): Given filepath for dropbox API token does not exist yet. Created empty {dropbox_API_token_filepath} for you to paste the dropbox API token into.")

    dbx=dropbox.Dropbox(dropbox_API_token)  #create dropbox instance
    return dbx


def list_files(dbx: dropbox.Dropbox, dir: str, not_exist_ok=True) -> list: #list all files in path, returns list[str]
    file_names=[]   #file names to return

    types.check(list_files, locals(), types.Mode.instance, types.Mode.instance)

    try:
        result=dbx.files_list_folder(dir)  #read first batch of file names
    except dropbox.exceptions.ApiError:
        if not_exist_ok==True:  #if folder not existing is ok:
            return []           #return empty list
        else:                   #otherwise forward dropbox exception
            raise

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
        
        upload_session_start_result=dbx.files_upload_session_start(file.read(CHUNK_SIZE))    #if file larger: start upload session
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