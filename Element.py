from typing import Tuple, Optional


class Element:
    """
    Represents a graphical element with position and bounding box.
    """

    def __init__(
        self,
        position: Optional[Tuple[float, float]] = (0.0, 0.0),
        bounding_box: Optional[Tuple[int, int, int, int]] = None,
    ):
        """
        Initializes an Element object.

        Args:
            position (Optional[Tuple[int, int]]): The (x, y) coordinates of the element.
            bounding_box (Optional[Tuple[int, int, int, int]]): The bounding box coordinates (left, top, right, bottom).
        """
        self.position = position
        self.bounding_box = bounding_box

    def __repr__(self) -> str:
        return f"Element(position={self.position}, bounding_box={self._bounding_box})"

    @property
    def position(self) -> Optional[Tuple[float, float]]:
        return self._position

    @position.setter
    def position(self, value: Optional[Tuple[float, float]]) -> None:
        if value is None or (
            isinstance(value, tuple)
            and len(value) == 2
            and all(isinstance(coord, (int, float)) for coord in value)
        ):
            self._position = value
        else:
            raise ValueError("Position must be a tuple of two floats or ints, or None.")

    @property
    def x(self) -> Optional[float]:
        if not self._position:
            return None
        return self._position[0]

    @x.setter
    def x(self, value: float) -> None:
        if self._position:
            self._position = (value, self._position[1])
        else:
            self._position = (value, 0)

    @property
    def y(self) -> Optional[float]:
        if not self._position:
            return None
        return self._position[1]

    @y.setter
    def y(self, value: int) -> None:
        if self._position:
            self._position = (self._position[0], value)
        else:
            self._position = (0, value)

    @property
    def bounding_box(self) -> Optional[Tuple[int, int, int, int]]:
        return self._bounding_box

    @bounding_box.setter
    def bounding_box(self, box: Optional[Tuple[int, int, int, int]]) -> None:
        if box is None:
            self._bounding_box = None
            return

        if (
            not isinstance(box, tuple)
            or len(box) != 4
            or not all(isinstance(coord, (int, float)) for coord in box)
        ):
            raise ValueError("Bounding box must be a tuple of four integers.")

        self._bounding_box = box
        self._fix_bounding_box()

    @property
    def left(self) -> Optional[int]:
        if not self._bounding_box:
            return None
        return self._bounding_box[0]

    @left.setter
    def left(self, value: int) -> None:
        if self._bounding_box:
            self._bounding_box = (
                value,
                self._bounding_box[1],
                self._bounding_box[2],
                self._bounding_box[3],
            )
        else:
            self._bounding_box = (value, 0, 0, 0)
        self._fix_bounding_box()

    @property
    def top(self) -> Optional[int]:
        if not self._bounding_box:
            return None
        return self._bounding_box[1]

    @top.setter
    def top(self, value: int) -> None:
        if self._bounding_box:
            self._bounding_box = (
                self._bounding_box[0],
                value,
                self._bounding_box[2],
                self._bounding_box[3],
            )
        else:
            self._bounding_box = (0, value, 0, 0)
        self._fix_bounding_box()

    @property
    def right(self) -> Optional[int]:
        if not self._bounding_box:
            return None
        return self._bounding_box[2]

    @right.setter
    def right(self, value: int) -> None:
        if self._bounding_box:
            self._bounding_box = (
                self._bounding_box[0],
                self._bounding_box[1],
                value,
                self._bounding_box[3],
            )
        else:
            self._bounding_box = (0, 0, value, 0)
        self._fix_bounding_box()

    @property
    def bottom(self) -> Optional[int]:
        if not self._bounding_box:
            return None
        return self._bounding_box[3]

    @bottom.setter
    def bottom(self, value: int) -> None:
        if self._bounding_box:
            self._bounding_box = (
                self._bounding_box[0],
                self._bounding_box[1],
                self._bounding_box[2],
                value,
            )
        else:
            self._bounding_box = (0, 0, 0, value)
        self._fix_bounding_box()

    def _fix_bounding_box(self):
        if not self._bounding_box:
            return

        left, top, right, bottom = self._bounding_box

        if left > right:
            left, right = right, left
        if top > bottom:
            top, bottom = bottom, top

        self._bounding_box = (left, top, right, bottom)

    @property
    def absolute_bounding_box(self) -> Optional[Tuple[int, int, int, int]]:
        if not self._bounding_box or not self._position:
            return None

        left, top, right, bottom = self._bounding_box
        x, y = self._position

        return (left + x, top + y, right + x, bottom + y)