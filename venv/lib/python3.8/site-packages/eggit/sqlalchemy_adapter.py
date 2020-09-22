import json
from datetime import date, datetime
from enum import Enum

from sqlalchemy.ext.declarative import DeclarativeMeta


def sqlalchemy_encoder():
    '''
    let the sqlalchemy result set can format with json
    '''
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don not repeat it's self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                fields = {}
                for field in [
                        x for x in dir(obj)
                        if not x.startswith('_') and x != 'metadata'
                ]:
                    data = obj.__getattribute__(field)
                    try:
                        if isinstance(data, datetime):
                            # format datetime
                            data = data.strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(data, Enum):
                            # format enums
                            data = data.name
                        elif isinstance(data, date):
                            data = data.strftime('%Y-%m-%d')
                        elif callable(data):
                            continue
                        json.dumps(data)
                        fields[field] = data
                    except TypeError:
                        pass
                        # fields[field] = None
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder
