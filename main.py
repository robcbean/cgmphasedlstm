#!/usr/bin/env python3
import config
import sys
import os
import pickle
from process_data.load_data import  loadScaler
from phased_lstm import plstmglucosemodel

class FreeStyleML:

    def __init__(self,_config_file):
        self.config = config.loadFromFile(_config_file)
        self.model = self.loadModel()
        self.scaler = loadScaler(self.model.getModelName(),self.config.model.model_folder)

    def loadModel(self):
        ret = plstmglucosemodel.PlstmGlucoseModel(_input_dim=self.config.model.input_dim)
        ret.load_state_dict(f'{self.config.model.model_folder}')
        return ret

    def processLoop(self):
        pass

if __name__ == "__main__":
    configFile = "config.json"
    if len(sys.argv) > 1:
        configFile = sys.argv[2]

    freeStyleML = FreeStyleML(configFile)
    freeStyleML.processLoop()
















