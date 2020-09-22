import os

from eggit.flask_restful_response import error
from flask import current_app
from flask.signals import got_request_exception
from flask_jwt_extended.exceptions import (JWTExtendedException, NoAuthorizationError,
                                           RevokedTokenError, InvalidHeaderError, WrongTokenError)
from flask_restful import Api as BaseApi
from jwt.exceptions import PyJWTError, ExpiredSignatureError, InvalidSignatureError, DecodeError
from werkzeug.exceptions import HTTPException

from ..exceptions .service_exception import ServiceException
from ..exceptions.system_exception import SystemException


class Api(BaseApi):

    def __init__(self, app=None, prefix='',
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=True, serve_challenge_on_401=False,
                 url_part_order='bae', errors=None):
        super().__init__(app, prefix,
                         default_mediatype, decorators,
                         catch_all_404s, serve_challenge_on_401,
                         url_part_order, errors)

    def handle_error(self, e):  # noqa
        got_request_exception.send(current_app._get_current_object(), exception=e)

        code = 200
        result = None

        if isinstance(e, HTTPException):
            raise HTTPException()
        elif isinstance(e, ServiceException) or isinstance(e, SystemException):
            result = error(msg=str(e), error_code=e.error_code, http_status_code=code)
        elif issubclass(type(e), JWTExtendedException):
            code = 401
            if isinstance(e, NoAuthorizationError):
                result = error(msg=str(SystemException(102004)), error_code=102004, http_status_code=code)
            elif isinstance(e, RevokedTokenError):
                result = error(msg=str(SystemException(102005)), error_code=102005, http_status_code=code)
            elif isinstance(e, InvalidHeaderError):
                result = error(msg=str(SystemException(102006)), error_code=102006, http_status_code=code)
            elif isinstance(e, WrongTokenError):
                result = error(msg=str(SystemException(102007)), error_code=102007, http_status_code=code)
        elif issubclass(type(e), PyJWTError):
            code = 401
            if isinstance(e, ExpiredSignatureError):
                result = error(msg=str(SystemException(102008)), error_code=102008, http_status_code=code)
            elif isinstance(e, InvalidSignatureError):
                result = error(msg=str(SystemException(102009)), error_code=102009, http_status_code=code)
            elif isinstance(e, DecodeError):
                result = error(msg=str(SystemException(102010)), error_code=102010, http_status_code=code)
        else:
            code = 500
            result = error(
                msg=str(e) if not os.environ.get('PRODUCTION_CONFIG') else 'No response',
                error_code=100001,
                http_status_code=code
            )

        return result
