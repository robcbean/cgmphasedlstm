class GetMessages:


    def __init__(self,_user,_password,_past_values):
        self.user = _user
        self.password = _password
        self.past_values = _past_values
        self.cg_interval_min = 0
    def getLastResult(self):
        raise Exception('getLastResult not implemented')
    @property
    def cg_interval_min(self):
        if self.min_interval == 0:
            raise  Exception('Continuos Glusose Interval not set.')

    @cg_interval_min.setter
    def cg_interval_min(self, _min_interval):
        self.cg_interval_min = _min_interval


class GetMessageFreeStle(GetMessages):
    def __init__(self,_user,_password,_past_values):
        super(GetMessageFreeStle, self).__init__(_user,_password,_past_values)
        self.cg_interval_min = 15

    def getLastResult(self):
        ret = range(1,self.past_values)
        return ret







