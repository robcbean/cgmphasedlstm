import sys

import torch
import torch.nn.functional as F
import enum
import math
import numpy as np


class Events(enum.Enum):
    BeforeTrain = 0
    Training = 1
    AfterTrain = 2
    BeforeTest = 3
    Testing = 4
    AfterTest = 5


class SubscriberTrainer:
    def __init__(self, _name):
        self.name = _name

    def before(self, _loss, _trainer):
        pass

    def doing(self, _loss, _trainer):
        pass

    def after(self, _loss, _trainer):
        pass


class Trainer:
    def calc_num_batches(self, _train=True):
        if _train:
            return math.ceil(self.train_data[0].shape[0] / self.batch_size)
        else:
            return math.ceil(self.test_data[0].shape[0] / self.batch_size)

    def create_generator_train(self, _data, _train):
        x, xt, y = _data[0], _data[1], _data[2]
        num_batches = self.calc_num_batches(_train=_train)
        for i in range(0, num_batches):
            yield torch.from_numpy(x[i : (i + self.batch_size)]).type(
                torch.float
            ), torch.from_numpy(xt[i : (i + self.batch_size)].astype(int)).type(
                torch.float
            ), torch.from_numpy(
                y[i : (i + self.batch_size)]
            ).type(
                torch.float
            )

    def __init__(
        self,
        _events,
        _model,
        _optimizer_name,
        _train_data,
        _test_data,
        _batch_size,
        _epochs,
        _lr,
        _clip_value=100,
    ):
        self.events = {event: dict() for event in _events}
        self.device = torch.device("cpu")
        self.model = _model
        self.train_data = _train_data
        self.test_data = _test_data
        self.batch_size = _batch_size
        self.lr = _lr
        self.epochs = _epochs
        self.optimizer = self.model.getOptimizerByName(_optimizer_name)(
            self.model.parameters(), lr=self.lr
        )
        self.clip_value = _clip_value
        self.epoch = 0
        if len(self.events) == 0:
            self.events = {}

    def get_suscribers(self, _event):
        ret = self.events[_event]
        return ret

    def register(self, _event, _who, _callback=None):
        if _callback == None:
            _callback = getattr(_who, "update")
        self.get_suscribers(_event)[_who] = _callback

    def unregister(self, _event, _who):
        del self.get_subscribers(_event)[_who]

    def dispatch(self, _event, loss=0):
        if len(self.events) > 0:
            for subscriber, callback in self.get_suscribers(_event).items():
                callback(loss, self)

    def train_and_test(self, _epochs=None):
        self.train(_epochs=_epochs, _test=True)

    def train(self, _epochs=None, _test=False):
        self.dispatch(Events.BeforeTrain)
        if _epochs != None:
            epochs = _epochs
        else:
            epochs = self.epochs

        for epoch_loop in range(1, epochs + 1):
            self.epoch = epoch_loop
            self.model.train()
            for batch_idx, (bX, bT, bY) in enumerate(
                self.create_generator_train(self.train_data, True)
            ):
                bX = bX.to(self.device)
                bT, bY = bT.to(self.device), bY.to(self.device)
                self.optimizer.zero_grad()
                output = self.model(bX, bT)
                bY = bY.reshape(-1)
                loss = F.l1_loss(output, bY)
                loss.backward()
                torch.nn.utils.clip_grad_value_(
                    self.model.parameters(), self.clip_value
                )
                self.optimizer.step()
                self.dispatch(Events.Training, loss.item())
            if _test:
                self.test()
            sys.stderr.write(
                f"Epoch: {epoch_loop} / {self.epochs} Loss: {loss.item()}\n"
            )
        self.dispatch(Events.AfterTrain)

    def test(self):
        self.dispatch(Events.BeforeTest)
        self.model.eval()
        test_loss = 0
        total = 0
        with torch.no_grad():
            for batch_idx, (bX, bT, bY) in enumerate(
                self.create_generator_train(self.test_data, _train=False)
            ):
                bX = bX.to(self.device)
                bT, bY = bT.to(self.device), bY.to(self.device)
                bY = bY.reshape(-1)
                output = self.model(bX, bT)
                test_loss += F.l1_loss(output, bY, reduction="sum").item()
                total = total + self.batch_size
                self.dispatch(Events.Testing, test_loss)

        test_loss = test_loss / total
        self.dispatch(Events.AfterTest, test_loss)
        sys.stderr.write(f"Epoch: {self.epoch} / {self.epochs} Test: {test_loss}\n")
