from typing import Optional, Union, Tuple


Pos = Union[complex, Tuple[float, float]]


def func(p: Optional[Pos]):
    if isinstance(p, complex):
        x = p.real
        y = p.imag
    elif isinstance(p, tuple):
        x, y = p
    else:
        x = y = 0
    print(x, y)


func(None)
