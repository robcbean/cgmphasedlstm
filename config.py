import json
import os


# https://stackoverflow.com/questions/38464302/wrapping-a-python-class-around-json-data-which-is-better 21/02/2022
class Conifg:
    exp_props = {}

    def __init__(self, d):
        self.__dict__ = d
        for key in [x for x in Conifg.exp_props if x not in self.__dict__]:
            setattr(self, key, Conifg.exp_props[key])


def loadFromFile(_filename):
    if os.path.exists(_filename):
        ret = json.load(open(_filename), object_hook=Conifg)
    else:
        raise Exception(f"The file {_filename} don" "exits.")
    return ret
