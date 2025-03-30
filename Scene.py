import os
import random
from PIL import Image
from Element import Element
from TextElement import TextElement
from typing import List, Optional, Tuple


class Scene:
    """
    Represents a scene with a specified width, height, and a list of objects.
    """

    def __init__(self, width: int, height: int, objects: Optional[List[object]] = None):
        """
        Initializes a Scene object.

        Args:
            width: The width of the scene.
            height: The height of the scene.
            objects: A list of objects in the scene.
        """
        self.width = width
        self.height = height
        self.objects = objects if objects is not None else []
        self.create_image()

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        if not isinstance(width, int):
            raise TypeError("Width set failed: width must be an intiger")
        if width < 0:
            raise ValueError("Width set failed: width must be a positive intiger")
        self._width = width

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, height: int) -> None:
        if not isinstance(height, int):
            raise TypeError("Height set failed: height must be an intiger")
        if height < 0:
            raise ValueError("Height set failed: height must be a positive intiger")
        self._height = height

    @property
    def bounding_box(self) -> Tuple[int, int]:
        return (0, 0, self.width, self.height)

    @staticmethod
    def is_box_inside(
        box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]
    ) -> bool:
        """
        Checks if box1 is completely inside box2.

        Args:
            box1: (left, top, right, bottom) coordinates of box1.
            box2: (left, top, right, bottom) coordinates of box2.

        Returns:
            True if box1 is completely inside box2, False otherwise.
        """
        left1, top1, right1, bottom1 = box1
        left2, top2, right2, bottom2 = box2

        return (
            left1 >= left2 and top1 >= top2 and right1 <= right2 and bottom1 <= bottom2
        )

    @staticmethod
    def is_box_touching(
        box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]
    ) -> bool:
        """
        Checks if box2 is touching box1 in any way (including overlapping).

        Args:
            box1: (left, top, right, bottom) coordinates of box1.
            box2: (left, top, right, bottom) coordinates of box2.

        Returns:
            True if box2 touches box1, False otherwise.
        """
        left1, top1, right1, bottom1 = box1
        left2, top2, right2, bottom2 = box2

        return not (
            right2 < left1 or right1 < left2 or bottom2 < top1 or bottom1 < top2
        )

    @staticmethod
    def _validate_element(element: object) -> None:
        if not isinstance(element, (Element, TextElement)):
            raise TypeError("Object must be an Element or a subclass of Element.")

    def create_image(
        self,
        mode: str = "RGB",
        color: str = "white",
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Image.Image:
        """
        Creates a PIL Image for the scene.

        Args:
            mode: The image mode (e.g., "RGB", "RGBA").
            color: The background color of the image.

        Returns:
            A PIL Image object representing the scene.
        """
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        self.image = Image.new(mode, (self.width, self.height), color)
        return self.image

    def add_object(self, element: Element) -> None:
        """
        Adds an object to the scene.

        Args:
            obj: The object to add.
        """
        self._validate_element(element)
        self.objects.append(element)

    def move(self, element: object, position: Tuple[float, float]) -> None:
        self._validate_element(element)
        element.position = position

    def move_random(self, element: object, within_bounds: bool = False) -> None:
        self._validate_element(element)
        if within_bounds:
            left, top, right, bottom = (
                element.bounding_box
            )  # left(-x), top(-y), right(+x), bottom(+y)
            x = random.uniform(-left, self.width - right)
            y = random.uniform(-top, self.height - bottom)
        else:
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)

        element.x = x
        element.y = y

    def place(self, element: object, position: Tuple[float, float]) -> None:
        self.add_object(element)
        self.move(element, position)

    def place_random(self, element: object, within_bounds: bool = False) -> None:
        self.add_object(element)
        self.move_random(element, within_bounds)

    def draw_objects(self) -> None:
        """
        Draws all objects in the scene onto the scene's image.
        """
        if self.image is None:
            raise ValueError("Scene image must be created before drawing objects.")

        for obj in self.objects:
            if not hasattr(obj, "draw") or not callable(obj.draw):
                raise TypeError(f"Object {obj} does not have a draw method.")
            obj.draw(self.image)

    def show(self) -> None:
        """
        Displays the scene's image.
        """
        if not self.image:
            raise ValueError("Image object does not exist for the current Scene.")
        self.image.show()

    def save(self, file_path: str, overwrite_existing: bool = False) -> None:
        """
        Saves the scene's image to a file.

        Args:
            file_path: The filename to save the image to.
            overwrite_existing: If True, overwrite existing files.
        """
        if os.path.exists(file_path) and not overwrite_existing:
            raise FileExistsError(
                f"FileExistsError: File already exists at {file_path}"
            )
        if not self.image:
            raise ValueError("Image object does not exist for the current Scene.")
        self.image.save(file_path)


def main():
    # Create a Scene
    scene = Scene(width=50, height=10)

    # Create the scene's image
    scene.create_image()

    # Add objects (replace with your object classes)

    from PIL import ImageDraw

    test_obj1 = TextElement("Hi", (100, 100))
    test_obj2 = TextElement("Yes", (100, 100))
    test_obj3 = TextElement("Hello", (200, 150), text_color="blue")

    scene.add_object(test_obj1)
    scene.add_object(test_obj2)
    scene.add_object(test_obj3)

    for object in scene.objects:
        scene.move_random(object, False)

    # Draw the objects
    scene.draw_objects()

    # Show and save the scene
    scene.show()
    # scene.save("scene.png")


if __name__ == "__main__":
    main()
