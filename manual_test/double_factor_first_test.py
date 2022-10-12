from pyicloud import PyiCloudService
from shutil import copyfileobj

#$ icloud --username=jappleseed@apple.com
#ICloud Password for jappleseed@apple.com:
#Save password in keyring? (y/N)

pycloud_service = PyiCloudService("robcbean@gmail.com")
drive_file = pycloud_service.drive['Shortcuts']['libreview.txt']
with drive_file.open(stream=True) as response:
    with open(drive_file.name, "wb") as file_out:
        copyfileobj(response.raw, file_out)




