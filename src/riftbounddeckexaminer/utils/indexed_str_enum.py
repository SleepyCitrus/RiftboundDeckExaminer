from enum import Enum


class IndexedStrEnum(str, Enum):
    """Enum that represents each enum as a tuple: (name string, index)"""

    def __new__(cls, value, index):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.index = index
        return obj
