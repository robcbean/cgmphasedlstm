#!/usr/bin/env python3
import config
import sys
import os
import torch
from process_data.load_data import loadScaler
from phased_lstm import plstmglucosemodel
from telegram import sender
from vault import credentials
from freestyle import GetMessages

class CgmPhasedLSTM:

    def __init__(self, _config_file, _cont_glucose_user, _cont_glucose_pass):
        self.config = config.loadFromFile(_config_file)
        self.model = self.loadModel()
        self.scaler = loadScaler(self.model.getModelName(),self.config.model.model_folder)
        self.cgs = GetMessages.GetMessageFreeStle(  _past_values=self.config.model.past_values
                                                    ,_password=_cont_glucose_pass
                                                    ,_user=_cont_glucose_user
                                                    ,_finger_print="3,(Macintosh;IntelMacOSX__)AppleWebKit/(KHTML,likeGecko)Version/Safari/,Mozilla/(Macintosh;IntelMacOSX__)AppleWebKit/(KHTML,likeGecko)Version/Safari/,AppleGPU,Europe/Madrid,1,MacIntel,es-ES,es-ES,AppleComputer,Inc.,safari"
                                                    ,_base_url="https://api-eu.libreview.io/"
                                                    ,_report_string_template="report_string.json"
                                                )

    def loadModel(self):
        ret = plstmglucosemodel.PlstmGlucoseModel(_input_dim=self.config.model.input_dim
                                                  ,_batch_size=self.config.model.batch_size
                                                  ,_hidden_dim=self.config.model.hidden_dim
                                                  ,_outputl1=self.config.model.outputl1
                                                  ,_outputl2=self.config.model.outputl2
                                                  ,_dropout2=self.config.model.dropout2
                                                  ,_dropout1=self.config.model.dropout1
                                                  ,_exp_func=self.config.model.exp_func
                                                  ,_use_lstm=self.config.model.use_lstm
                                                  ,_past_values=self.config.model.past_values
                                                  ,_batch_normalization=self.config.model.batch_normalization
                                                  ,_nlf1=self.config.model.nlf1
                                                  ,_nlf2=self.config.model.nlf2
                                                  )
        filename = os.path.join(self.config.model.model_folder,ret.getModelName())
        if os.path.exists(filename):
            ret.load_state_dict(torch.load(filename))
        else:
            raise Exception(f'The model {filename} don''t exists.')
        return ret

    def processLoop(self):
        data_c, data_s = self.cgs.getLastResult()

if __name__ == "__main__":
    configFile = "config.json"
    if len(sys.argv) > 1:
        configFile = sys.argv[2]

    vault_cred_mgr = credentials.CredentialsManagerVault()
    telegram_send = sender.TelegramSender(vault_cred_mgr.telegram_chat,vault_cred_mgr.telegram_token)
    telegram_send.sendMessage("Hola Roberto")
    freeStyleML = CgmPhasedLSTM(_config_file=configFile,
                                _cont_glucose_user=vault_cred_mgr.glucose_user,
                                _cont_glucose_pass=vault_cred_mgr.glucose_password)
    freeStyleML.processLoop()

















