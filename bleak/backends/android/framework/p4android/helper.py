from typing import Iterator


# In python for android java iterators objects are iterable by default. No special handling is needed.
def iterate_java_obj(java_iterable) -> Iterator:
    return java_iterable
