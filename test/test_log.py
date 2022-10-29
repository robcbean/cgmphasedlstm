from logmessages.Log import LogMessages, MessageType
import datetime


def test_log() -> None:
    log_message: LogMessages = LogMessages()
    #today: datetime.date = datetime.date.today()

    log_message.write_to_log(message="Message", message_type=MessageType.MESSAGE)
    log_message.write_to_log(message="Error", message_type=MessageType.ERROR)
    log_message.write_to_log(message="Error", message_type=MessageType.ERROR)



test_log()