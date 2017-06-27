from pydrive.auth import GoogleAuth, InvalidConfigError
from pydrive.drive import GoogleDrive
import sys, os.path
import yaml

def upload(name, file_path):
    print "Creating " + name + " data with " + file_path
    folder_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder' and trashed = false and title = '" + name + "'"}).GetList()
    #Check if folder has been created
    if len(folder_list) == 0:
        #If not create and update folder_list
        folder_metadata = {
            'title': name,
            'mimeType' : 'application/vnd.google-apps.folder',
            #Add a unique identifier
            "properties" : {
                "filesyncfolder": True
            }
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder' and trashed = false and title = '" + name + "'"}).GetList()

    folder = folder_list[0]
    check_multiple_folders(folder_list)
        #Get folder id
    if folder['title'] == name:
        id = folder['id']
    #Register the new file within the folder
    file_metadata = {
            "parents": [{"id": id}],
            "properties" : {
                "filesyncfile": True
            }
        }
    
    file1 = drive.CreateFile(file_metadata)
    file1.SetContentFile(file_path)

    #Rename all old files

    existing_list = drive.ListFile({'q': "'" + id + "' in parents and trashed = false and title = '" + name + "'"}).GetList()
    if len(existing_list) > 0:
        for file in existing_list:
            file["title"] = file["title"] +  " OLD"
            file.Upload()
    file1["title"] = name
    file1.Upload()
    pass

def update(name, file_path):
    #Get existing folder list
    folder_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder' and trashed = false and title = '" + name + "'"}).GetList()
    check_multiple_folders(folder_list)
    #Get all files within the parent folder and same name
    file_list = drive.ListFile({'q': "'" + folder_list[0]['id'] + "' in parents and trashed = false and title = '" + name + "'"}).GetList()
    check_multiple_files(file_list)
    file = file_list[0]
    file.SetContentFile(file_path)
    file.Upload()
    pass

def download(file_id, file_save):
    print "Downloading file " + file_id + " to " + file_save
    name = os.path.basename(file_id)
    #Get existing folder list
    folder_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder' and trashed = false and title = '" + name + "'"}).GetList()
    check_multiple_folders(folder_list)
    #Get all files within the parent folder and same name
    file_list = drive.ListFile({'q': "'" + folder_list[0]['id'] + "' in parents and trashed = false and title = '" + name + "'"}).GetList()
    check_multiple_files(file_list)
    file = file_list[0]
    file.GetContentFile(file_save)
    pass

def check_multiple_folders(folder_list):
    if len(folder_list) > 1:
        print "WARNING: There are multiple folders with the same name in your Drive"
    pass

def check_multiple_files(file_list):
    if len(file_list) > 1:
        print "WARNING: There are multiple files with the same name in the folder. Terminating..."
        sys.exit()
def track(file_name, file_location):
    if os.path.exists("track.yml") != True:
        print "Creating a a new tracking file..."
        buffered_data = {}
    else:
        file = open("track.yml", 'r')
        buffered_data = yaml.load(file)
        file.close()
    if(buffered_data.has_key(file_name)):
        print "That file name is already registered!"
        sys.exit(1)
    file = open("track.yml", 'w')
    buffered_data[file_name] = file_location
    yaml.dump(buffered_data, file)
    file.close()
    print "'" + file_name + "' is now linked to " + file_location


def sync_download():
    if os.path.exists("track.yml") != True:
        print "There is no tracking file. Run 'track' before you sync"
    file = open("track.yml", 'r')
    tracked_files = yaml.load(file)
    file.close()
    for key in tracked_files:
        print "Downloading " + key + " to " + tracked_files[key]
        download(key, tracked_files[key])
def sync_update():
    if os.path.exists("track.yml") != True:
        print "There is no tracking file. Run 'track' before you sync"
    file = open("track.yml", 'r')
    tracked_files = yaml.load(file)
    file.close()
    for key in tracked_files:
        print "Updating " + tracked_files[key] + " as " + key
        update(key, tracked_files[key])

def sync_upload():
    if os.path.exists("track.yml") != True:
        print "There is no tracking file. Run 'track' before you sync"
    file = open("track.yml", 'r')
    tracked_files = yaml.load(file)
    file.close()
    for key in tracked_files:
        print "Uploading " + tracked_files[key] + " as " + key
        upload(key, tracked_files[key])


ga =  GoogleAuth()
ga.LoadCredentialsFile("creds.json")

if os.path.exists("creds.json")!= True:
    ga.LocalWebserverAuth()
    ga.SaveCredentialsFile("creds.json")
    print "Saving user credentials"
else:
    ga.LoadCredentialsFile("creds.json")
command = sys.argv[1]

drive = GoogleDrive(ga)

#upload [file path]
if command == "upload":
   upload(os.path.basename(sys.argv[2]), sys.argv[2])
#update [file path]
elif command == "update":
    update(os.path.basename(sys.argv[2]), sys.argv[2])
elif command == "download":
    download(sys.argv[2], sys.argv[3])
#track [file name] [file location]
elif command == "track":
    track(sys.argv[2], sys.argv[3])
elif command == "track_down":
    sync_download()
elif command == "track_up":
    sync_update()
elif command == "track_load":
    sync_upload()