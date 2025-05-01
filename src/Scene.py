import os
import math
import random
from PIL import Image
from typing import List, Optional, Tuple, Union
from elements import Element, TextElement, ImageElement


class Scene:
    """
    Represents a scene with a specified width, height, and a list of objects.
    """

    def __init__(
        self,
        width: int,
        height: int,
        elements: Optional[List[object]] = None,
    ):
        """
        Initializes a Scene object.

        Args:
            width: The width of the scene.
            height: The height of the scene.
            objects: A list of objects in the scene.
        """
        self.width = width
        self.height = height
        self.elements = elements if elements is not None else []

    @property
    def dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "elements": [element.dict for element in self.elements],
        }

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
    def artboard_box(self) -> Tuple[int, int]:
        return (0, 0, self.width, self.height)

    def element_index(self, element: Union[Element, TextElement]) -> Optional[int]:
        try:
            return self.elements.index(element)
        except ValueError:
            return None

    @staticmethod
    def is_box_inside(
        inside_box: Tuple[float, float, float, float],
        outside_box: Tuple[float, float, float, float],
        outside_box_margin: Union[int, float] = 0,
        inside_box_padding: Union[int, float] = 0,
    ) -> bool:
        """
        Checks if inside_box is completely inside outside_box, considering margins and padding.

        Args:
            inside_box: (left, top, right, bottom) coordinates of the inside box.
            outside_box: (left, top, right, bottom) coordinates of the outside box.
            outside_box_margin: Margin applied to the outside box.
            inside_box_padding: Padding applied to the inside box.

        Returns:
            True if inside_box is completely inside outside_box, False otherwise.
        """

        if not all(
            isinstance(coord, (int, float))
            for box in (inside_box, outside_box)
            for coord in box
        ):
            raise TypeError("Coordinates must be int or float.")

        inside_left, inside_top, inside_right, inside_bottom = inside_box
        outside_left, outside_top, outside_right, outside_bottom = outside_box

        return (
            inside_left - inside_box_padding >= outside_left + outside_box_margin
            and inside_top - inside_box_padding >= outside_top + outside_box_margin
            and inside_right + inside_box_padding <= outside_right - outside_box_margin
            and inside_bottom + inside_box_padding
            <= outside_bottom - outside_box_margin
        )

    @staticmethod
    def is_box_touching(
        box1: Tuple[
            Union[int, float], Union[int, float], Union[int, float], Union[int, float]
        ],
        box2: Tuple[
            Union[int, float], Union[int, float], Union[int, float], Union[int, float]
        ],
        minimum_distance: Union[int, float] = 0,
    ) -> bool:
        """
        Checks if box2 is touching box1 in any way (including overlapping).

        Args:
            box1: (left, top, right, bottom) coordinates of box1.
            box2: (left, top, right, bottom) coordinates of box2.

        Returns:
            True if box2 touches box1, False otherwise.
        """
        if not all(
            isinstance(coord, (int, float)) for box in (box1, box2) for coord in box
        ):
            raise TypeError("Coordinates must be int or float.")

        left1, top1, right1, bottom1 = box1
        left2, top2, right2, bottom2 = box2

        return not (
            right2 + minimum_distance < left1
            or right1 + minimum_distance < left2
            or bottom2 + minimum_distance < top1
            or bottom1 + minimum_distance < top2
        )

    @staticmethod
    def _validate_element(element: object) -> None:
        if not isinstance(element, (Element, TextElement, ImageElement)):
            raise TypeError("Object must be an Element or a subclass of Element.")

    def create_image(
        self,
        mode: str = "RGBA",
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
        self.elements.append(element)

    def move(self, element: object, position: Tuple[float, float]) -> None:
        self._validate_element(element)
        element.position = position

    def move_random(
        self,
        element: object,
        constrain_to_artboard: bool = False,
        artboard_margin: Union[int, float] = 0,
        collision: bool = False,
        scene_elements: Optional[
            List[Union["Element", "TextElement", "ImageElement"]]
        ] = None,
        minimum_distance: Optional[Union[int, float]] = None,
        max_attempts: Union[int, float] = 100,
    ) -> Optional[Tuple[Union[int, float], Union[int, float]]]:
        """
        Moves an element to a random position within the scene.

        Args:
            element: The element to move.
            constrain_to_artboard: If True, constrains the element to the artboard boundaries.
            artboard_margin: Margin to apply when constraining to the artboard.
            collision: If True, ensures that the new position does not collide with other elements.
            scene_elements: A list of scene elements to check for collisions; if None, uses self.elements.
            minimum_distance: The minimum allowed distance between elements when checking for collisions.
            max_attempts: Maximum number of attempts to find a valid position.

        Returns:
            The new position of the element (x, y) if found, otherwise None.
        """
        self._validate_element(element)

        for _ in range(int(max_attempts)):
            if constrain_to_artboard:
                if (artboard_margin * 2) >= self.height or (
                    artboard_margin * 2
                ) >= self.width:
                    raise ValueError("Margin is too large for the artboard dimensions.")
                left, top, right, bottom = (
                    element.bounding_box
                )  # (left, top, right, bottom)
                x = random.uniform(
                    -left + artboard_margin, self.width - right - artboard_margin
                )
                y = random.uniform(
                    -top + artboard_margin, self.height - bottom - artboard_margin
                )
            else:
                x = random.uniform(0, self.width)
                y = random.uniform(0, self.height)

            if not collision:
                element.position = (x, y)
                return (x, y)

            if scene_elements is None:
                scene_elements = self.elements

            if minimum_distance is None:
                minimum_distance = 0

            collided = False
            for scene_element in scene_elements:
                if scene_element is element:
                    continue
                if self.is_box_touching(
                    element.calculate_absolute_box((x, y), element.bounding_box),
                    scene_element.absolute_bounding_box,
                    minimum_distance,
                ):
                    collided = True
                    break

            if not collided:
                element.position = (x, y)
                return (x, y)

        return None

    def place(self, element: object, position: Tuple[float, float]) -> None:
        self.add_object(element)
        self.move(element, position)

    def place_random(
        self,
        element: object,
        constrain_to_artboard: bool = False,
        artboard_margin: Union[int, float] = 0,
        collision: bool = False,
        scene_elements: Optional[
            List[Union[Element, TextElement, ImageElement]]
        ] = None,
        minimum_distance: Optional[Union[int, float]] = None,
        max_attempts: Optional[Union[int, float]] = 100,
    ) -> None:
        self.add_object(element)
        self.move_random(
            element,
            constrain_to_artboard,
            artboard_margin,
            collision,
            scene_elements,
            minimum_distance,
            max_attempts,
        )

    def move_next(
        self,
        element: Union[Element, TextElement],
        reference_element: Optional[Union[Element, TextElement]] = None,
        angle: Optional[Union[int, float]] = None,  # degrees
        # additional_elements: Optional[Union[Element, TextElement]] = None,
        minimum_distance: Union[int, float] = 0,  # bounding box
        within_bounds_sctrict: bool = True,
        artboard_margin: Union[int, float] = 0,
        max_attempts: Optional[int] = None,
    ) -> None:
        """
        Moves an element next to another element.
        """
        self._validate_element(element)

        if reference_element is not None:
            self._validate_element(reference_element)
        if not reference_element:
            if not self.elements:
                raise Exception(
                    "No objects found in scene to automatically reference from."
                )
            reference_element = self.elements[self.element_index(element) - 1]

        if max_attempts is None:
            max_attempts = int(max(self.height, self.width))

        furthest_distance_incriment = (
            math.sqrt(self.width**2 + self.height**2) / max_attempts
        )

        for attempt_number in range(max_attempts):
            distance = (attempt_number + 1) * furthest_distance_incriment

            if angle is None:
                dx = distance * random.uniform(-1, 1)
                dy = distance * random.uniform(-1, 1)
            else:
                dx = distance * math.cos(math.radians(angle))
                dy = distance * math.sin(math.radians(angle))

            new_position = (reference_element.x + dx, reference_element.y + dy)
            preview_bounding_box = element.calculate_absolute_box(
                new_position, element.bounding_box
            )

            if within_bounds_sctrict and not self.is_box_inside(
                preview_bounding_box,
                self.artboard_box,
                outside_box_margin=artboard_margin,
            ):
                continue

            if self.is_box_touching(
                preview_bounding_box,
                reference_element.absolute_object_box,
                minimum_distance,
            ):
                continue

            scene_elements = self.elements
            # if additional_elements is not None:
            #     elements.extend(additional_elements)

            touching = False
            for scene_element in scene_elements:
                if scene_element is element:
                    continue
                if scene_element.position is None or any(
                    coord is None for coord in scene_element.position
                ):
                    continue
                if self.is_box_touching(
                    preview_bounding_box,
                    scene_element.absolute_bounding_box,
                    minimum_distance,
                ):
                    touching = True
                    break
            if touching:
                continue

            element.position = new_position
            return True

        return False

    def draw_objects(self) -> None:
        """
        Draws all objects in the scene onto the scene's image.
        """
        if self.image is None:
            raise ValueError("Scene image must be created before drawing objects.")

        for obj in self.elements:
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

    for object in scene.elements:
        scene.move_random(object, True, artboard_margin=4)

    # Draw the objects
    scene.draw_objects()

    # Show and save the scene
    scene.show()
    # scene.save("scene.png")


if __name__ == "__main__":
    main()
