from enum import Enum, unique


@unique
class Sex(Enum):
    '''
    sex enum
    '''

    unknown = 0,
    male = 1,
    female = 2
