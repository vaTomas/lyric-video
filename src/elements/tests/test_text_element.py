import pytest
from datetime import timedelta
from PIL import Image, ImageFont

# Assuming TextElement is in module text_element.py in project root
from elements import TextElement


def test_default_font_and_bounding_box():
    # Create with minimal args
    te = TextElement(text="Hello", start=timedelta(seconds=1), end=timedelta(seconds=2))
    # font should be set to default and bounding_box generated
    assert hasattr(te, 'font') and isinstance(te.font, ImageFont.FreeTypeFont)
    assert te._object_box is not None
    # dict property returns ms
    d = te.dict
    assert d['start'] == 1000
    assert d['end'] == 2000
    assert d['text'] == "Hello"


def test_font_setter_type_error():
    te = TextElement(text="Hi", start=timedelta(), end=timedelta())
    with pytest.raises(TypeError):
        te.font = "not_a_font"


def test_set_font_path_error(tmp_path):
    te = TextElement(text="Test", start=timedelta(), end=timedelta())
    # Provide invalid path
    with pytest.raises(OSError):
        te.set_font("nonexistent.ttf", 12)


# def test_set_font_size_without_font():
#     te = TextElement(text="X", start=timedelta(), end=timedelta())
#     # Remove font attribute
#     del te._font
#     with pytest.raises(ValueError):
#         te.set_font_size(20)


# def test_set_font_path_without_font():
#     te = TextElement(text="Y", start=timedelta(), end=timedelta())
#     del te._font
#     with pytest.raises(ValueError):
#         te.set_font_path("arial.ttf")


# def test_draw_without_setup():
#     te = TextElement(text=None, position=None, start=timedelta(), end=timedelta())
#     image = Image.new('RGB', (100,100))
#     with pytest.raises(ValueError):
#         te.draw(image)


def test_draw_success(tmp_path):
    te = TextElement(text="Hi", position=(10,10), start=timedelta(), end=timedelta())
    image = Image.new('RGB', (200,200), 'white')
    # Should not raise
    te.draw(image)
    # Check pixel change near position
    px = image.getpixel((10,10))
    assert px != (255,255,255)
