import sys
from  urllib.parse import urljoin
import requests
import datetime
import os
import time
import json
from mako.template import Template
from lxml import html
import platform
import pandas as pd


class GetMessages:
    def __init__(self,_user,_password,_past_values):
        self.user = _user
        self.password = _password
        self.past_values = _past_values
        self.cg_interval_min_p = 0
    def getLastResult(self):
        raise Exception('getLastResult not implemented')
    @property
    def cg_interval_min(self):
        if self.cg_interval_min_p == 0:
            raise  Exception('Continuos Glusose Interval not set.')
        return self.cg_interval_min_p

    @cg_interval_min.setter
    def cg_interval_min(self, _cg_interval_min):
        self.cg_interval_min_p = _cg_interval_min


class GetMessageFreeStle(GetMessages):
    def __init__(self,_user,_password,_finger_print,_base_url,_report_string_template,_past_values):
        super(GetMessageFreeStle, self).__init__(_user,_password,_past_values)
        self.cg_interval_min = 15
        self.finger_print = _finger_print
        self.base_url = _base_url
        self.report_string_template = _report_string_template

    def __loginURL__(self):
        ret = f'{urljoin(self.base_url,"auth/login")}'
        return ret

    def __timeToAdd__(self):
        if platform.system().lower() == "linux":
            ret = datetime.timedelta(hours=-2)
        else:
            ret = datetime.timedelta(hours=-1)
        return ret

    def __reportURL(self):
        ret = f'{urljoin(self.base_url,"/reports")}'
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
        login_url = self.__loginURL__()
        params = self.__loginParams__()
        response_login = requests.post(login_url, json=params).json()
        ret = response_login['data']['authTicket']['token']
        return ret

    def __reportString__(self):
        today_date = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()) 
        #today_date = int((datetime.datetime.now(datetime.timezone.utc) - datetime.datetime(1970, 1, 1)).total_seconds())
        start_date = today_date - (24 * 60 * 60 + 60)
        if not os.path.exists(self.report_string_template):
            raise Exception(f'The report string template file {self.report_string_template} don''t exists.')
        template = Template(filename=self.report_string_template)
        template_rended = template.render(today_date=today_date,start_date=start_date)
        ret = json.loads(template_rended)
        return ret

    def __getUrlReports__(self,_report_url,_reports_string,_token_login):
        token_header = {'Authorization': 'Bearer ' + _token_login}
        response_reports = requests.post(_report_url, json=_reports_string, headers=token_header).json()
        ret = response_reports['data']['url']
        return ret

    def __getDataResult__(self,_url_reports,_token_login):

        options_report_first = requests.options(_url_reports)
        if options_report_first == "":
            pass

        options_report_second = requests.get(_url_reports).json()
        time.sleep(2)

        url_lp = options_report_second['data']['lp']
        report_url_json = requests.get(url_lp).json()

        if 'urls' in report_url_json['args'].keys():
            report_url = report_url_json['args']['urls']['10'] + '?session=' + _token_login
            resport_result = requests.get(report_url)
            time.sleep(2)
        else:
            sys.stderr.write(f'Error {report_url_json["args"].keys()}')
            return self.getLastResult()

        tree = html.fromstring(resport_result.content)
        json_string_data = \
            tree.xpath("/html/head/script[contains(text(),'DataForLibreWeeklySummary')]")[0].text.split(';')[1].split('=')[1]
        ret = json.loads(json_string_data)['Data']['Days']

        return ret

    def __getDataResultsProcessed__(self,_data_result):

        cont_values = []
        cont_dates = []
        send_values = []
        send_dates = []

        hours_to_add = self.__timeToAdd__()
        for day in _data_result:
            cont_data = day['Glucose']
            for data_c in cont_data:
                for value_c in data_c:
                    time_value = int(value_c['Timestamp'])
                    date_value = datetime.datetime.fromtimestamp(time_value) + hours_to_add
                    if date_value.hour != 0 and date_value.minute != 0 and date_value.second != 0:  # RBC 12/09/21 quito los valores exactos están mal
                        glucose_value = int(value_c['Value'])
                        cont_dates.append(date_value)
                        cont_values.append(glucose_value)
            sen_data = day['SensorScans']
            for data_s in sen_data:
                val = data_s['Timestamp']
                time_value = int(val)
                date_value = datetime.datetime.fromtimestamp(time_value)
                date_value = date_value  + hours_to_add
                if date_value.hour != 0 and date_value.minute != 0 and date_value.second != 0:  # RBC 12/09/21 quito los valores exactos están mal
                    glucose_value = int(data_s['Value'])
                    send_values.append(glucose_value)
                    send_dates.append(date_value)

        ret_c = pd.Series(cont_values, index=cont_dates)
        ret_c = ret_c.sort_index()
        ret_c.index.name = 'time'

        ret_s = pd.Series(send_values, index=send_dates)
        ret_s = ret_s.sort_index()
        ret_s.index.name = 'time'

        return ret_c,ret_s

    def getLastResult(self):
        token_login = self.__tokenLogin__()
        url_reports = self.__getUrlReports__(self.__reportURL(), self.__reportString__(),token_login)
        data_result = self.__getDataResult__(url_reports,token_login)
        ret_c,ret_s = self.__getDataResultsProcessed__(data_result)
        return ret_c, ret_s







