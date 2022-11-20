import datetime
import converttime

time_utc: datetime.time = datetime.datetime.now()
time_local: datetime.datetime = \
    converttime.convert_time_from_tz_to_machine(date_to_convert=time_utc, tzname="Europe/Madrid")

print(f"{converttime.get_machine_tz()}")
print(f"date_time_utc:{time_utc}\tdate_time_local{time_local}")



