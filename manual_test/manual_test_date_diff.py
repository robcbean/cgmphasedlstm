import datetime
import converttime

date_time_utc: datetime.datetime = datetime.datetime.now()
time_delta: datetime.timedelta = \
    converttime.get_time_diff_from_tz(tzname_src="Europe/Madrid", tzname_dst="UTC")

print(f"{converttime.get_machine_tz()}")
print(f"Time Madrid:{date_time_utc.time()} Time UTC {(date_time_utc-time_delta).time()}")




