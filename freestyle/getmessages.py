import datetime
import json
import os
import platform
import sys
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from lxml import html
from mako.template import Template


class GetMessages:
    def __init__(self, _user: str, _password: str, _past_values: int):
        self.user: str = _user
        self.password: str = _password
        self.past_values: int = _past_values
        self.cg_interval_min_p: int = 0

    def get_last_result(self):
        raise Exception("getLastResult not implemented")

    @property
    def cg_interval_min(self):
        if self.cg_interval_min_p == 0:
            raise Exception("Continuos Glusose Interval not set.")
        return self.cg_interval_min_p

    @cg_interval_min.setter
    def cg_interval_min(self, _cg_interval_min):
        self.cg_interval_min_p = _cg_interval_min


class GetMessageFreeStytle(GetMessages):
    def __init__(
            self,
            _user,
            _password,
            _finger_print,
            _base_url,
            _report_string_template,
            _past_values,
            _double_factor,
    ):
        super(GetMessageFreeStytle, self).__init__(_user, _password, _past_values)
        self.cg_interval_min = 15
        self.finger_print = _finger_print
        self.base_url = _base_url
        self.report_string_template = _report_string_template
        self.double_factor = _double_factor

    def __login_url__(self):
        ret = f'{urljoin(self.base_url, "auth/login")}'
        return ret

    def __time_to_add__(self):
        if platform.system().lower() == "linux":
            ret = datetime.timedelta(hours=-2)
        else:
            ret = datetime.timedelta(hours=-1)
        return ret

    def __report_url__(self) -> str:
        ret: str = f'{urljoin(self.base_url, "/reports")}'
        return ret

    @property
    def __send_code_url__(self) -> str:
        ret: str = f'{urljoin(self.base_url, "/auth/continue/2fa/sendcode")}'
        return ret
    @property
    def __result_code_url__(self) -> str:
        ret: str = f'{urljoin(self.base_url, "/auth/continue/2fa/result")}'
        return ret

    def __login_params__(self):
        ret = {
            "email": self.user,
            "fingerprint": self.finger_print,
            "password": self.password,
        }
        return ret

    def __token_header__(self, _token_login):
        ret = {"Autorization": f"Bearer {_token_login}"}
        return ret

    def __token_login_single_factor__(self):
        login_url = self.__login_url__()
        params = self.__login_params__()
        response_login = requests.post(login_url, json=params).json()
        ret = response_login["data"]["authTicket"]["token"]
        return ret

    def __report_string__(self):
        today_date = int(
            (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        )
        # today_date = int((datetime.datetime.now(datetime.timezone.utc) - datetime.datetime(1970, 1, 1)).total_seconds())
        start_date = today_date - (24 * 60 * 60 + 60)
        if not os.path.exists(self.report_string_template):
            raise Exception(
                f"The report string template file {self.report_string_template} don"
                "t exists."
            )
        template = Template(filename=self.report_string_template)
        template_rended = template.render(today_date=today_date, start_date=start_date)
        ret = json.loads(template_rended)
        return ret

    def get_token_header(self, token: str) -> dict:
        token_header: dict  = {"Authorization": "Bearer " + token}
        return token_header

    def __get_url_reports__(self, _report_url, _reports_string, _token_login):
        response_reports = requests.post(
            _report_url, json=_reports_string, headers=self.get_token_header(_token_login)
        ).json()
        ret = response_reports["data"]["url"]
        return ret

    def __get_data_result__(self, _url_reports, _token_login):

        options_report_first = requests.options(_url_reports)
        if options_report_first == "":
            pass

        options_report_second = requests.get(_url_reports).json()
        time.sleep(2)

        url_lp = options_report_second["data"]["lp"]
        report_url_json = requests.get(url_lp).json()

        if "urls" in report_url_json["args"].keys():
            report_url = (
                    report_url_json["args"]["urls"]["10"] + "?session=" + _token_login
            )
            resport_result = requests.get(report_url)
            time.sleep(2)
        else:
            sys.stderr.write(f'Error {report_url_json["args"].keys()}')
            return self.get_last_result()

        tree = html.fromstring(resport_result.content)
        json_string_data = \
            tree.xpath("/html/head/script[contains(text(),'window.report')]")[0].text.split(';')[1].split('=')[1]
        ret = json.loads(json_string_data)['Data']['Days']

        return ret

    def __get_data_resultds_proceseed__(self, _data_result):

        cont_values = []
        cont_dates = []
        send_values = []
        send_dates = []

        hours_to_add = self.__time_to_add__()
        for day in _data_result:
            cont_data = day["Glucose"]
            for data_c in cont_data:
                for value_c in data_c:
                    time_value = int(value_c["Timestamp"])
                    date_value = (
                            datetime.datetime.fromtimestamp(time_value) + hours_to_add
                    )
                    if (
                            date_value.hour != 0
                            and date_value.minute != 0
                            and date_value.second != 0
                    ):  # RBC 12/09/21 quito los valores exactos están mal
                        glucose_value = int(value_c["Value"])
                        cont_dates.append(date_value)
                        cont_values.append(glucose_value)
            sen_data = day["SensorScans"]
            for data_s in sen_data:
                val = data_s["Timestamp"]
                time_value = int(val)
                date_value = datetime.datetime.fromtimestamp(time_value)
                date_value = date_value + hours_to_add
                if (
                        date_value.hour != 0
                        and date_value.minute != 0
                        and date_value.second != 0
                ):  # RBC 12/09/21 quito los valores exactos están mal
                    glucose_value = int(data_s["Value"])
                    send_values.append(glucose_value)
                    send_dates.append(date_value)

        ret_c = pd.Series(cont_values, index=cont_dates)
        ret_c = ret_c.sort_index()
        ret_c.index.name = "time"

        ret_s = pd.Series(send_values, index=send_dates)
        ret_s = ret_s.sort_index()
        ret_s.index.name = "time"

        return ret_c, ret_s



    def __request_send_code_to_mobile__(self, _token: str) -> str:
        message: dict = {
            "isPrimaryMethod": True
        }
        request_code = requests.post(self.__send_code_url__, json=message, headers=self.get_token_header(_token)).json()
        ret: str = request_code["ticket"]["token"]

        return ret


    def __token_login_double_factor__(self, _token_login: str):
        ret: str = _token_login

        return ret

    def get_last_result(self):
        token_login: str = ""
        while token_login == "":
            try:
                token_login_single_factor: str = self.__token_login_single_factor__()
                if not self.double_factor:
                    token_login = self.__token_login_double_factor__(token_login_single_factor)
                else:
                    token_login = __
            except:
                time.sleep(5 * 60)

        url_reports = self.__get_url_reports__(
            self.__report_url__(), self.__report_string__(), token_login
        )
        data_result = self.__get_data_result__(url_reports, token_login)
        ret_c, ret_s = self.__get_data_resultds_proceseed__(data_result)
        return ret_c, ret_s
