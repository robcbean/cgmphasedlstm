import sys
import datetime
import logging

DATE_SUFFIX: str = "#SUFIX#"
SUFFIX_LOG__NAME: str = f"log_{DATE_SUFFIX}.log"


class MessageType:
    ERROR: int = 0
    MESSAGE: int = 1


class LogMessages:

    stderr: object = None
    stdout: object = None
    log_date: datetime.date

    def __init__(self, stdout=sys.stdout, stderr=sys.stderr) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.log_date = datetime.datetime.today()
        self.setup_login()

    def setup_login(self):
        logging.basicConfig(filename=self.get_file_name())
    def get_file_name(self):
        ret: str = SUFFIX_LOG__NAME.replace(SUFFIX_LOG__NAME, DATE_SUFFIX, self.log_date.strftime("%Y%m%d"))
        return ret

    def write_to_log(self, message: str, message_type: MessageType) -> None:
        if datetime.datetime.today() != self.log_date:
            self.log_date = datetime.datetime.today()
            self.setup_login()
        if message_type == MessageType.MESSAGE:
            self.send_output_message(message)
        elif message_type == MessageType.ERROR:
            self.send_error_message(message)
        else:
            raise Exception(f"Message type not defined")

    def send_output_message(self, message: str) -> None:
        self.stdout.write(message + "\n")
        logging.info(message)

    def send_error_message(self, message: str) -> None:
        self.stderr.write(message + "\n")
        logging.error(message)
