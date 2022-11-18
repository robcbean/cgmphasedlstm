import os
import re
from shutil import copyfileobj

import pyicloud.services.drive
from pyicloud import PyiCloudService

class DoubleFactorManager:
    icloud_user: str
    icloud_password: str
    icloud_file: str

    def __init__(self, icloud_user: str, icloud_password: str, icloud_file: str):
        self.icloud_user = icloud_user
        self.icloud_password = icloud_password
        self.icloud_file = icloud_file

    def get_pyicloud_service(self) -> PyiCloudService:
        ret: PyiCloudService = PyiCloudService(apple_id=self.icloud_user)
        if ret is None:
            ret = PyiCloudService(apple_id=self.icloud_user, password=self.icloud_password)
        return ret

    def get_code_from_file_content(self, file_content: list) -> int:
        ret: int = -1
        file_len: int = len(file_content)
        if file_len > 1:
            line: str = file_content[file_len-1]
            results: list[str] = re.findall("[0-9]+", line)
            if len(results) == 1:
                ret = int(results[0])
        return ret

    def get_file_content(self) -> str:
        ret: str = ""
        cur_file: pyicloud.services.drive.DriveNode = None
        path_string: list = self.icloud_file.split(os.path.sep)
        for file in path_string:
            if cur_file is None:
                cur_file = self.get_pyicloud_service().drive[file]
            else:
                cur_file = cur_file[file]

        local_file: str = os.path.basename(self.icloud_file)
        if cur_file is not None:
            if os.path.exists(local_file):
                os.remove(local_file)
            with cur_file.open(stream=True) as response:
                with open(local_file, "wb") as file_out:
                    copyfileobj(response.raw, file_out)
            if os.path.exists(local_file):
                ret = open(local_file).readlines()

        return ret
    def get_code(self) -> int:
        file_content: str = self.get_file_content()
        ret: int = self.get_code_from_file_content(file_content=file_content)
        return ret





