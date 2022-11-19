import sys
import logging

SUFFIX_LOG__NAME: str = f"cgmphasedlstm.log"


class MessageType:
    ERROR: int = 0
    MESSAGE: int = 1


class LogMessages:
    stderr: object = None
    stdout: object = None
    app_name: str

    def __init__(self, app_name: str = "cgm", stdout=sys.stdout, stderr=sys.stderr) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.app_name = app_name

    def get_logger(self, message_type: int) -> logging.Logger:
        ret: logging.Logger

        logging.basicConfig(filename=SUFFIX_LOG__NAME,
                            format="%(asctime)s - %(message)s")
        ret = logging.getLogger(self.app_name)
        if message_type == MessageType.MESSAGE:
            ret.setLevel(logging.INFO)
        else:
            ret.setLevel(logging.ERROR)
        return ret

    def write_to_log(self, message: str, message_type: int = MessageType.MESSAGE) -> None:
        if message_type == MessageType.MESSAGE:
            self.send_output_message(message, message_type)
        elif message_type == MessageType.ERROR:
            self.send_error_message(message, message_type)
        else:
            raise Exception(f"Message type not defined")
        logging.shutdown()

    def remove_new_lines(self, message: str) -> str:
        ret: str = message.replace("\n", " ")
        return ret

    def send_output_message(self, message: str, message_type: int) -> None:
        self.stdout.write(message + "\n")
        self.get_logger(message_type).info(self.remove_new_lines(message))

    def send_error_message(self, message: str, message_type: int) -> None:
        self.stderr.write(message + "\n")
        self.get_logger(message_type).error(self.remove_new_lines(message))
