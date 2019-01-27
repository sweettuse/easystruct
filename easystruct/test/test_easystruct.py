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


def _compare(s: EasyStructBase, packed):
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
    _compare(c, b'(\x00)\x00*\x00+\x00abcdefghi\x00\x00\x00\xff\xff')
