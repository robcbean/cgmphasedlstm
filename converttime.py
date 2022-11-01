from pytz import timezone
import time
import datetime


UTC_TZONE: str = "UTC"

def get_machine_tz() -> str:
    ret: str = time.tzname[0]
    return ret

def get_diff_from_utc(date_to_convert: datetime.datetime, tzname: str = "CET") -> datetime.timedelta:
    tz = timezone(tzname)
    utc = timezone('UTC')
    utc.localize(datetime.datetime.now())
    delta: datetime.timedelta = utc.localize(date_to_convert) - tz.localize(date_to_convert)
    return delta


def convert_to_utc(date_to_convert: datetime.datetime, tzname: str = "CET") -> datetime.datetime:
    time_delta: datetime.timedelta = get_diff_from_utc(date_to_convert=date_to_convert, tzname=tzname)
    ret: datetime.datetime = date_to_convert + time_delta
    return ret


def convert_from_utf(date_to_convert: datetime.datetime, tzname: str = "CET") -> datetime.datetime:
    time_delta: datetime.timedelta = get_diff_from_utc(date_to_convert=date_to_convert, tzname=tzname)
    ret: datetime.datetime = date_to_convert - time_delta
    return ret


def datetime_machine_to_utc(date_to_convert: datetime.datetime) -> datetime.datetime:
    ret: datetime.datetime = convert_to_utc(date_to_convert=date_to_convert, tzname=get_machine_tz())
    return ret


def utc_to_datetime_machine(date_to_convert: datetime.datetime) -> datetime.datetime:
    ret = datetime.datetime = convert_from_utf(date_to_convert=date_to_convert, tzname=get_machine_tz())
    return ret


def utc_to_display(date_to_convert: datetime, tz_to_display: str = "CET") -> datetime.datetime:
    ret: datetime.datetime = convert_from_utf(date_to_convert=date_to_convert, tzname=tz_to_display)
    return ret
