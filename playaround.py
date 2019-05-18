from typing import Iterator, NamedTuple

from easystruct import *
import bitstruct
from pprint import pprint

from easystruct.easystruct import _StructField


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


class Bits(EasyStructBase):
    one_bit: EasyStruct(b'u1')
    four_bits: EasyStruct(b'u4')


class FiveBits(EasyStructBase):
    one_bit: EasyStruct(b'u1')
    four_bits: EasyStruct(b'u4')
    five_bits: EasyStruct(b'u1u4')


# b = Bits(1, 3)
# print(b.pack())
# print(Bits.unpack(b.pack()))

# fb = FiveBits(1, 2, [1, 2])
# print(fb)
# print(len(fb.pack()))
# print(fb.pack())
# print(FiveBits.unpack(fb.pack()))

class EightBits(EasyStructBase):
    three_bits: EasyStruct(b'u3')
    five_bits: EasyStruct(b'u5')


class TenBits(EasyStructBase):
    three_bits: EasyStruct(b'u3')
    five_bits: EasyStruct(b'u5')
    two_bits: EasyStruct(b'u2')


# eb = EightBits(4, 7)
# print(eb)
# print(eb.pack())
# print(EightBits.unpack(eb.pack()))
# # print(EightBits.unpack(eb.pack()))
#
# tb = TenBits(4, 30, 3)
# print(tb)
# print(tb.pack())
# print(TenBits.unpack(tb.pack()))


# class Orig(EasyStructBase):
#     shorts: EasyStruct('<4H')
#
#
# tb = Orig([1, 2, 3, 1])
# print(tb)
# print(tb.pack())
# print(Orig.unpack(tb.pack()))

class S(EasyStructBase):
    i: EasyStruct('<H')
    s: EasyStruct('12s')


s = S(4, 'jebtuse')
print(s)
print(s.pack())
print(S.unpack(s.pack()))


# class Extra(TenBits):
#     shorts: EasyStruct('<4H')

# tb = Extra(4, 30, 3, [1, 2, 3, 4])
# print(tb)
# print(tb.pack())
# print(Extra.unpack(tb.pack()))
#
# class Other(EasyStructBase):
#     t: EasyStruct(b'<H')


# o = Other(12)
# print(o)
# print(o.pack())

# b = B(*range(7))
# pprint(b.__dataclass_fields__)
# pprint(b.pack())
# h = H(*range(4))
# print(h)
# # print(h.pack())
