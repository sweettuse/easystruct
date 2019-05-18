from easystruct import *


class S(EasyStructBase):
    s: EasyStruct('10s')
    ull: EasyStruct('Q')
    c: EasyStruct('s')


class A(EasyStructBase):
    a: EasyStruct('<4H')
    b: EasyStruct('<12s')


class C(A):
    a: A
    b: EasyStruct('H')


def _create(cls, *args):
    print(80 * '=')
    c = cls(*args)
    print(c)
    print(c.pack())
    print(cls.unpack(c.pack()))
    print(80 * '=')
    return c


def _compare(s: EasyStructBase, packed: bytes):
    s_p = s.pack()
    s_u = s.unpack(packed)

    assert s_p == packed
    assert s == s_u


def test_simple():
    s = S('a', 2 ** 64 - 1, 'c')
    _compare(s, b'a\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xffc')


def test_compound_fields():
    a = A(tuple(range(40, 44)), 'abcdefghi')
    _compare(a, b'(\x00)\x00*\x00+\x00abcdefghi\x00\x00\x00')


def test_compound_objects():
    a = A(tuple(range(40, 44)), 'abcdefghi')
    c = C(a, 65535)
    print(c)
    print(c.pack())
    print(C.unpack(c.pack()))
    return
    _compare(c, b'(\x00)\x00*\x00+\x00abcdefghi\x00\x00\x00\xff\xff')


class Bits(EasyStructBase):
    two_bits: EasyStruct(b'u2')
    nine_bits: EasyStruct(b'u9')


class MultiBits(EasyStructBase):
    three: EasyStruct(b'u4u4u4')
    two: EasyStruct(b'u4u12')
    one: EasyStruct(b'u97')


class BitsBytes(EasyStructBase):
    s: EasyStruct('H')
    twelve_bits: EasyStruct(b'u12')
    seven_bits: EasyStruct(b'u7')
    s2: EasyStruct('12s')


class IterDC(MultiBits):
    other: EasyStruct('<4H')


class BitsBytesStr(EasyStructBase):
    bits: Bits
    s: EasyStruct('12s')
    bits_bytes: BitsBytes


bits = _create(Bits, 2, 255)
bits_bytes = _create(BitsBytes, 4, 1000, 100, 'jebtus')
bbs = _create(BitsBytesStr, bits, 'hello', bits_bytes)
multi = _create(MultiBits, [1, 2, 3], [4, 5], 98273498798729873987298374987)
iter_dc = _create(IterDC, *multi, tuple(range(1000, 1004)))


def test_bits():
    _compare(bits, b'\x9f\xe0')


def test_bits_bytes():
    _compare(bits_bytes, b'\x04\x00>\x8c\x80jebtus\x00\x00\x00\x00\x00\x00')


def test_bbs():
    _compare(bbs, b'\x9f\xe0hello\x00\x00\x00\x00\x00\x00\x00\x04\x00>\x8c\x80jebtus\x00\x00\x00\x00\x00\x00')


def test_multibits():
    _compare(multi, b'\x124\x00Y\xecOv\xa6"A\xc1t\xed}\xaaX')


def test_iterable_dataclass():
    _compare(iter_dc, b'\x124\x00Y\xecOv\xa6"A\xc1t\xed}\xaaX\xe8\x03\xe9\x03\xea\x03\xeb\x03')

