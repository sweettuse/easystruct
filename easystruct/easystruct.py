import re
from contextlib import suppress
from functools import lru_cache
from itertools import islice, groupby, chain
from struct import *
from typing import NamedTuple, Iterator, Dict, Callable, Any, Union, Tuple

import bitstruct

from easystruct.utils import classproperty, dataclass


class _NameNum(NamedTuple):
    name: str
    num: int


class _StructField(NamedTuple):
    """component that actually does the parsing to/from struct bytes"""
    struct: Union[Struct, bitstruct.CompiledFormat]
    num_bytes: int
    multi: bool

    def pack(self, *data) -> bytes:
        return self.struct.pack(*self._prepare(data))

    def unpack(self, byte_stream: Iterator[bytes]):
        # noinspection PyTypeChecker
        res = self.struct.unpack(bytes(islice(byte_stream, self.num_bytes)))
        if self.multi:
            res = [res]
        return res

    def _prepare(self, data):
        res = iter(data[0]) if self.multi else data
        return res


@dataclass
class _BitStructPlaceHolder:
    """represent bitstructs"""
    fmt: str


class EasyStruct:
    """
    class member annotation that, when used in conjunction with EasyStructBase, will allow
    easy transformation from objects to struct representations and back again

    pass a `str` object to create a `Struct`
    pass a `bytes` object to create a `bitstruct`
    """

    def __init__(self, fmt_str: Union[str, bytes], packer: Callable = lambda x: x, unpacker: Callable = lambda x: x):
        self._fmt_str = fmt_str
        self._is_str = self._init_is_str(fmt_str)
        self.field = self._init_field(fmt_str, self._is_str)
        self._packer = packer
        self._unpacker = unpacker

    @classmethod
    def _init_is_str(cls, fmt_str):
        return not isinstance(fmt_str, bytes) and 's' in fmt_str.lower()

    @classmethod
    def _init_field(cls, fmt_str, is_str) -> Union[_StructField, _BitStructPlaceHolder]:
        if isinstance(fmt_str, bytes):
            fs = fmt_str.decode()
            return _BitStructPlaceHolder(fs)

        multi = bool(not is_str and re.search('[0-9]+', fmt_str))
        return _StructField(Struct(fmt_str), calcsize(fmt_str), multi)

    def pack(self, *data) -> bytes:
        """take instance data and put to bytes"""
        if self._is_str:
            data = (d.encode() for d in data)
        return self.field.pack(*self._packer(data))

    def unpack(self, byte_stream: Iterator[bytes]) -> Any:
        """read bytes in"""
        res = self.field.unpack(byte_stream)
        if self._is_str:
            res = (res[0].strip(bytes([0])).decode(),)
        return self._unpacker(res)


class EasyBitStruct(EasyStruct):
    @classmethod
    def _init_field(cls, fmt_str, is_str) -> Union[_StructField, _BitStructPlaceHolder]:
        cp = bitstruct.compile(fmt_str)
        num_bytes, num_bits = divmod(cp.calcsize(), 8)
        return _StructField(cp, num_bytes + bool(num_bits), multi=False)


class _UnpackHelper:
    """allow easy access to chunks of data at a time for unpacking"""
    def __init__(self, data):
        self.data = data
        self._is_iterable = False
        if not isinstance(data, EasyStructBase):
            with suppress(TypeError):
                self.data = iter(data)
                self._is_iterable = True

    def get(self, num):
        if not self._is_iterable:
            return self.data

        res = list(islice(self.data, num))
        if num == 1:
            res = res[0]
        return res


@dataclass
class EasyStructBase:
    """have all classes that you want to transform to/from structs inherit from this at some level"""

    def __init_subclass__(cls, **kwargs):
        dataclass(cls)

    def pack(self):
        res = []
        for names, es in self._structs.items():
            data = ((getattr(self, name), num) for name, num in names)
            res.append(es.pack(*chain.from_iterable(d if num > 1 else [d] for d, num in data)))
        return b''.join(res)

    @classmethod
    def unpack(cls, data: Union[bytes, Iterator[bytes]]) -> 'EasyStructBase':
        data = iter(data)
        res = {}
        for names, es in cls._structs.items():
            dw = _UnpackHelper(es.unpack(data))
            res.update((nn.name, dw.get(nn.num)) for nn in names)

        return cls(**res)

    @classproperty
    @lru_cache()
    def _structs(cls) -> Dict[Tuple[_NameNum, ...], EasyStruct]:
        """return existing structs on the object"""
        structs = {name: field.type for name, field in cls.__dataclass_fields__.items()
                   if isinstance(field.type, EasyStruct)
                   or issubclass(field.type, EasyStructBase)}

        return cls._coalesce_bit_structs(structs)

    @classmethod
    def _coalesce_bit_structs(cls, structs: Dict[str, EasyStruct]):
        """join together bitstructs that are adjacent"""
        res = {}
        key = lambda name_val: isinstance(getattr(name_val[1], 'field', None), _BitStructPlaceHolder)
        for k, vals in groupby(structs.items(), key=key):
            if k:
                names, fmts = [], []
                for name, placeholder in vals:
                    fmt = placeholder.field.fmt
                    names.append(_NameNum(name, bitstruct.compile(fmt)._number_of_arguments))
                    fmts.append(fmt)
                res[tuple(names)] = EasyBitStruct(''.join(fmts))
            else:
                for name, s in vals:
                    res[(_NameNum(name, 1),)] = s
        return res
