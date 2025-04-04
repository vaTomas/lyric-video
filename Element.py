import math
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
        angle: Optional[Union[int, float]] = None,
    ):
        """
        Initializes an Element object.

        Args:
            position (Optional[Tuple[int, int]]): The (x, y) coordinates of the element.
            bounding_box (Optional[Tuple[int, int, int, int]]): The bounding box coordinates (left, top, right, bottom).
        """
        self.position = position
        self.bounding_box = bounding_box
        self.angle = angle

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

    def _get_bounding_box_edge(self, index: int) -> Optional[Union[int, float]]:
        """Helper function to get a bounding box coordinate by index."""
        if not self.bounding_box:
            return None
        return self.bounding_box[index]

    def _set_bounding_box_edge(self, index: int, value: Union[int, float]) -> None:
        """Helper function to set a bounding box coordinate by index."""
        self._validate_value(value)
        if self.bounding_box:
            new_bounding_box = list(self.bounding_box)
            new_bounding_box[index] = value
            self.bounding_box = tuple(new_bounding_box)
        else:
            new_bounding_box = [None, None, None, None]
            new_bounding_box[index] = value
            self.bounding_box = tuple(new_bounding_box)
        self._fix_bounding_box()

    @property
    def left(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_edge(0)

    @left.setter
    def left(self, value: Union[int, float]) -> None:
        self._set_bounding_box_edge(0, value)

    @property
    def top(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_edge(1)

    @top.setter
    def top(self, value: Union[int, float]) -> None:
        self._set_bounding_box_edge(1, value)

    @property
    def right(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_edge(2)

    @right.setter
    def right(self, value: Union[int, float]) -> None:
        self._set_bounding_box_edge(2, value)

    @property
    def bottom(self) -> Optional[Union[int, float]]:
        return self._get_bounding_box_edge(3)

    @bottom.setter
    def bottom(self, value: Union[int, float]) -> None:
        self._set_bounding_box_edge(3, value)

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
        if not self.position:
            return None

        return self.calculate_absolute_box(self.position)

    @property
    def area(self) -> Optional[Union[int, float]]:
        """
        Calculates the area of the bounding box.

        Returns:
            The area of the bounding box, or None if the bounding box is invalid.
        """
        if not self.bounding_box:
            return None

        if any(coord is None for coord in self.bounding_box):
            return None

        if not all(isinstance(coord, (int, float)) for coord in self.bounding_box):
            return None

        return (self.right - self.left) * (self.bottom - self.top)

    def calculate_absolute_box(self, position: Tuple[float, float]) -> Optional[
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

    @property
    def angle(self) -> Optional[Union[int, float]]:
        return self._angle

    @angle.setter
    def angle(self, angle: Optional[Union[int, float]]) -> None:
        if angle is None:
            angle = None
            return

        if not isinstance(angle, (int, float)):
            raise TypeError("Angle must be an int, float, or None.")
        self._angle = angle % (2 * math.pi)

    @property
    def vertecies(
        self,
    ) -> Optional[
        Tuple[
            Tuple[Union[int, float], Union[int, float]],
            Tuple[Union[int, float], Union[int, float]],
            Tuple[Union[int, float], Union[int, float]],
            Tuple[Union[int, float], Union[int, float]],
        ]
    ]:
        left, top, right, bottom = self.bounding_box
        angle = self.angle
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        vertecies = (
            (left, top),
            (right, top),
            (right, bottom),
            (left, bottom),
        )
        rotated_vertecies = []
        for x, y in vertecies:
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            rotated_vertecies.append((new_x, new_y))
        return tuple(rotated_vertecies)

    @property
    def absolute_vertecies(
        self,
    ) -> Optional[
        Tuple[
            Tuple[Union[int, float], Union[int, float]],
            Tuple[Union[int, float], Union[int, float]],
            Tuple[Union[int, float], Union[int, float]],
            Tuple[Union[int, float], Union[int, float]],
        ]
    ]:
        px, py = self.position
        vertecies = self.vertecies
        absolute_vertecies = []
        for vx, vy in vertecies:
            absolute_vertecies.append((vx + px, vy + py))
        return tuple(absolute_vertecies)


def __test_angle_normalization(item_count=5):
    import random

    angles = []
    for _ in range(item_count):
        angles.append(random.uniform(-100, 100))
    print(angles)

    element_angles = []
    for angle in angles:
        element = Element(angle=angle)
        element_angles.append(element.angle)
    print(element_angles)

    result = all(
        element_angle >= 0 or element_angle <= 2 * math.pi
        for element_angle in element_angles
    )
    print(f"Test | Angle Normalization: {result}")
    return result


def __test_element_vertecies(item_count=5, children=1, size=100):
    import random
    from PIL import Image, ImageDraw

    def generate_random_tuple(num_elements, min_val, max_val):
        return tuple(random.uniform(min_val, max_val) for _ in range(num_elements))

    elements = []
    for _ in range(item_count):
        position = generate_random_tuple(2, 0, size)
        box = generate_random_tuple(4, size * -0.1, size * 0.1)
        for _ in range(children):
            angle = random.uniform(0, 2 * math.pi)
            elements.append(Element(angle=angle, position=position, bounding_box=box))

    image = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(image)
    for element in elements:
        print(element.vertecies)
        print(element.absolute_vertecies)
        draw.polygon(element.absolute_vertecies, outline="black")
        draw.rectangle(element.absolute_bounding_box, outline="red")
        draw.point(element.position, fill="red")
    image.show()


def __test():
    item_count = 5
    __test_element_vertecies(item_count=item_count, children=10, size=1000)
    # __test_angle_normalization(item_count)


if __name__ == "__main__":
    __test()
