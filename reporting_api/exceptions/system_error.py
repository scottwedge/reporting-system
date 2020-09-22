from enum import unique

from .error_core import ErrorCore


@unique
class SystemError(ErrorCore):
    '''
    defined system errors
    '''

    SYSTEM_ERROR = 101001
    SERVICE_UNAVAILABLE = 101002
    REMOTE_SERVICE_ERROR = 101003
    TOO_MANY_PENDING_TASKS = 101004
    JOB_EXPIRED = 101005
    RPC_ERROR = 101006
    DATABASE_ERROR = 101007

    LIMITED_IP_ADDRESS = 102001
    INVALID_REQUEST_BODY = 102002
    MISSING_REQUIRED_PARAMETER = 102003

    MISSING_AUTHORIZATION_HEADER = 102004
    REVOKED_TOKEN_ERROR = 102005
    BAD_AUTHORIZATION_HEADER = 102006
    WRONG_TOKEN_ERROR = 102007
    EXPIRED_SIGNATURE_ERROR = 102008
    INVALID_SIGNATURE_ERROR = 102009
    TOKEN_ERROR = 102010

    def descriptions(self, error, *context):
        '''
        generate error desc
        :params error: SystemError object
        :returns: description with string for error
        '''

        _descriptions = {
            'SYSTEM_ERROR': 'System error',
            'SERVICE_UNAVAILABLE': 'System unavailable',
            'REMOTE_SERVICE_ERROR': 'Remote service error',
            'TOO_MANY_PENDING_TASKS': 'Too many pending tasks, system is busy',
            'JOB_EXPIRED': 'Job expired',
            'RPC_ERROR': 'RPC error',
            'DATABASE_ERROR': 'Database error',

            'LIMITED_IP_ADDRESS': 'Limited IP address',
            'INVALID_REQUEST_BODY': 'Invalid request body',
            'MISSING_REQUIRED_PARAMETER': 'Incorrect parameters',

            'MISSING_AUTHORIZATION_HEADER': 'Missing authorization header',
            'REVOKED_TOKEN_ERROR': 'Revoked token error',
            'BAD_AUTHORIZATION_HEADER': 'Bad Authorization header. Expected value \'Bearer <JWT>\'',
            'WRONG_TOKEN_ERROR': 'Only refresh tokens are allowed',
            'EXPIRED_SIGNATURE_ERROR': 'Expired signature error',
            'INVALID_SIGNATURE_ERROR': 'Signature verification failed',
            'TOKEN_ERROR': 'The token error',
        }

        error_desc = _descriptions[str(error).split('.')[1]]

        if context:
            result = error_desc.format(*context)
            return result

        return error_desc
