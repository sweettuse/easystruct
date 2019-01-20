import inspect

from functools import lru_cache
from itertools import chain, islice
from struct import *
from typing import NamedTuple, Iterable


class StructField(NamedTuple):
    struct: Struct
    num_bytes: int

    def pack(self, data) -> bytes:
        return self.struct.pack(*self.prepare(data))

    def unpack(self, byte_stream: Iterable):
        res = self.struct.unpack(bytes(islice(byte_stream, self.num_bytes)))
        res = res[0] if len(res) == 1 else res
        return res

    @classmethod
    def prepare(cls, data):
        return [data]


class StructIterField(StructField):
    @classmethod
    def prepare(cls, data):
        return iter(data)


class EasyStruct:
    def __init__(self, fmt_str: str, field_cls=StructField):
        self._fmt_str = fmt_str
        self.field = field_cls(Struct(fmt_str), calcsize(fmt_str))

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def pack(self):
        d = self.instance.payload[self.name]
        print(d)
        return self.field.pack(d)

    def unpack(self, data):
        res = self.field.unpack(data)
        print('fdup', res)
        self.instance.__dict__[self.name] = res


class ColorStruct(EasyStruct):
    def __init__(self):
        super().__init__('<4H', StructIterField)


class EasyStructBase:
    def __init__(self, payload):
        self.payload = payload

    def pack(self):
        return b''.join(getattr(self, name).pack() for name in self._lifx_fields())

    @classmethod
    def unpack(cls, data: bytes):
        res = cls({})
        data = iter(data)
        for name in cls._lifx_fields():
            getattr(res, name).unpack(data)
        return res

    @classmethod
    @lru_cache()
    def _lifx_fields(cls):
        data = chain(*(vars(c).items() for c in reversed(inspect.getmro(cls))))
        fields = [name for name, f in data if isinstance(f, EasyStruct)]
        print(fields)
        return fields

    def __str__(self):
        fields = {name: getattr(self, name) for name in self._lifx_fields()}
        field_str = ', '.join(f'{k}={v}' for k, v in fields.items())
        return f'{type(self).__name__}({field_str})'


class M1(EasyStructBase):
    short = EasyStruct('H')


class M2(M1):
    color = ColorStruct()


class M3(M2):
    string = EasyStruct('12s')


c = 1, 2, 3, 4

m2 = M2(dict(short=c[0], color=c))
t = m2.pack()
t = t
print(t)
new_m2 = M2.unpack(t)
print(new_m2)
print(new_m2.short + 2)

m3 = M3(dict(short=c[0], color=c, string=b'snth'))
print(M3.unpack(m3.pack()))

from dataclasses import dataclass
@dataclass
class Jeb:
    a: EasyStruct('H')
