class Converter(object):
    '''
    converters
    '''

    @staticmethod
    def str_to_int(str_val):
        '''
        convert string to int

        :param str_val: the source string value
        :returns: the target integer value
        :raises ValueError: trigs when user provide an error str_val
        '''

        try:
            return int(str_val)
        except ValueError:
            return None

    @staticmethod
    def str_to_bool(str_val):
        '''
        convert string to boolean

        :param str_val: the source string value
        :returns: the target boolean value
        '''
        if (str_val == 'False'):
            return False

        return True
