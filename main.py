#!/usr/bin/env python3
import numpy as np

import config
import sys
import os
import torch
from process_data.load_data import loadScaler
from phased_lstm import plstmglucosemodel
from telegram import sender
from vault import credentials
from freestyle import GetMessages
from process_data.load_data import LoadData

class CgmPhasedLSTM:

    def __init__(self, _config_file, _cont_glucose_user, _cont_glucose_pass,_telegram_chat,_telegram_token):
        self.config = config.loadFromFile(_config_file)
        self.model = self.loadModel()
        self.scaler = loadScaler(self.model.getModelName(),self.config.model.model_folder)
        self.cgs = GetMessages.GetMessageFreeStle(  _past_values=self.config.model.past_values
                                                    ,_password=_cont_glucose_pass
                                                    ,_user=_cont_glucose_user
                                                    ,_finger_print= self.config.glucose.freetyle_fingerprint
                                                    ,_base_url= self.config.glucose.freetyle_baseurl
                                                    ,_report_string_template="report_string.json"
                                                )
        self.telegram_send = sender.TelegramSender(_telegram_chat, _telegram_token)
        self.loader = LoadData()
        self.loader.__init_parameters__("",self.scaler,self.model.past_values,self.config.model.future_steps,self.config.model.time_range_minutes)

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

    def scaleData(self,_data):
        ret = self.scaler.transform_values(_data)
        return  ret;

    def prepareData(self,_data_c,_data_s):
        n_records = _data_c.shape[0]
        values_to_pred = _data_c[(n_records-self.model.past_values):(n_records)]
        cgm_values = values_to_pred.values
        cgm_values_scaled = self.scaler.transform_values(cgm_values)
        cgm_time = values_to_pred.index
        extra_xs = np.zeros(self.model.past_values)
        for i in range(0,self.model.past_values-1):
            cur_time = cgm_time[i]
            extra_xs[i] = self.loader.find_prev_value(cur_time,_data_s)
            if extra_xs[i] != 0:
                extra_xs[i] = self.scaler.transform_values(extra_xs[i])
        cgm_values_and_measures = np.concatenate((cgm_values_scaled, extra_xs), axis=None)
        cgm_values_and_measures = np.reshape(cgm_values_and_measures, (-1, 12))
        cgm_values_and_measures = cgm_values_and_measures.transpose()
        cgm_time_pred = np.array(range(0, self.model.past_values)).astype(float)

        return cgm_values_and_measures, cgm_time_pred, cgm_time


    def sendMessageToTelegram(self,_last_value,_pred_value):
        return True



    def processLoop(self):
        data_c, data_s = self.cgs.getLastResult()
        xs, xt, xt_t = self.prepareData(data_c,data_s)
        last_value = self.scaler.inverse_transform_value(xs[xs.shape[0]-1])[0]
        last_time = xt_t[xs.shape[0]-1]
        output = self.model.predict(xs,xt)
        pred_value = self.scaler.inverse_transform_value(output.item())[0]
        if self.sendMessageToTelegram(last_value,pred_value):
            msg = f'Actual glucose {last_value} {last_time} next glucose {pred_value}'
            sys.stderr.write(msg)
            self.telegram_send.sendMessage(msg)






if __name__ == "__main__":
    configFile = "config.json"
    if len(sys.argv) > 1:
        configFile = sys.argv[2]

    vault_cred_mgr = credentials.CredentialsManagerVault()

    freeStyleML = CgmPhasedLSTM(_config_file=configFile,
                                _cont_glucose_user=vault_cred_mgr.glucose_user,
                                _cont_glucose_pass=vault_cred_mgr.glucose_password,
                                _telegram_chat=vault_cred_mgr.telegram_chat,
                                _telegram_token=vault_cred_mgr.telegram_token)
    freeStyleML.processLoop()

















