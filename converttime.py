from datetime import datetime
from datetime import timedelta
from pytz import timezone
import time


def get_machine_tz() -> str:
    ret: str = time.tzname[1]
    return ret

def get_diff_from_utc(date_to_convert: datetime, tzname: str = "Europe/Madrid") -> timedelta:
    tz = timezone(tzname)
    utc = timezone('UTC')
    utc.localize(datetime.now())
    delta: timedelta = utc.localize(date_to_convert) - tz.localize(date_to_convert)
    return delta


def convert_to_utc(date_to_convert: datetime, tzname: str = "Europe/Madrid") -> datetime:
    time_delta: timedelta = get_diff_from_utc(date_to_convert=date_to_convert, tzname=tzname)
    ret: datetime = date_to_convert - time_delta
    return ret

def convert_from_utf(date_to_convert: datetime, tzname: str = "Europe/Madrid") -> datetime:
    time_delta: timedelta = get_diff_from_utc(date_to_convert=date_to_convert, tzname=tzname)
    ret: datetime = date_to_convert + time_delta
    return ret

def date_machine_to_utc(date_to_convert: datetime.date) -> datetime.date:
    ret: datetime.date = convert_to_utc(date_to_convert=date_to_convert, tzname=get_machine_tz())
    return ret

def utc_to_date_machine(date_to_convert: datetime.date) -> datetime.date:
    ret = datetime.date = convert_from_utf(date_to_convert=date_to_convert, tzname=GetMessageFreeStytle.UTC_TZONE)
    return ret

def utc_to_display(date_to_convert: datetime.date) -> datetime.date:
    ret: datetime.date = convert_from_utf(date_to_convert=date_to_convert, tzname=self.tz_to_display)
    return ret

