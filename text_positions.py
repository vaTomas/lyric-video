import os
import re
import srt
import math
import random
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from subtitle import get_subtitles as get_subtitles
from video_movie import animate_image_scrolling_moviepy as make_video


def get_optimal_text_positions(
                                texts,
                                width=1920,
                                height=1080,
                                font_path="arial.ttf",
                                font_size=30,
                                text_align="center",
                                text_padding = 30,
                                max_attempts = 10,
                            ):
    """
    Creates an image with lyrics from an SRT file laid out in random locations, supporting italics.

    Args:
        srt_file_path (str): Path to the SRT file.
        output_image_path (str): Path to save the output image.
        width (int): Width of the output image.
        height (int): Height of the output image.
        font_path (str): Path to the regular font file.
        font_size (int): Size of the text.
        italic_font_path (str): Path to the italic font file.
    """  
    dummy_image = Image.new("RGB", (0, 0))
    draw = ImageDraw.Draw(dummy_image)
    
    font = ImageFont.truetype(font_path, font_size)

    drawn_boxes = []

    for text in texts:
        
        if not drawn_boxes:
            x = random.randint(0, width)
            y = random.randint(0, height)
        else:
            x, y = get_middle_point(drawn_boxes[-1])

        left, top, right, bottom = draw.textbbox((x, y), text, font=font, anchor='mm', align=text_align)
        new_box = (left - text_padding, top - text_padding, right + text_padding, bottom + text_padding)
        
        new_box = find_spot(new_box, drawn_boxes, width, height, max_attempts)
        if new_box:
            drawn_boxes.append(new_box)
        else:
            print(f"Warning: Could not place text '{text}' without overlap.")

    return drawn_boxes


def is_box_overlapping(box1, box2):
    """Checks if two bounding boxes overlap."""
    x1_left, y1_top, x1_right, y1_bottom = box1
    x2_left, y2_top, x2_right, y2_bottom = box2

    return not (x1_right < x2_left or x1_left > x2_right or y1_bottom < y2_top or y1_top > y2_bottom)


def is_box_out_of_bounds(box, width, height):
    """
    Checks if a bounding box is out of bounds of a given width and height.

    Args:
        box (tuple): A tuple (left, top, right, bottom) representing the bounding box.
        width (int): The width of the image or area.
        height (int): The height of the image or area.

    Returns:
        bool: True if the box is out of bounds, False otherwise.
    """

    left, top, right, bottom = box

    if left < 0 or top < 0 or right > width or bottom > height:
        return True  # Box is out of bounds
    else:
        return False  # Box is within bounds
    

def get_middle_point(box: Tuple[int, int]) -> Tuple[int, int]:
    """
    Calculates the middle point of a box defined by its corner coordinates.

    Args:
        box (List[Tuple[int, int]]): A list of tuples, where each tuple represents a corner coordinate (x, y).
                                     The box should be defined by at least two opposite corners.

    Returns:
        Tuple[float, float]: The middle point of the box as (x, y).

    Raises:
        ValueError: If the box does not have at least two corners.
    """
    if len(box) < 2:
        raise ValueError("Box must have at least two corners.")

    # Assuming the box is defined by two opposite corners
    left, top, right, bottom = box
    return (left + right) // 2, (top + bottom) // 2


def find_spot(
    bounding_box: Tuple[int, int, int, int],
    existing_boxes: List[Tuple[int, int, int, int]],
    width: int,
    height: int,
    max_attempts: int = 1000
) -> Optional[Tuple[int, int, int, int]]:
    """
    Finds the nearest available spot for a box, avoiding overlaps and out-of-bounds,
    using any direction.

    Args:
        bounding_box (tuple): The box to place (left, top, right, bottom).
        existing_boxes (list): List of already placed boxes.
        width (int): Image width.
        height (int): Image height.
        max_attempts (int): Maximum attempts to find a spot.

    Returns:
        tuple: The adjusted box, or None if no spot is found.
    """
    furthest_distance = math.sqrt(width**2 + height**2)
    distance_increment = furthest_distance / max_attempts

    for attempt_number in range(max_attempts):
        angle = random.uniform(0, 2 * math.pi)
        distance = attempt_number * distance_increment
        dx = int(distance * math.cos(angle))
        dy = int(distance * math.sin(angle))

        left, top, right, bottom = bounding_box
        new_left = left + dx
        new_top = top + dy
        new_right = right + dx
        new_bottom = bottom + dy

        new_box = (new_left, new_top, new_right, new_bottom)

        if is_box_out_of_bounds(new_box, width, height):
            continue

        overlap = False
        for drawn_box in existing_boxes:
            if is_box_overlapping(new_box, drawn_box):
                overlap = True
                break

        if not overlap:
            return new_box

    return None


def make_image(
    texts,
    output_image_path,
    width=1920,
    height=1080,
    font_path="arial.ttf",
    font_size=30,
    text_align="center",
    text_padding = 30,
    max_attempts = 10,
):
    font = ImageFont.truetype(font_path, font_size)

    image = Image.new("RGB", (width, height), "White")
    draw = ImageDraw.Draw(image)

    text_boxes_positions = get_optimal_text_positions(
        texts = texts,
        width = width,
        height = width,
        font_size = font_size,
        text_padding = text_padding,
        max_attempts = max_attempts
    )

    text_positions = []
    for text_box in text_boxes_positions:
        pos = get_middle_point(text_box)
        text_positions.append(pos)

    for i in range(len(texts)):
        text = texts[i]
        pos = text_positions[i]
        # draw.rectangle(bounding_box, outline="black")
        draw.text(pos, text, font=font, fill="black", anchor="mm", align=text_align)

    try:
        image.save(output_image_path)
        print(f"Lyric image saved to {output_image_path}")
    except Exception as e:
        print(f"An error occurred saving the image: {e}")

    points = []
    for pos in text_positions:
        x, y = pos
        points.append((x + (width // 2), y + (height // 2), 3))
    make_video(output_image_path, points, visible_width=1920, visible_height=1080, fps=15)
    

def main():
    # Example usage:
    srt_file = "test/subtitle.srt"  # Replace with your SRT file path.
    output_image = "test/lyric_image.png"
    size = 9000
    file_text = get_subtitles(srt_file)
    texts = list()
    for text in file_text:
        texts.append(text.content)

    make_image(texts,
                                output_image,
                                width = size,
                                height = size,
                                font_size = 80,
                                text_padding= 300,
                                max_attempts= 1000,
                            )
        
    

if __name__ == "__main__":
    main()