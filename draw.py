import os
import re
import srt
import random
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from subtitle import get_subtitles as get_subtitles

def create_lyric_image_from_srt(srt_file_path,
                                output_image_path,
                                width=1920,
                                height=1080,
                                font_path="arial.ttf",
                                font_size=30,
                                italic_font_path="ariali.ttf",
                                text_align="lm"):
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

    subtitles = get_subtitles(srt_file_path)

    background = Image.new("RGB", (width, height), "white")  # White background. Adjust as needed.
    draw = ImageDraw.Draw(background)
    
    regular_font = ImageFont.truetype(font_path, font_size)
    italic_font = ImageFont.truetype(italic_font_path, font_size)

    for subtitle in subtitles:
        lyric = subtitle.content
        # lyric = subtitle.content.replace('\n', ' ') #remove newlines


        x = 0 #random.randint(0, width - 200) #start x position
        y = 0 #random.randint(0, height - 50) #start y position.

        draw.text((x, y), lyric, font=italic_font, fill="black", anchor=text_align)
        left, top, right, bottom = draw.textbbox((x,y), lyric, font=italic_font)

    try:
        background.save(output_image_path)
        print(f"Lyric image saved to {output_image_path}")
    except Exception as e:
        print(f"An error occurred saving the image: {e}")


def main():
    # Example usage:
    srt_file = "test/lyrics/video.srt"  # Replace with your SRT file path.
    output_image = "test/lyric_image.png"
    create_lyric_image_from_srt(srt_file,
                                output_image,
                                width = 10000,
                                height = 10000,
                                font_size = 100
                                )

if __name__ == "__main__":
    main()