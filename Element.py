from typing import Tuple, Optional, Union


class Element:
    """
    Represents a graphical element with position and bounding box.
    """

    def __init__(
        self,
        position: Optional[Tuple[Union[int, float], Union[int, float]]] = None,
        bounding_box: Optional[
            Tuple[
                Union[int, float],
                Union[int, float],
                Union[int, float],
                Union[int, float],
            ]
        ] = None,
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
    def position(self) -> Optional[Tuple[Union[int, float], Union[int, float]]]:
        return self._position

    @position.setter
    def position(
        self, value: Optional[Tuple[Union[int, float], Union[int, float]]]
    ) -> None:
        self._validate_tuple(value)
        self._position = value

    @property
    def x(self) -> Optional[Union[int, float]]:
        if not self._position:
            return None
        return self._position[0]

    @x.setter
    def x(self, value: Union[int, float]) -> None:
        self._validate_value(value)
        if self._position:
            self._position = (value, self._position[1])
        else:
            self._position = (value, None)

    @property
    def y(self) -> Optional[Union[int, float]]:
        if not self._position:
            return None
        return self._position[1]

    @y.setter
    def y(self, value: Union[int, float]) -> None:
        self._validate_value(value)
        if self._position:
            self._position = (self._position[0], value)
        else:
            self._position = (None, value)

    @property
    def bounding_box(self) -> Optional[
        Tuple[
            Union[int, float],
            Union[int, float],
            Union[int, float],
            Union[int, float],
        ]
    ]:
        return self._bounding_box

    @bounding_box.setter
    def bounding_box(
        self,
        box: Tuple[
            Union[int, float],
            Union[int, float],
            Union[int, float],
            Union[int, float],
        ],
    ) -> None:
        # if box is None:
        #     self._bounding_box = None
        #     return
        self._validate_tuple(box, 4)
        # if (
        #     not isinstance(box, tuple)
        #     or len(box) != 4
        #     or not all(isinstance(coord, (int, float)) for coord in box)
        # ):
        #     raise ValueError("Bounding box must be a tuple of four integers.")

        self._bounding_box = box
        self._fix_bounding_box()

    def _get_bounding_box_coord(self, index: int) -> Optional[Union[int, float]]:
        """Helper function to get a bounding box coordinate by index."""
        if not self._bounding_box:
            return None
        return self._bounding_box[index]

    def _set_bounding_box_coord(self, index: int, value: Union[int, float]) -> None:
        """Helper function to set a bounding box coordinate by index."""
        self._validate_value(value)
        if self._bounding_box:
            new_bounding_box = list(self._bounding_box)
            new_bounding_box[index] = value
            self._bounding_box = tuple(new_bounding_box)
        else:
            new_bounding_box = [None, None, None, None]
            new_bounding_box[index] = value
            self._bounding_box = tuple(new_bounding_box)
        self._fix_bounding_box()

    @property
    def left(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_coord(0)

    @left.setter
    def left(self, value: Union[int, float]) -> None:
        self._set_bounding_box_coord(0, value)

    @property
    def top(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_coord(1)

    @top.setter
    def top(self, value: Union[int, float]) -> None:
        self._set_bounding_box_coord(1, value)

    # Add right and bottom properties similarly...

    @property
    def right(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_coord(2)

    @right.setter
    def right(self, value: Union[int, float]) -> None:
        self._set_bounding_box_coord(2, value)

    @property
    def bottom(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_coord(3)

    @bottom.setter
    def bottom(self, value: Union[int, float]) -> None:
        self._set_bounding_box_coord(3, value)

    def _fix_bounding_box(self):
        if not self._bounding_box:
            return

        left, top, right, bottom = self._bounding_box

        if left and right:
            if left > right:
                left, right = right, left

        if top and bottom:
            if top > bottom:
                top, bottom = bottom, top

        self._bounding_box = (left, top, right, bottom)

    @property
    def absolute_bounding_box(self) -> Optional[
        Tuple[
            Union[int, float],
            Union[int, float],
            Union[int, float],
            Union[int, float],
        ]
    ]:
        if not self._position:
            return None

        return self._calculate_absolute_box(self._position)

    def simulate_absolute_bounding_box(
        self, position: Tuple[Union[int, float], Union[int, float]]
    ) -> Optional[
        Tuple[
            Union[int, float],
            Union[int, float],
            Union[int, float],
            Union[int, float],
        ]
    ]:
        return self._calculate_absolute_box(position)

    def _calculate_absolute_box(self, position: Tuple[float, float]) -> Optional[
        Tuple[
            Union[int, float],
            Union[int, float],
            Union[int, float],
            Union[int, float],
        ]
    ]:
        self._validate_tuple(position)
        if not self._bounding_box:
            return None

        left, top, right, bottom = self._bounding_box
        x, y = position

        return (
            left + x if left is not None else None,
            top + y if top is not None else None,
            right + x if right is not None else None,
            bottom + y if bottom is not None else None,
        )

    @staticmethod
    def _validate_tuple(
        value: any,
        members: int = 2,
    ) -> None:
        """Validates if the position is a tuple of two numbers or None."""
        if value is None:
            return  # None is valid

        is_tuple = isinstance(value, tuple)
        has_two_elements = len(value) == members
        are_numbers = all(isinstance(coord, (int, float)) for coord in value)

        if not (is_tuple and has_two_elements and are_numbers):
            raise ValueError(
                f"Position must be a tuple of {members} floats, ints, or None."
            )

    @staticmethod
    def _validate_value(value: any):
        if value is None:
            return
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a float, int, or None")
