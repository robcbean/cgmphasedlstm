import sys
import os
import pickle
import pandas as pd
import numpy as np
import datetime
import enum
from process_data.extract_data import ExportFileFields, RecordTypeOutput
from sklearn import preprocessing


class ScalerValues(enum.Enum):
    NoScaler = ""
    MinMaxScaler = "MinMaxScaler"
    StandardScaler = "StandardScaler"


def sequence_to_supervised(data, nb_past_steps, nb_steps_in_future):
    """Computes feature and target process_data for the sequence. The features are the
    number of past steps used, and the target is the specified number of steps
    into the future."""
    x = rolling_window(data, nb_past_steps)
    y = data[nb_past_steps + nb_steps_in_future - 1 :: 1]

    x, y = zip(*zip(x, y))

    return np.array(x), np.array(y)


def rolling_window(sequence, window):
    """Splits the sequence into window sized chunks by moving the window along
    the sequence."""
    shape = sequence.shape[:-1] + (sequence.shape[-1] - window + 1, window)
    strides = sequence.strides + (sequence.strides[-1],)
    return np.lib.stride_tricks.as_strided(sequence, shape=shape, strides=strides)


class Scaler:
    def __init__(self, _scaler):
        self.scaler = _scaler
        self.scaler_function = self.__getScaler__(self.scaler)

    def transform_values(self, _values):
        ret = _values
        if self.scaler == ScalerValues.MinMaxScaler:
            ret = (ret - self.scaler_function.data_min_) / (
                self.scaler_function.data_max_ - self.scaler_function.data_min_
            )
        elif self.scaler == ScalerValues.StandardScaler:
            ret = (ret - self.scaler_function.mean_) / self.scaler_function.std_

        return ret

    def inverse_transform_value(self, _value):
        ret = _value
        if self.scaler == ScalerValues.MinMaxScaler:
            ret = (
                ret * (self.scaler_function.data_max_ - self.scaler_function.data_min_)
                + self.scaler_function.data_min_
            )
        elif self.scaler == ScalerValues.StandardScaler:
            ret = ret * self.scaler_function.std_ + self.scaler_function.mean_
        return ret

    def inverse_transform_values(self, _values):
        ret = _values
        if self.scaler != ScalerValues.NoScaler:
            pass
        elif self.scaler == ScalerValues.MinMaxScaler:
            ret = self.scaler_function.inverse_transform(_values)
        elif self.scaler == ScalerValues.StandardScaler:
            ret = self.scaler_function.inverse_transform(_values)
        return ret

    def __getScaler__(self, _scaler):
        ret = self.__processNone__
        if _scaler == ScalerValues.MinMaxScaler:
            ret = preprocessing.MinMaxScaler()
        elif _scaler == ScalerValues.StandardScaler:
            ret = preprocessing.StandardScaler()
        return ret

    def __processNone__(self, _value):
        return _value


def storeScaler(_scaler, _model_name, _model_folder):
    filename = os.path.join(_model_folder, f"{_model_name}.p")
    pickle.dump(_scaler, open(filename, "wb"))


def loadScaler(_model_name, _model_folder):
    filename = os.path.join(_model_folder, f"{_model_name}.p")
    ret = pickle.load(open(filename, "rb"))
    return ret


