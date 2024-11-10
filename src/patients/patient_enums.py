
from enum import Enum, auto

class Sex(Enum):
    """Patient sex categories"""
    MALE = 'M'
    FEMALE = 'F'

    def __str__(self):
        return self.value

class Ethnicity(Enum):
    """Patient ethnicity categories"""
    WHITE = 'white'
    SOUTH_ASIAN = 'south_asian'
    BLACK = 'black'
    MIXED = 'mixed'
    OTHER = 'other'
    UNKNOWN = 'unknown'

    def __str__(self):
        return self.value