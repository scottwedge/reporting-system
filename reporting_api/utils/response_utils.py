from collections import Counter
from datetime import datetime
from enum import Enum
from decimal import Decimal
from sqlalchemy.exc import DatabaseError
from eggit.flask_restful_response import ok
from ..exceptions.system_error import SystemError
from ..exceptions.system_exception import SystemException


def obj_to_dict(obj, keys=None, *, display=True, format_time='%Y-%m-%d %H:%M:%S'):
    '''Get the specified key value of the model
    :param obj: The model object to be converted.
    :param keys: Key name to process. What you want to include or not in the returned results, e.g. ['name', 'sex']
    :param display: If it is "True", the :keys: includes the result of the return, otherwise it is excluded.
    :param format_time: Format a field that is a datetime type
    '''
    dict_result = {}
    if obj:
        obj_values = obj.__dict__

        for key in obj_values:
            if key == '_sa_instance_state':
                continue
            if (display and key in keys) or (not display and key not in keys):
                key_value = obj_values.get(key)
                if isinstance(key_value, datetime):
                    dict_result[key] = datetime.strftime(key_value, format_time)
                elif isinstance(key_value, Enum):
                    dict_result[key] = key_value.value
                elif isinstance(key_value, Decimal):
                    dict_result[key] = str(key_value)
                elif isinstance(key_value, float):
                    dict_result[key] = round(key_value, 2)
                else:
                    dict_result[key] = key_value
    return dict_result


def db_commit(db, msg=''):
    try:
        db.session.commit()
    except DatabaseError as e:
        db.session.rollback()
        raise SystemException(SystemError.DATABASE_ERROR)
    else:
        return ok(msg=msg)


def dict_sum(x, y):
    X, Y = Counter(x), Counter(y)
    z = dict(X + Y)
    return z


def double_point(number):
    return round(number, 2)


def four_point(number):
    return round(number, 4)
