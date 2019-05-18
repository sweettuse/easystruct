from dataclasses import dataclass as orig_dataclass
from functools import partial


def dataclass(_cls=None, *, iter=True, **kwargs):
    """make dataclass classes iterable"""

    if _cls is None:
        return partial(dataclass, _cls, iter=iter, **kwargs)

    new_cls = orig_dataclass(_cls, **kwargs)

    if iter:
        def _iter(self):
            yield from (getattr(self, attr) for attr in self.__dataclass_fields__)

        def _len(self):
            return len(self.__dataclass_fields__)

        new_cls.__iter__ = _iter
        new_cls.__len__ = _len

    return new_cls


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, cls):
        return self.f(cls)
