EasyStruct
---

EasyStruct is a small py3.7+ library that makes it really easy to
convert between class instances and structs and vice versa.


quickstart
---
```python
from easystruct import EasyStruct, EasyStructBase


class SimpleStruct(EasyStructBase):
    unsigned_short: EasyStruct('H')
    four_shorts: EasyStruct('4h')
    string: EasyStruct('25s')


class BitStruct(SimpleStruct):
    twelve_bits_together: EasyStruct(b'u12')  # notice i'm passing bytes here to indicate bit packing
    four_individual_bits: EasyStruct(b'u1u1u1u1')


def display(s: EasyStructBase):
    packed = s.pack()
    unpacked = type(s).unpack(packed)
    print(80 * '=')
    print(f'packed: {packed}')
    print(f'unpacked: {unpacked}')
    print(f'packed->unpacked == orig?: {unpacked == s}')
    print(80 * '=')


s = SimpleStruct(45, tuple(range(10, 14)), 'hi this is pretty easy')
display(s)

b = BitStruct(12, tuple(range(4)), 'str', 2048, [1, 1, 0, 1])
display(b)

# note EasyStructBase instances are iterable:

b2 = BitStruct(*s, 1024, [1, 0, 0, 1])
display(b2)
```

output:
```text

================================================================================
packed: b'-\x00\n\x00\x0b\x00\x0c\x00\r\x00hi this is pretty easy\x00\x00\x00'
unpacked: SimpleStruct(unsigned_short=45, four_shorts=(10, 11, 12, 13), string='hi this is pretty easy')
packed->unpacked == orig?: True
================================================================================
================================================================================
packed: b'\x0c\x00\x00\x00\x01\x00\x02\x00\x03\x00str\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\r'
unpacked: BitStruct(unsigned_short=12, four_shorts=(0, 1, 2, 3), string='str', twelve_bits_together=2048, four_individual_bits=[1, 1, 0, 1])
packed->unpacked == orig?: True
================================================================================
================================================================================
packed: b'-\x00\n\x00\x0b\x00\x0c\x00\r\x00hi this is pretty easy\x00\x00\x00@\t'
unpacked: BitStruct(unsigned_short=45, four_shorts=(10, 11, 12, 13), string='hi this is pretty easy', twelve_bits_together=1024, four_individual_bits=[1, 0, 0, 1])
packed->unpacked == orig?: True
================================================================================

```


