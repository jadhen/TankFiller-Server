
import datetime


def datetime_2_js_date(year, month, day):
    t = datetime.datetime(year, month, day)
    return (t-datetime.datetime(1970, 1, 1)).total_seconds()*1000
