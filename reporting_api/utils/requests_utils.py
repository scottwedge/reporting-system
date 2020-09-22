from flask import g
from flask_restful import reqparse
from werkzeug import datastructures

from ..exceptions.service_error import ServiceError
from ..exceptions.service_exception import ServiceException
from ..exceptions.system_error import SystemError
from ..exceptions.system_exception import SystemException


def _get_request():
    if 'req' not in g:
        g.req = reqparse.RequestParser()
    return g.req


def get_required_argument(key, default=None, type=str):
    kwargs = dict(default=default)

    parser = _get_request()
    parser.add_argument(key, **kwargs)
    args = parser.parse_args()
    try:
        args[key] = type(args[key])
    except:
        return None, False

    else:
        if args[key] is None or type == str and args[key].strip() == '':
            return None, False
        return args[key], True


def get_argument(key, *, default=None, type=str, location=None, help=None, action=None,  # noqa
                 required=False, limit=None, validate=None, encoding=False, trim=False):
    '''
    @param limit: Limit string length.
    @param validate: Limit integer size.  page--> 0 < value < 30; int--> 0 < value < 10000
    '''

    kwargs = dict(default=default)
    if location:
        kwargs['location'] = location
    if action:
        kwargs['action'] = action
    if type == 'file':
        kwargs['type'] = datastructures.FileStorage
        kwargs['location'] = location if location else 'files'

    parser = _get_request()
    parser.add_argument(key, **kwargs)
    args = parser.parse_args()

    if required and (args[key] is None or type == str and args[key].strip() == '' and key != '_id'):
        raise SystemException(SystemError.MISSING_REQUIRED_PARAMETER, help if help else key)

    if args[key] is None or type == 'file':
        return args[key]

    try:
        args[key] = type(args[key])
    except:
        raise ServiceException(ServiceError.INVALID_VALUE)

    if validate and type == int:
        if validate == 'page':
            if not (0 < args[key] <= 100):
                args[key] = default if default else 10
        elif validate == 'int':
            if not (0 < args[key] < 10000):
                raise ServiceException(ServiceError.INVALID_VALUE)

    return args[key]
