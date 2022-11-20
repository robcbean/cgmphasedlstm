import datetime
import converttime

date_time_utc: datetime.datetime = datetime.datetime.now() + datetime.timedelta(hours=-1)
date_time_local: datetime.datetime = \
    converttime.convert_from_machine_to_tz(date_to_convert=date_time_utc, tzname="Europe/Madrid")

print(f"{converttime.get_machine_tz()}")
print(f"date_time_utc:{date_time_utc}\tdate_time_local{date_time_local}")

