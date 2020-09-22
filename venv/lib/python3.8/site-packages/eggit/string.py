import time
from datetime import datetime


class DTFormat(object):
    date_format = None
    datetime_format = None

    def __init__(self, date_format='%Y-%m-%d', datetime_format='%Y-%m-%d %H:%M:%S'):
        self.date_format = date_format
        self.datetime_format = datetime_format


class DateTimeUtils():

    @staticmethod
    def timestamp_to_datetime_object(timestamp):
        '''
        1514736000 --> datetime object

        :param timestamp: unix timestamp
        :returns: datetime object
        :raises ValueError: timestamp string format error
        '''
        if isinstance(timestamp, (int, float, str)):
            try:
                timestamp = int(timestamp)
            except ValueError:
                return None

            if len(str(timestamp)) == 13:
                timestamp = int(timestamp / 1000)
            if len(str(timestamp)) != 10:
                return None

        else:
            return None

        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def to_time_stamp(datetime_str):
        '''
        2018-01-01 00:00:00 -->  1514736000

        :param datetime_str: datetime string
        :returns: unix time stamp
        :raises ValueError: datetime string format error
        '''
        try:
            dtf = DTFormat()
            struct_time = time.strptime(datetime_str, dtf.datetime_format)
            return time.mktime(struct_time)
        except ValueError as e:
            return None

    @staticmethod
    def now():
        '''
        get now datetime

        :returns: datetime string
        '''
        dft = DTFormat()
        return datetime.now().strftime(dft.datetime_format)

    @staticmethod
    def get_datetime_string(datetime_obj):
        '''
        get datetime string from datetime object

        example:
            DateTimeUtils.get_datetime_string(datetime.now())

        :param datetime_obj: datetime object
        :returns: datetime string
        '''

        dft = DTFormat()
        return datetime_obj.strftime(dft.datetime_format)

    @staticmethod
    def get_datetime_object(datetime_str):
        '''
        get datetime object from datetime string

        example:
            DateTimeUtils.get_datetime_object('2018-01-01 00:00:00')

        :param datetime string: datetime string
        :returns: datetime object
        '''

        dft = DTFormat()
        return datetime.strptime(datetime_str, dft.datetime_format)

    def timestamp_to_datetime_string(timestamp):
        '''
        1514736000 --> 2018-01-01 00:00:00 (string)

        :param timestamp: unix timestamp
        :returns: datetime object
        :raises ValueError: timestamp string format error
        '''

        return DateTimeUtils.get_datetime_string(DateTimeUtils.timestamp_to_datetime_object(timestamp))
