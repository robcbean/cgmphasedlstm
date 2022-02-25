from  urllib.parse import urljoin
import requests
import datetime
import os
import json
from mako.template import Template

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
    def __init__(self,_user,_password,_finger_print,_base_url,_report_string_template,_past_values):
        super(GetMessageFreeStle, self).__init__(_user,_password,_past_values)
        self.cg_interval_min = 15
        self.finger_print = _finger_print
        self.base_url = _base_url
        self.report_string_template = _report_string_template

    def __loginURL__(self):
        ret = f'{urljoin(self.base_url,"/auth/login/")}'
        return ret

    def __loginParams__(self):
        ret  = \
        {
            "email" : self.user,
            "fingerprint" : self.finger_print,
            "password" : self.password
        }
        return ret

    def __tokenHeader__(self, _token_login):
        ret = {'Autorization': f'Bearer {_token_login}'}
        return ret

    def __tokenLogin__(self):
        response_login = requests.post(self.__loginURL__(), self.__loginParams__()).json()
        ret = response_login['data']['authTicket']['token']
        return ret

    def __reportString__(self):
        today_date = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())
        start_date = today_date - (24 * 60 * 60 + 60)
        if not os.path.exists(self.report_string_template):
            raise Exception(f'The report string template file {self.report_string_template} don''exists')
        template = Template(filename=self.report_string_template)
        ret = json.load(template.render())
        return ret


    def getLastResult(self):
        token_login = self.__tokenLogin__()
        #ret = range(1,self.past_values)
        #return ret







