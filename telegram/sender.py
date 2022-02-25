import requests
import sys

class TelegramSender:

    def __init__(self, _chat_id, _token, _verbose=False):
        self.chat_id = _chat_id
        self.token = _token
        self.verbose = _verbose

    def sendImage(self,_image_path):
        url = f'https://api.telegram.org/bot{self.token}/sendPhoto'
        files = {'photo': open(_image_path, 'rb')}
        data = {'chat_id': f'{self.chat_id}'}
        r = requests.post(url, files=files, data=data)
        if self.verbose:
            sys.stderr.write(f'{r.status_code} {r.reason} {r.content}')

    def sendMessage(self,_message):
        url_api = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_id}&text={_message}'
        requests.post(url_api).json()



