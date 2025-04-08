import os
import math
from PIL import Image, ImageOps
from typing import Tuple, Optional, Union

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
        object_box: Optional[
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
        super().__init__(position=position, object_box=object_box, angle=angle)

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

    def draw(self, image: Image) -> None:
        if self.image is None:
            return

        self._validate_tuple(value=self.size, members=2, allow_none=False)

        size = tuple(int(dimension) for dimension in self.size)

        _image = ImageOps.exif_transpose(self.image).convert("RGBA")
        _image = _image.resize(size=size, resample=Image.Resampling.LANCZOS)
        _image = _image.rotate(
            math.degrees(self.angle), expand=True, resample=Image.Resampling.BICUBIC
        )

        self._validate_tuple(value=self.position, members=2, allow_none=False)
        image.paste(_image, self.position, _image)


def main():
    import sys
    import random
    from PIL import ImageDraw, ImageOps

    canvas_size = 1000
    image_path = "test/image1.jpg"
    image_size = 500

    image = Image.new("RGBA", (canvas_size, canvas_size), color="white")
    draw = ImageDraw.Draw(image)

    # rotation_angle = 30
    # img = Image.open(image_path)
    # img = ImageOps.exif_transpose(img)
    # img = img.resize((image_size, image_size)).convert("RGBA")
    # img = img.rotate(rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)
    # img.show()

    image_element = ImageElement(
        image_path,
        position=(100, 100),
        object_box=(0, 0, image_size / 2, image_size / 2),
        angle=math.radians(30),
    )
    print(sys.getsizeof(image_element))
    print(sys.getsizeof(image))
    image_element.draw(image)
    # image.paste(image_element.image, image_element.position)
    # print(sys.getsizeof(image_element))
    # print(sys.getsizeof(image))
    image.show()


if __name__ == "__main__":
    main()
