import sys
import datetime
import logging

SUFFIX_LOG__NAME: str = f"cgmphasedlstm.log"

class MessageType:
    ERROR: int = 0
    MESSAGE: int = 1


class LogMessages:

    stderr: object = None
    stdout: object = None
    logger: logging.Logger
    app_name: str

    def __init__(self, app_name: str, stdout=sys.stdout, stderr=sys.stderr) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.app_name = app_name
        self.logger = self.setup_login()
    def setup_login(self) -> logging.Logger :
        ret: logging.Logger

        logging.basicConfig(filename=SUFFIX_LOG__NAME,
                                format="%(asctime)s - %(message)s" )
        ret = logging.getLogger(self.app_name)
        ret.setLevel(logging.INFO)
        return ret

    def write_to_log(self, message: str, message_type: MessageType) -> None:
        self.setup_login()
        if message_type == MessageType.MESSAGE:
            self.send_output_message(message)
        elif message_type == MessageType.ERROR:
            self.send_error_message(message)
        else:
            raise Exception(f"Message type not defined")

    def send_output_message(self, message: str) -> None:
        self.stdout.write(message + "\n")
        self.logger.info(message)

    def send_error_message(self, message: str) -> None:
        self.stderr.write(message + "\n")
        self.logger.error(message)


