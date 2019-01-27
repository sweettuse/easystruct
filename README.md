EasyStruct
---

EasyStruct is a small py3.6+ library that makes it really easy to
convert between class instances and structs and vice versa.


quickstart
---
```python
from easystruct import EasyStruct, EasyStructBase

class ToStruct(EasyStructBase):
    unsigned_short: EasyStruct('H')
    four_shorts: EasyStruct('4h')
    string: EasyStruct('25s')

class Extend(ToStruct):
    extra: EasyStruct('d')
   
   
e = Extend(45, tuple(range(10, 14)), 'hi this is pretty easy', 7.2)
print('packed:', e.pack())
new_e = Extend.unpack(e.pack())
print('access vars and add them:', new_e.unsigned_short + new_e.extra)
print('orig:', e)
print('new: ', new_e)
```

output:
```
packed: b'-\x00\n\x00\x0b\x00\x0c\x00\r\x00hi this is pretty easy\x00\x00\x00\xcd\xcc\xcc\xcc\xcc\xcc\x1c@'
access vars and add them: 52.2
orig: Extend(unsigned_short=45, four_shorts=(10, 11, 12, 13), string='hi this is pretty easy', extra=7.2)
new:  Extend(unsigned_short=45, four_shorts=(10, 11, 12, 13), string='hi this is pretty easy', extra=7.2)
```


