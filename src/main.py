import subprocess
import random
import os
from PIL import Image, ImageDraw, ImageFont

def create_lyric_video(audio_file, lyrics, images, output_video, duration=30, image_count=10, image_size=(100, 100), font_path="arial.ttf", font_size=30):
    """
    Creates a music lyric video with randomly scattered images and text lyrics on a plane.

    Args:
        audio_file (str): Path to the audio file.
        lyrics (list): List of lyric strings.
        images (list): List of paths to image files.
        output_video (str): Path to the output video file.
        duration (int): Duration of the video in seconds.
        image_count (int): Number of images to scatter on the plane.
        image_size (tuple): Size of the images (width, height).
        font_path (str): Path to the font file.
        font_size (int): Size of the text.
    """

    # 1. Generate the static background image (the "plane")
    width = 1920  # Adjust as needed
    height = 1080 # Adjust as needed
    background = Image.new("RGB", (width, height), "white") # White background. Adjust as needed.

    # 2. Scatter the images on the background
    for _ in range(image_count):
        img_path = random.choice(images)
        try:
            img = Image.open(img_path).resize(image_size)
        except FileNotFoundError:
            print(f"Warning: Image file not found: {img_path}")
            continue

        x = random.randint(0, width - image_size[0])
        y = random.randint(0, height - image_size[1])

        if img.mode == "RGBA": #check if image has an alpha channel.
            background.paste(img, (x, y), img) # Use mask to handle transparency
        else:
            background.paste(img, (x,y)) # paste without mask if no alpha channel.

    background.save("background.png")

    # 3. Generate lyric images
    lyric_images = []
    font = ImageFont.truetype(font_path, font_size)

    for i, lyric in enumerate(lyrics):
        lyric_img = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Transparent background
        draw = ImageDraw.Draw(lyric_img)

        # Use textbbox() to get text size
        left, top, right, bottom = draw.textbbox((0, 0), lyric, font=font)
        text_width = right - left
        text_height = bottom - top

        x = random.randint(0, width - text_width)
        y = random.randint(0, height - text_height)
        draw.text((x, y), lyric, font=font, fill="black")  # Black text. Adjust as needed.
        lyric_img.save(f"lyric_{i}.png")
        lyric_images.append(f"lyric_{i}.png")

    # 4. Generate the FFMPEG commands
    ffmpeg_commands = [
        "ffmpeg",
        "-loop", "1", "-i", "background.png",  # Static background
    ]

    # Add lyric image inputs and filters
    for i, lyric_img in enumerate(lyric_images):
        ffmpeg_commands.extend(["-i", lyric_img])
        ffmpeg_commands.extend([
            "-filter_complex",
            f"[0:v][{i+1}:v]overlay=enable='between(t,{i*duration/len(lyrics)},{(i+1)*duration/len(lyrics)})'",
        ])

    ffmpeg_commands.extend([
        "-i", audio_file,  # Audio input
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        output_video,
    ])

    # 5. Execute FFMPEG
    try:
        subprocess.run(ffmpeg_commands, check=True)
        print(f"Video created successfully: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
    finally:
        #cleanup lyric images
        for lyric_image in lyric_images:
            os.remove(lyric_image)
        os.remove("background.png")

# Example usage
audio_file = "audio.mp3"  # Replace with your audio file
lyrics = ["Verse 1", "Line 1", "Line 2", "Chorus", "Verse 2", "Line 1", "Line 2", "Outro"]  # Your lyrics
images = ["image1.jpg", "image2.jpg", "image3.jpg"]  # Replace with your image paths
output_video = "lyric_video.mp4"

create_lyric_video(audio_file, lyrics, images, output_video)