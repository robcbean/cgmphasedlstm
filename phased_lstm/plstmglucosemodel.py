import torch
from torch import nn, optim
from phased_lstm import plstmcell
import torch.nn.functional as F


class PlstmGlucoseModel(nn.Module):
    def __init__(
        self,
        _input_dim=1,
        _hidden_dim=40,
        _batch_size=250,
        _past_values=12,
        _use_lstm=True,
        _outputl1=512,
        _dropout1=0.3,
        _outputl2=256,
        _dropout2=0.3,
        _exp_func=True,
        _nlf1="relu",
        _nlf2="relu",
        _batch_normalization=False,
    ):
        super(PlstmGlucoseModel, self).__init__()
        self.input_dim = _input_dim
        self.hidden_dim = _hidden_dim
        self.use_lstm = _use_lstm
        self.outputl1 = _outputl1
        self.outputl2 = _outputl2
        self.batch_size = _batch_size
        self.exp_func = _exp_func
        self.dropout1 = _dropout1
        self.dropout2 = _dropout2
        self.nlf1 = _nlf1
        self.nlf2 = _nlf2
        self.batch_normalization = _batch_normalization
        self.past_values = _past_values

        if self.batch_normalization:
            self.btn = nn.BatchNorm1d(_past_values)

        self.rnn = plstmcell.PLSTM(_input_dim, _hidden_dim)
        self.linear_1 = nn.Linear(_hidden_dim, _outputl1)
        self.linear_2 = nn.Linear(in_features=_outputl1, out_features=_outputl2)
        self.std = nn.Linear(in_features=_outputl2, out_features=1)
        self.mu = nn.Linear(in_features=_outputl2, out_features=1)
        self.final_output = nn.Linear(
            in_features=_batch_size * _past_values * 2, out_features=_batch_size
        )

    def forward(self, points, times):
        if self.batch_normalization:
            norm = self.btn(points)
        else:
            norm = points

        lstm_out, _ = self.rnn(norm, times)
        linear_out_1 = self.linear_1(lstm_out)  # Linear (hidden_dim, 512)
        relu_output_1 = self.getFunctionByName(self.nlf1)(linear_out_1)  # Relu
        dropout_1 = F.dropout(relu_output_1, self.dropout1)  # Dropout 0.2

        linear_out_2 = self.linear_2(dropout_1)  # Linear (512,256)
        relu_output_2 = self.getFunctionByName(self.nlf2)(linear_out_2)  # Relu
        dropout_2 = F.dropout(relu_output_2, self.dropout2)  # Dropout 0.3

        out_mu = self.mu(dropout_2)  # Linear (256,1)
        out_std = self.std(dropout_2)
        if self.exp_func:
            out_std = torch.exp(out_std)  # Exponential function

        mu_std = torch.cat([out_std, out_mu])

        flat = torch.flatten(mu_std)  # Flatten
        ret = self.final_output(flat)  # Linear (3000,1)

        return ret

    def predict(self, _xs, _xt):
        xs = _xs.reshape(1, _xs.shape[0], _xs.shape[1])
        # xso = torch.from_numpy(xs).type(torch.float)
        xs = torch.tensor(list(xs.astype(float)))
        xt = _xt.reshape(1, _xt.shape[0])
        # xto = torch.from_numpy(xt.astype(int)).type(torch.float)
        xt = torch.tensor(list(xt.astype(float)))
        output = self(xs.to(torch.float), xt.to(torch.float))
        return output

    def getOptimizerByName(self, optimizer_name):
        ret = None

        if optimizer_name == "adam":
            ret = optim.Adam
        elif optimizer_name == "sgd":
            ret = optim.SGD
        elif optimizer_name == "adamax":
            ret = optim.Adamax
        elif optimizer_name == "adamw":
            ret = optim.AdamW
        elif optimizer_name == "adadelta":
            ret = optim.Adadelta
        elif optimizer_name == "rmsprop":
            ret = optim.RMSprop
        elif optimizer_name == "rprop":
            ret = optim.Rprop

        return ret

    def getFunctionByName(self, function_name):
        ret = None
        if function_name == "relu":
            ret = torch.relu
        elif function_name == "sigmoid":
            ret = torch.sigmoid
        elif function_name == "tanh":
            ret = torch.tanh
        return ret

    def __convert_bool(self, _value):
        ret = 0
        if _value:
            ret = 1
        return ret

    def getModelName(self):

        ret = f"id_{self.input_dim}_hd_{self.hidden_dim}_bs{self.batch_size}_ul_{self.__convert_bool(self.use_lstm)}"
        ret = (
            ret
            + f"_o1_{self.outputl1}_o2_{self.outputl2}_d1_{self.dropout1}_d2_{self.dropout2}"
        )
        ret = (
            ret
            + f"_ex_{self.__convert_bool(self.exp_func)}_n1_{self.nlf1}_n2_{self.nlf2}_bn_{self.__convert_bool(self.batch_normalization)}"
        )

        return ret
