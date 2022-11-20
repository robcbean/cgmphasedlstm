import datetime
import converttime

date_time_utc: datetime.datetime = datetime.datetime.now()
date_time_local: datetime.datetime = \
    converttime.convert_from_tz_to_machine(date_to_convert=date_time_utc, tzname="Europe/Madrid")

print(f"{converttime.get_machine_tz()}")
print(f"date_time_utc:{date_time_utc}\tdate_time_local{date_time_local}")



