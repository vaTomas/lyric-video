from typing import Any


class Keyframe:
    def __init__(self, time: int = 0, value: Any = None):
        self.time = time
        self.value = value

    @property
    def time(self) -> int:
        """The time milliseconds of this keyframe."""
        return self._time

    @time.setter
    def time(self, t: int):
        self._time = t

    @property
    def value(self) -> Any:
        """The payload or value at this keyframe."""
        return self._value

    @value.setter
    def value(self, v: Any):
        self._value = v


def test():
    import random

    x = random.uniform(-15, 16)
    y = random.uniform(-15, 16)
    t = random.uniform(0, 100)

    kf = Keyframe(t, (x, y))
    print(kf.time == t)
    print(kf.value == (x, y))


if __name__ == "__main__":
    test()
