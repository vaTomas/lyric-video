from typing import Tuple, Optional, Union
from datetime import timedelta
from PIL import ImageFont, Image, ImageDraw

from .element import Element


class TextElement(Element):
    """
    Represents a text element with optional text, position, padding, bounding box,
    start and end times, and font.
    """

    def __init__(
        self,
        text: str,
        position: Optional[Tuple[float, float]] = None,
        bounding_box: Optional[Tuple[int, int, int, int]] = None,
        angle: Union[int, float] = 0,
        padding: Optional[int] = None,
        start: Optional[timedelta] = None,
        end: Optional[timedelta] = None,
        font: Optional[ImageFont.FreeTypeFont] = None,
        text_alignment="center",
        text_anchor="mm",
        text_color="black",
    ):
        """
        Initializes a TextElement object.

        Args:
            text (Optional[str]): The text content.
            position (Optional[Tuple[int, int]]): The (x, y) coordinates of the text.
            padding (Optional[int]): The padding around the text.
            bounding_box (Optional[Tuple[int, int, int, int]]): The bounding box coordinates (left, top, right, bottom).
            start (Optional[timedelta]): The start time of the text element.
            end (Optional[timedelta]): The end time of the text element.
            font (Optional[ImageFont.FreeTypeFont]): The font used for the text.
        """
        super().__init__(position=position, object_box=bounding_box, angle=angle)

        self.text = text

        self.padding = padding

        self.start = start
        self.end = end

        self.text_alignment = text_alignment
        self.text_anchor = text_anchor
        self.text_color = text_color

        if font is not None:
            self.font = font
        else:
            self.set_font()

    def __repr__(self) -> str:
        """
        Returns a string representation of the TextElement object.
        """
        return (
            f"TextElement("
            f"text={self.text}, "
            f"position={self.position}, "
            f"padding={self.padding}, "
            f"bounding_box={self._object_box}, "
            f"start={self.start}, "
            f"end={self.end}, "
            f"font={self.font}"
            f")"
        )

    @property
    def dict(self) -> dict:
        data = super().dict
        data.update({
            "text": self.text,
            "start": self.start.seconds * 1000 + self.start.microseconds // 1000,
            "end": self.end.seconds * 1000 + self.end.microseconds // 1000,
        })

        return data

    @property
    def font(self) -> ImageFont.FreeTypeFont:
        return self._font

    @font.setter
    def font(self, font: ImageFont.FreeTypeFont) -> None:
        if not isinstance(font, ImageFont.FreeTypeFont):
            raise TypeError(
                "Font set failed: font must be an instance of ImageFont.FreeTypeFont"
            )
        self._font = font
        self.generate_bounding_box()

    def set_font(self, font_path: str = "calibri.ttf", font_size: float = 11) -> None:
        try:
            self._font = ImageFont.truetype(font_path, font_size)
            self.generate_bounding_box()
        except OSError:
            raise OSError(f"Font not found at {font_path}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")

    def set_font_size(self, size: float) -> None:
        if not self._font:
            raise ValueError("Font not set. Cannot change font size.")
        self.set_font(self._font.path, size)

    def set_font_path(self, font_path: str) -> None:
        if not self._font:
            raise ValueError("Font not set. Cannot change font path.")
        self.set_font(font_path, self._font.size)

    def generate_bounding_box(self) -> None:
        if self.font is None:
            raise ValueError("Font must be set before generating bounding box.")
        if self.text is None:
            raise ValueError("Text must be set before generating bounding box.")

        temp_image = Image.new("RGB", (0, 0))
        left, top, right, bottom = ImageDraw.Draw(temp_image).textbbox(
            (0, 0),
            self.text,
            self.font,
            anchor=self.text_anchor,
            align=self.text_alignment,
        )

        self.object_box = (left, top, right, bottom)

    def draw(self, image: Image.Image) -> None:
        """
        Draws the text element onto the given image.

        Args:
            image: The PIL Image object to draw on.
        """
        if not self.text or not self.position or not self.font:
            raise ValueError("Text, position, and font must be set before drawing.")

        draw = ImageDraw.Draw(image)
        draw.text(
            self.position,
            self.text,
            font=self.font,
            fill=self.text_color,
            anchor=self.text_anchor,
            align=self.text_alignment,
        )


def main():
    # Example Usage
    import random
    from datetime import timedelta
    from PIL import ImageDraw, Image
    from subtitle import get_subtitles

    # font = ImageFont.truetype("arial.ttf", 24) #replace with your font.
    # text_element = TextElement(
    #     text="Hello, world!",
    #     position=(100, 200),
    #     padding=10,
    #     bounding_box=(50, 150, 250, 250),
    #     start=timedelta(seconds=5),
    #     end=timedelta(seconds=10),
    #     font=font,
    # )

    subtitles_path = "test/subtitle.srt"
    subtitles = get_subtitles(subtitles_path)
    size = 1000

    text_elements = []

    for subtile in subtitles:
        text_element = TextElement(
            text=subtile.content, start=subtile.start, end=subtile.end
        )
        text_element.position = (random.uniform(0, size), random.uniform(0, size))
        # text_element.generate_bounding_box()
        text_elements.append(text_element)

    image = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(image)

    size = 1
    for text_element in text_elements:
        text_element.set_font_size(size)
        if size % 2 == 0:
            text_element.set_font_path(r"c:\\windows\\fonts\\brushsci.ttf")
        text_element.draw(image)
        draw.rectangle(text_element.bounding_box, outline="green")
        draw.rectangle(text_element.absolute_bounding_box, outline="yellow")
        size += 1
        print(f"{text_element.position}, {text_element.bounding_box}")
        # print(text_element.text)

    image.show()


if __name__ == "__main__":
    main()