class LoadData:
    def __init_parameters__(
        self, _filename, _scaler, _past_values, _future_steps, _time_range_minutes
    ):
        self.filename = _filename
        self.scaler = Scaler(_scaler)
        self.past_values = _past_values
        self.future_steps = _future_steps
        self.time_range_minutes = _time_range_minutes

    def __init__(self):
        self.__init_parameters__(None, None, None, None, None)

    def __processNone__(self, _value):
        return _value

    def __check_none_paramter__(self, _parameter, _name):
        if _parameter == None:
            raise Exception(f"The parameter {_name} muut have a value.")

    def __check__parameters__(
        self,
        _filename=None,
        _scaler=None,
        _past_values=None,
        _future_steps=None,
        _time_range_minutes=None,
    ):

        self.__check_none_paramter__(_filename, "_filename")
        if not os.path.exists(_filename):
            raise Exception(f"The file {_filename} don" " exists.")

        self.__check_none_paramter__(_scaler, "_scaler")
        self.__check_none_paramter__(_past_values, "_past_values")
        self.__check_none_paramter__(_future_steps, "_future_steps")
        self.__check_none_paramter__(_time_range_minutes, "_time_range_minutes")

    def get_raw_data_df(self):
        ret = pd.read_csv(self.filename, sep="\t")
        return ret

    def get_series_data(self, _raw_data, _field="", _value=""):
        if _field != "" and _value != "":
            raw_data = _raw_data[_raw_data[_field] == _value]
        else:
            raw_data = _raw_data

        values = raw_data[ExportFileFields.GlucoseValue.value].values
        if self.scaler != ScalerValues.NoScaler:
            values_scaled = self.scaler.scaler_function.fit_transform(
                values.reshape(-1, 1)
            ).reshape(-1)
        else:
            values_scaled = values
        date_values = raw_data[ExportFileFields.Timestamp.value].values
        index = pd.DatetimeIndex(pd.to_datetime(date_values, format="%d-%m-%Y %H:%M"))
        ret = pd.Series(values_scaled, index=index)
        ret.index.name = "time"
        return ret

    def get_series_data_df(self, _raw_data):
        series_data_periodic = self.get_series_data(
            _raw_data, ExportFileFields.Type.value, RecordTypeOutput.Periodic.value
        )
        series_data_puntal = self.get_series_data(
            _raw_data,
            ExportFileFields.Type.value,
            RecordTypeOutput.Puntual.value,
        )

        return series_data_periodic, series_data_puntal

    def split_data_in_steps(self, _series_data):
        dt = _series_data.index.to_series().diff().dropna()
        idx_breaks = np.argwhere((dt != pd.Timedelta(15, "m")).values)

        nd_glucose_level = _series_data.values
        nd_glucose_index = _series_data.index.to_numpy(dtype=object)

        consecutive_segments = np.split(nd_glucose_level, idx_breaks.flatten())
        consecutive_segments = [
            c
            for c in consecutive_segments
            if len(c) >= self.past_values + self.future_steps
        ]

        consecutive_segments_time = np.split(nd_glucose_index, idx_breaks.flatten())
        consecutive_segments_time = [
            d
            for d in consecutive_segments_time
            if len(d) >= self.past_values + self.future_steps
        ]

        sups = [
            sequence_to_supervised(c, self.past_values, self.future_steps)
            for c in consecutive_segments
        ]
        xss = [sup[0] for sup in sups]
        yss = [sup[1] for sup in sups]
        xs = np.concatenate(xss)
        ys = np.concatenate(yss)

        sups_t = [
            sequence_to_supervised(d, self.past_values, self.future_steps)
            for d in consecutive_segments_time
        ]
        xts = [sup[0] for sup in sups_t]
        xt = np.concatenate(xts)

        return np.expand_dims(xs, axis=2), xt, ys

    def find_prev_value(self, _cur_time, _series_data_extra):
        ret = 0
        prev_time_min = _cur_time + datetime.timedelta(minutes=-self.time_range_minutes)

        values = _series_data_extra[
            (_series_data_extra.index > prev_time_min)
            & (_series_data_extra.index < _cur_time)
        ]

        if len(values) > 0:
            ret = values.values[0]

        return ret

    def extract_extra_xs(self, _xs, _xt, _series_data_extra):
        new_shape = _xs.shape
        ret = np.empty((new_shape[0], new_shape[1], new_shape[2] + 1))

        for i in range(0, _xt.shape[0] - 1):
            cur_xt = _xt[i]
            cur_xs = _xs[i]

            extra_xs = np.zeros(self.past_values)
            for j in range(0, self.past_values):
                cur_time = cur_xt[j]
                extra_xs[j] = self.find_prev_value(cur_time, _series_data_extra)
            new_xs = np.concatenate((cur_xs, extra_xs), axis=None)

            new_xs = np.reshape(new_xs, (-1, 12))
            ret[i] = new_xs.transpose()

        return ret

    def load_gluose_data_from_file(
        self,
        _filename,
        _scaler=ScalerValues.NoScaler,
        _past_values=12,
        _future_steps=1,
        _time_range_minutes=15,
    ):
        self.__check__parameters__(
            _filename, _scaler, _past_values, _future_steps, _time_range_minutes
        )
        self.__init_parameters__(
            _filename, _scaler, _past_values, _future_steps, _time_range_minutes
        )

        sys.stderr.write(f"Loading data_load from file {self.filename}\n")

        series_data_periodic, series_data_puntal = self.get_series_data_df(
            self.get_raw_data_df()
        )
        xs_tmp, xt, ys = self.split_data_in_steps(series_data_periodic)

        xs, xt_t = self.get_extra_data(series_data_puntal, xs_tmp, xt)

        sys.stderr.write("Load data_load sucessfully..\n")

        return xs, xt, xt_t, ys

    def get_extra_data(self, series_data_puntal, xs_tmp, xt):
        xs = self.extract_extra_xs(xs_tmp, xt, series_data_puntal)
        xt_t = xt.copy()
        for i in range(0, xt.shape[0] - 1):
            new_val = np.array(range(0, xt.shape[1])).astype(float)
            xt[i] = new_val
        return xs, xt_t


def split_all_data(xs, xt, xt_t, ys, train_fraction, valid_fraction):

    xs_train, xs_valid, xs_test = split_data(xs, train_fraction, valid_fraction)
    xt_train, xt_valid, xt_test = split_data(xt, train_fraction, valid_fraction)
    xt_t_train, xt_t_valid, xt_t_test = split_data(xt_t, train_fraction, valid_fraction)
    ys_train, ys_valid, ys_test = split_data(ys, train_fraction, valid_fraction)

    return (
        xs_train,
        xt_train,
        xt_t_train,
        ys_train,
        xs_valid,
        xt_valid,
        xt_t_valid,
        ys_valid,
        xs_test,
        xt_test,
        xt_t_test,
        ys_test,
    )


def split_data(xs, train_fraction, valid_fraction):
    n = len(xs)
    nb_train = int(np.ceil(train_fraction * n))
    nb_valid = int(np.ceil(valid_fraction * n))
    i_end_train = nb_train
    i_end_valid = nb_train + nb_valid

    return np.split(xs, [i_end_train, i_end_valid])
