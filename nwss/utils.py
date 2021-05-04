import datetime


def get_future_date(hours):
    return (datetime.date.today() +
            datetime.timedelta(hours=hours))
