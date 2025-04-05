import os
from typing import Tuple, Optional, Union
from PIL import Image

from Element import Element


class ImageElement(Element):
    """
    Represents an image element with optional image path, position,
    bounding box, angle, and the loaded PIL Image object.
    """

    def __init__(
        self,
        image_path: Optional[str] = None,
        position: Optional[Tuple[Union[int, float], Union[int, float]]] = None,
        bounding_box: Optional[
            Tuple[
                Union[int, float],
                Union[int, float],
                Union[int, float],
                Union[int, float],
            ]
        ] = None,
        angle: Union[int, float] = 0,
        image: Image = None,
    ):
        super().__init__(position=position, object_box=bounding_box, angle=angle)

        self._image_path = None
        self._image = None

        if not image:
            self.image_path = image_path
        else:
            self.image = image

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, image_path) -> None:
        if image_path is None:
            self._image_path = None
            self.image = None
            return

        if not isinstance(image_path, str):
            raise TypeError(f"Image path must be a string or None.")

        if not os.path.exists(image_path):
            return FileNotFoundError(f"FileNotFoundError: {image_path}")

        self._image_path = image_path
        self.image = Image.open(image_path)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image: Image) -> None:
        if image is None:
            self._image = None
            self.object_box = None
            return

        if not isinstance(image, Image.Image):
            raise TypeError("Image must be an instance of Image.")

        self._image = image
        if self.object_box is None:
            self.object_box = image.getbbox()


def main():
    import sys
    from PIL import ImageDraw

    size = 1000

    image = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(image)

    image_element = ImageElement(image_path='test/image1.jpg', position=(100,100))
    print(sys.getsizeof(image_element))
    print(sys.getsizeof(image))
    image.paste(image_element.image,image_element.position)
    print(sys.getsizeof(image_element))
    print(sys.getsizeof(image))
    image.show()
    

if __name__ == "__main__":
    main()
