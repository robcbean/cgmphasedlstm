from converttime import get_diff_from_utc, convert_to_utc, convert_from_utf
from datetime import timedelta
from datetime import datetime


def test_get_diff() -> None:

    tznone: str = "Europe/Madrid"

    time_delta_expected: timedelta = timedelta(hours=+1)
    time_delta: timedelta = get_diff_from_utc(date_to_convert=datetime.now(), tzname=tznone)

    assert time_delta_expected == time_delta

    expected_time_to: datetime = datetime.now() + timedelta(hours=-1)
    time_to: datetime = convert_to_utc(date_to_convert=expected_time_to, tzname=tznone)
    expected_time_from: datetime = datetime.now() + timedelta(hours=+1)
    time_from: datetime = convert_from_utf(date_to_convert=expected_time_from, tzname=tznone)

    print(f"\nExpected: {expected_time_to} Actual: {time_to}\n")
    #assert expected_time_to == time_to

    print(f"\nExpected: {expected_time_from} Actual: {time_from}\n")
    #assert expected_time_from == time_from
