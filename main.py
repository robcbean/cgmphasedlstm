#!/usr/bin/env python3
import datetime
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import torch

import config
from freestyle import getmessages
from phased_lstm import plstmglucosemodel
from process_data.load_data import LoadData, loadScaler
from telegram import sender
from vault import credentials
import schedule

class CgmPhasedLSTM:
    last_time: datetime.time
    prev_last_time: datetime.time
    def __init__(
            self,
            _config_file,
            _cont_glucose_user,
            _cont_glucose_pass,
            _telegram_chat,
            _telegram_token,
            _icloud_user,
            _icloud_password
    ):
        self.config = config.loadFromFile(_config_file)
        self.model = self.loadModel()
        self.scaler = loadScaler(
            self.model.getModelName(), self.config.model.model_folder
        )
        self.cgs = getmessages.GetMessageFreeStytle(
            _past_values=self.config.model.past_values,
            _password=_cont_glucose_pass,
            _user=_cont_glucose_user,
            _finger_print=self.config.glucose.freetyle_fingerprint,
            _base_url=self.config.glucose.freetyle_baseurl,
            _report_string_template="report_string.json",
            _icloud_user=_icloud_user,
            _icloud_password=_icloud_password,
            _filename_token_double_factor="double_factor.txt",
            _double_factor=True
        )
        self.telegram_send = sender.TelegramSender(_telegram_chat, _telegram_token)
        self.loader = LoadData()
        self.loader.__init_parameters__(
            "",
            self.scaler,
            self.model.past_values,
            self.config.model.future_steps,
            self.config.model.time_range_minutes,
        )

    def loadModel(self):
        ret = plstmglucosemodel.PlstmGlucoseModel(
            _input_dim=self.config.model.input_dim,
            _batch_size=self.config.model.batch_size,
            _hidden_dim=self.config.model.hidden_dim,
            _outputl1=self.config.model.outputl1,
            _outputl2=self.config.model.outputl2,
            _dropout2=self.config.model.dropout2,
            _dropout1=self.config.model.dropout1,
            _exp_func=self.config.model.exp_func,
            _use_lstm=self.config.model.use_lstm,
            _past_values=self.config.model.past_values,
            _batch_normalization=self.config.model.batch_normalization,
            _nlf1=self.config.model.nlf1,
            _nlf2=self.config.model.nlf2,
        )
        filename = os.path.join(self.config.model.model_folder, ret.getModelName())
        if os.path.exists(filename):
            ret.load_state_dict(torch.load(filename))
        else:
            raise Exception(f"The model {filename} don" "t exists.")
        return ret

    def scaleData(self, _data):
        ret = self.scaler.transform_values(_data)
        return ret

    def prepareData(self, _data_c, _data_s):
        n_records = _data_c.shape[0]
        values_to_pred = _data_c[(n_records - self.model.past_values): (n_records)]
        cgm_values = values_to_pred.values
        cgm_values_scaled = self.scaler.transform_values(cgm_values)
        cgm_time = values_to_pred.index
        extra_xs = np.zeros(self.model.past_values)
        for i in range(0, self.model.past_values - 1):
            cur_time = cgm_time[i]
            extra_xs[i] = self.loader.find_prev_value(cur_time, _data_s)
            if extra_xs[i] != 0:
                extra_xs[i] = self.scaler.transform_values(extra_xs[i])
        cgm_values_and_measures = np.concatenate(
            (cgm_values_scaled, extra_xs), axis=None
        )
        cgm_values_and_measures = np.reshape(cgm_values_and_measures, (-1, 12))
        cgm_values_and_measures = cgm_values_and_measures.transpose()
        cgm_time_pred = np.array(range(0, self.model.past_values)).astype(float)

        return cgm_values_and_measures, cgm_time_pred, cgm_time

    def generate_image(self, _x_values_time, _y_values, _x_next_value, _y_next_value):
        x_values = _x_values_time.values
        x_values = np.insert(x_values, len(x_values), _x_next_value)
        y_values = _y_values
        y_values = np.insert(y_values, len(y_values), _y_next_value)
        y_values = y_values.round(2)

        fig = plt.figure()
        plt.xlabel("Dia/Hora")
        plt.ylabel("Glucosa")

        for i, j in zip(x_values, y_values):
            plt.annotate(str(j), xy=(i, j))

        plt.plot(x_values, y_values)
        ret = "image.png"
        plt.savefig(ret)

        return ret

    def glucoseInRange(self, _last_value, _pred_value):
        ret = True
        if _pred_value != 0:
            variation = (_last_value - _pred_value) / _pred_value * 100
        else:
            variation = 0

        if _pred_value > self.config.glucose.threshold_high:
            ret = False
        elif _pred_value < self.config.glucose.threshold_low:
            ret = False
        elif variation > self.config.glucose.variation_percent:
            ret = False

        return ret

    def sendMessageToTelegram(self, _xt_t, _xs, _last_value, _pred_value, _last_time):

        next_time = _last_time + datetime.timedelta(
            minutes=self.config.model.time_range_minutes
        )

        msg = f"\nActual glucose {_last_value} at {_last_time}\nNext glucose {_pred_value} at {next_time}\n"
        sys.stderr.write(msg)
        self.telegram_send.sendMessage(msg)
        self.telegram_send.sendImage(
            os.path.join(
                os.getcwd(),
                self.generate_image(
                    _xt_t,
                    self.scaler.inverse_transform_value(np.transpose(_xs)[0]),
                    next_time,
                    _pred_value,
                ),
            )
        )
        # (_x_values_time, _y_values, _x_next_value, _y_next_value
    def start_proces(self):
        schedule.every(self.config.wait_time).seconds.until(self.config.end_notification_time).do(self.get_gluclose_values)
    def processLoop(self):
        self.prev_last_time = None
        self.last_time = None
        self.start_proces()
        schedule.every(1).day.at(self.config.start_notification_time).do(self.start_proces)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_gluclose_values(self):
        try:
            sys.stderr.write("\nProcesing get_glucse_values\n")
            data_c, data_s = self.cgs.get_last_result()
            xs, xt, xt_t = self.prepareData(data_c, data_s)
            output = self.model.predict(xs, xt)
            last_value = self.scaler.inverse_transform_value(xs[xs.shape[0] - 1])[0]
            self.last_time = xt_t[xt_t.shape[0] - 1]
            sys.stderr.write(
                f"\nPrev. last time:{self.prev_last_time}\tLast time: {self.last_time}"
            )
            if self.prev_last_time == None or self.last_time > self.prev_last_time:
                pred_value = self.scaler.inverse_transform_value(output.item())[0]
                sys.stderr.write(
                    f"\nLast value: {last_value} prev_value: {pred_value}"
                )
                if not self.glucoseInRange(last_value, pred_value):
                    self.sendMessageToTelegram(
                        xt_t, xs, last_value, pred_value, last_time
                    )
        except Exception as ex:
            sys.stderr.write(str(ex))
        self.prev_last_time = self.last_time


if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    configFile = "config.json"
    if len(sys.argv) > 1:
        configFile = sys.argv[2]

    vault_cred_mgr = credentials.CredentialsManagerVault()

    freeStyleML = CgmPhasedLSTM(
        _config_file=configFile,
        _cont_glucose_user=vault_cred_mgr.glucose_user,
        _cont_glucose_pass=vault_cred_mgr.glucose_password,
        _telegram_chat=vault_cred_mgr.telegram_chat,
        _telegram_token=vault_cred_mgr.telegram_token,
        _icloud_user=vault_cred_mgr.icloud_user,
        _icloud_password=vault_cred_mgr.icloud_password
    )
    freeStyleML.processLoop()
