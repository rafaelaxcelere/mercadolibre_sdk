import dateutil.parser as dateutil_parser
import pytz


def iso8601_to_datetime_utc(iso8601_date):
    datestring = iso8601_date
    parsed = dateutil_parser.parse(datestring)
    date_utc = parsed.replace(tzinfo=pytz.utc) - parsed.utcoffset()
    return date_utc.replace(tzinfo=None)
