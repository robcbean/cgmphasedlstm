from pytz import timezone
import time
import datetime

UTC_TZONE: str = "UTC"

def get_machine_tz() -> str:
    ret: str = time.tzname[0]
    return ret

def get_time_diff_from_tz(tzname_src: str = "UTC", tzname_dst: str = "CET") -> datetime.timedelta:
    date_to_convert: datetime.datetime = datetime.datetime.now()
    dst_time_zone = timezone(tzname_dst)
    src_time_zone = timezone(tzname_src)
    delta: datetime.timedelta = dst_time_zone.localize(date_to_convert) - src_time_zone.localize(date_to_convert)
    return delta






