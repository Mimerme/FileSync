from pydrive.auth import GoogleAuth, InvalidConfigError
from pydrive.drive import GoogleDrive
import sys, os.path

ga =  GoogleAuth()
SAVE = False
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
    #Extract the file name from path
    name = os.path.basename(sys.argv[2])
    print "Creating new file data with " + sys.argv[2]
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
    if len(folder_list) > 1:
        print "WARNING: There are multiple folders with the same name in your Drive"
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
    file1.SetContentFile(sys.argv[2])

    #Rename all old files

    existing_list = drive.ListFile({'q': "'" + id + "' in parents and trashed = false and title = '" + name + "'"}).GetList()
    if len(existing_list) > 0:
        for file in existing_list:
            file["title"] = file["title"] +  " OLD"
            file.Upload()
    file1.Upload()
#update [file path]
elif command == "update":
    name = os.path.basename(sys.argv[2])
    #Get existing folder list
    folder_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder' and trashed = false and title = '" + name + "'"}).GetList()
    if len(folder_list) > 1:
        print "WARNING: There are multiple folders with the same name in your Drive"
    #Get all files within the parent folder and same name
    file_list = drive.ListFile({'q': "'" + folder_list[0]['id'] + "' in parents and trashed = false and title = '" + name + "'"}).GetList()
    if len(file_list) > 1:
        print "WARNING: There are multiple files with the same name in the folder. Terminating..."
        sys.exit()
    file = file_list[0]
    file.SetContentFile(sys.argv[2])
    file.Upload()
        
elif command == "download":
    print "Downloading file " + sys.argv[2] + " to " + sys.argv[3]
    name = os.path.basename(sys.argv[2])
    #Get existing folder list
    folder_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder' and trashed = false and title = '" + name + "'"}).GetList()
    if len(folder_list) > 1:
        print "WARNING: There are multiple folders with the same name in your Drive"
    #Get all files within the parent folder and same name
    file_list = drive.ListFile({'q': "'" + folder_list[0]['id'] + "' in parents and trashed = false and title = '" + name + "'"}).GetList()
    if len(file_list) > 1:
        print "WARNING: There are multiple files with the same name in the folder. Terminating..."
        sys.exit()
    file = file_list[0]
    file.GetContentFile(sys.argv[3])
elif command == "track":
    pass