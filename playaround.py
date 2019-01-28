from typing import Iterator, NamedTuple

from easystruct import *
import bitstruct
from pprint import pprint

from easystruct.easystruct import _StructField, _StructIterField


class EasyBitStruct(EasyStruct):
    @staticmethod
    def _init_is_str(fmt_str):
        return False

    @staticmethod
    def _init_field(fmt_str, is_str) -> _StructField:
        return _StructIterField(bitstruct.compile(fmt_str), bitstruct.calcsize(fmt_str))


class H(NamedTuple):
    origin: int
    tagged: int
    addressable: int = 1
    protocol: int = 1024

    # not a part of the base tuple
    fmt_str = 'u2u1u1u12'

    @classmethod
    def unpacker(cls, data):
        return cls(*data)

print(H.fmt_str)
print(H(1, 2))


class Header(EasyStructBase):
    size: EasyStruct('<H')
    origin: EasyStruct('<B')
    tagged: EasyStruct('<H')
    addressable: EasyStruct('<H')
    protocol: EasyStruct('<H')
    source: EasyStruct('<H')


class B(Header):
    field: EasyStruct('H')


b = B(1, 2)
pprint(b.__dataclass_fields__)
