from enum import unique

from .error_core import ErrorCore


@unique
class ServiceError(ErrorCore):
    '''
    defined serivce errors
    '''

    NO_AUTH = 201001
    RECORD_NOT_FOUND = 201002
    DATA_ALREADY_EXISTS = 201003
    DELETE_FAILED = 201004
    VALUE_TOO_LONG = 201005
    INVALID_VALUE = 201006
    RECORD_ALREADY_EXISTS = 201007
    CUSTOMIZE = 201008

    WRONG_PASSWORD = 202001
    ADMIN_NOT_EXISTS = 202002

    CANNOT_DELETE_SUPER_ADMIN = 203001
    CANNOT_DELETE_YOURSELF = 203002



    def descriptions(self, error, *context):
        '''
        generate error desc
        :params error: ServiceError object
        :returns: description with string for error
        '''

        _descriptions = {

            'NO_AUTH': 'Insufficient permissions',
            'RECORD_NOT_FOUND': '{}',
            'DATA_ALREADY_EXISTS': 'Data already exists',
            'VALUE_TOO_LONG': 'Field value is too long, exceeds limit',
            'DELETE_FAILED': 'Delete failed, please try again',
            'INVALID_VALUE': 'The parameter value is invalid',
            "RECORD_ALREADY_EXISTS": "{}",
            "CUSTOMIZE": "{}",

            'WRONG_PASSWORD': 'Wrong password',
            'ADMIN_NOT_EXISTS': 'Admin not exists',

            'CANNOT_DELETE_SUPER_ADMIN': 'You cannot delete super admin',
            'CANNOT_DELETE_YOURSELF': 'You cannot delete yourself',
        }

        error_desc = _descriptions[str(error).split('.')[1]]

        if context:
            result = error_desc.format(*context)
            return result

        return error_desc
