import re
from dataclasses import dataclass
from functools import lru_cache
from itertools import islice
from struct import *
from typing import NamedTuple, Iterator, Dict, Callable


class _StructField(NamedTuple):
    """component that actually does the parsing to/from struct bytes"""
    struct: Struct
    num_bytes: int

    def pack(self, data) -> bytes:
        return self.struct.pack(*self.prepare(data))

    def unpack(self, byte_stream: Iterator):
        res = self.struct.unpack(bytes(islice(byte_stream, self.num_bytes)))
        return res[0] if len(res) == 1 else res

    @classmethod
    def prepare(cls, data):
        return [data]


class _StructIterField(_StructField):
    """used for fields that have multiple items (e.g. '4d')"""

    @classmethod
    def prepare(cls, data):
        return iter(data)


class EasyStruct:
    """
    class member annotation that, when used in conjunction with EasyStructBase, will allow
    easy transformation from objects to struct representations and back again
    """

    def __init__(self, fmt_str: str, packer: Callable = lambda x: x, unpacker: Callable = lambda x: x):
        self._fmt_str = fmt_str
        self.is_str = 's' in self._fmt_str.lower()
        self.field = self._init_field(fmt_str, self.is_str)
        self.packer = packer
        self.unpacker = unpacker

    @staticmethod
    def _init_field(fmt_str, is_str) -> _StructField:
        field_cls = _StructIterField if not is_str and re.search('[0-9]+', fmt_str) else _StructField
        return field_cls(Struct(fmt_str), calcsize(fmt_str))

    def pack(self, d):
        """take instance data and put to bytes"""
        if self.is_str:
            d = d.encode()
        return self.field.pack(self.packer(d))

    def unpack(self, byte_stream: Iterator):
        """read bytes in"""
        res = self.field.unpack(byte_stream)
        if self.is_str:
            res = res.strip(bytes([0])).decode()
        return self.unpacker(res)


@dataclass
class EasyStructBase:
    """have all classes that you want to transform to/from structs inherit from this at some level"""

    def __init_subclass__(cls, **kwargs):
        dataclass(cls)

    def pack(self):
        return b''.join(es.pack(getattr(self, name)) for name, es in self._structs().items())

    @classmethod
    def unpack(cls, data: bytes) -> 'EasyStructBase':
        data = iter(data)
        res = {name: es.unpack(data) for name, es in cls._structs().items()}
        return cls(**res)

    @classmethod
    @lru_cache()
    def _structs(cls) -> Dict[str, EasyStruct]:
        return {name: field.type for name, field in cls.__dataclass_fields__.items()
                if isinstance(field.type, EasyStruct)
                or issubclass(field.type, EasyStructBase)}
