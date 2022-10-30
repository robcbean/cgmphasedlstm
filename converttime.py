from datetime import datetime
from datetime import timedelta
from pytz import timezone


def get_diff_from_utc(date_to_convert: datetime, tzname: str = "Europe/Madrid") -> timedelta:
    tz: str = timezone(tzname)
    utc: str = timezone('UTC')
    #utc.localize(datetime.now())
    delta: timedelta = utc.localize(date_to_convert) - date_to_convert
    return delta


def convert_to_utc(date_to_convert: datetime, tzname: str = "Europe/Madrid") -> datetime:
    time_delta: timedelta = get_diff_from_utc(date_to_convert=date_to_convert, tzname=tzname)
    ret: datetime = date_to_convert - time_delta
    return ret


def convert_from_utf(date_to_convert: datetime, tzname: str = "Europe/Madrid") -> datetime:
    time_delta: timedelta = get_diff_from_utc(date_to_convert=date_to_convert, tzname=tzname)
    ret: datetime = date_to_convert + time_delta
    return ret
