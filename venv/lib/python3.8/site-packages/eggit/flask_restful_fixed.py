from flask_restful import Api
from flask import current_app
from flask import abort as original_flask_abort
from flask import make_response as original_flask_make_response
from flask.signals import got_request_exception
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response as ResponseBase
from flask_restful.utils import http_status_message
import sys


class Api2(Api):
    def __init__(self, app=None, prefix='',
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=False, serve_challenge_on_401=False,
                 url_part_order='bae', errors=None):
        super().__init__(app, prefix,
                 default_mediatype, decorators,
                 catch_all_404s, serve_challenge_on_401,
                 url_part_order, errors)

    def handle_error(self, e):
        """Error handler for the API transforms a raised exception into a Flask
        response, with the appropriate HTTP status code and body.

        :param e: the raised Exception object
        :type e: Exception

        """

        got_request_exception.send(current_app._get_current_object(), exception=e)

        if not isinstance(e, HTTPException) and current_app.propagate_exceptions:
            exc_type, exc_value, tb = sys.exc_info()
            if exc_value is e:
                raise
            else:
                raise e

        # features
        headers = Headers()
        code = 200
        if isinstance(e, HTTPException):
            default_data = {
                'error_code': 100000,
                'msg': str(e),
                'bool_status': False
            }
            code = e.code
        elif type(e).__name__ in ('ServiceException', 'SystemException'):
            default_data = {
                    'error_code': e.error_code,
                    'msg': str(e),
                    'bool_status': False
                    }
        elif type(e).__name__ == 'NoAuthorizationError':
            default_data = {
                    'error_code': 0,
                    'msg': str(e),
                    'bool_status': False
                    }
            code = 401
        elif type(e).__name__ == 'ExpiredSignatureError':
            default_data = {
                    'error_code': 1,
                    'msg': str(e),
                    'bool_status': False
                    }
            code = 401
        elif type(e).__name__ == 'RevokedTokenError':
            default_data = {
                    'error_code': 2,
                    'msg': str(e),
                    'bool_status': False
                    }
            code = 401
        elif type(e).__name__ == 'InvalidHeaderError':
            default_data = {
                    'error_code': 3,
                    'msg': str(e),
                    'bool_status': False
                    }
            code = 401
        elif type(e).__name__ == 'InvalidSignatureError':
            default_data = {
                    'error_code': 4,
                    'msg': str(e),
                    'bool_status': False
                    }
            code = 401
        elif type(e).__name__ == 'MethodNotAllowed':
            default_data = {
                    'error_code': 5,
                    'msg': str(e),
                    'bool_status': False
                    }
            code = 405
        else:
            default_data = {
                'error_code': 100000,
                'msg': 'No response',
                'bool_status': False
            }


        # Werkzeug exceptions generate a content-length header which is added
        # to the response in addition to the actual content-length header
        # https://github.com/flask-restful/flask-restful/issues/534
        remove_headers = ('Content-Length',)

        for header in remove_headers:
            headers.pop(header, None)

        data = getattr(e, 'data', default_data)

        if code and code >= 500:
            exc_info = sys.exc_info()
            if exc_info[1] is None:
                exc_info = None
            current_app.log_exception(exc_info)

        error_cls_name = type(e).__name__
        if error_cls_name in self.errors:
            custom_data = self.errors.get(error_cls_name, {})
            code = custom_data.get('status', 500)
            data.update(custom_data)

        if code == 406 and self.default_mediatype is None:
            # if we are handling NotAcceptable (406), make sure that
            # make_response uses a representation we support as the
            # default mediatype (so that make_response doesn't throw
            # another NotAcceptable error).
            supported_mediatypes = list(self.representations.keys())
            fallback_mediatype = supported_mediatypes[0] if supported_mediatypes else "text/plain"
            resp = self.make_response(
                data,
                code,
                headers,
                fallback_mediatype = fallback_mediatype
            )
        else:
            resp = self.make_response(data, code, headers)

        return resp
