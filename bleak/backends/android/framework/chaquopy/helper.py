from typing import Iterator, TypeVar

from java.lang import Iterable

T = TypeVar("T")


def iterate_java_obj(java_iterable: "Iterable[T]") -> Iterator[T]:
    iterator = java_iterable.iterator()
    while iterator.hasNext():
        yield iterator.next()
