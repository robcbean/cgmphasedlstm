from datetime import datetime
from pytz import timezone


def get_diff(now, tzname):
    tz = timezone(tzname)
    utc = timezone('UTC')
    utc.localize(datetime.now())
    delta =  utc.localize(now) - tz.localize(now)
    return delta


now = datetime.utcnow()
print(now)
tzname = 'Europe/Madrid'
delta = get_diff(now, tzname)
print(delta)
now_in_stockholm = now + delta
print(now_in_stockholm)
print(f"{datetime.now().astimezone().tzinfo}")