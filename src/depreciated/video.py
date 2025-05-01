import os
import srt
import random
import subprocess
from typing import List, Tuple, Optional
from subtitle.subtitle import get_subtitles as get_subtitles
from audio import extract_audio as extract_audio


def generate_ffmpeg_commands(
    srt_file_path: str,
    image_path: str,
    audio_path: str,
    output_video_path: str,
    image_width: int,
    image_height: int,
    move_speed: int = 50,  # Pixels per second
) -> None:
    """Generates and executes FFmpeg commands to move an image based on SRT timings."""

    subtitles = get_subtitles(srt_file_path)

    commands = []
    # prev_end = 0.0

    # for subtitle in subtitles:
    #     start_time = subtitle.start.total_seconds()
    #     end_time = subtitle.end.total_seconds()
    #     text = subtitle.content

    #     # Calculate movement based on time and speed
    #     dx = random.randint(-move_speed, move_speed) #random movement
    #     dy = random.randint(-move_speed, move_speed)

    #     # Generate FFmpeg commands
    #     commands.extend([
    #         "-loop", "1",
    #         "-i", image_path,
    #         "-t", str(end_time - prev_end),
    #         "-vf", f"scale={image_width}:{image_height}, "
    #                f"\"[v]drawtext=text='{text}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2[txt];"
    #                f"[txt]translate=x='{dx}*t':y='{dy}*t'\"",
    #         "-c:v", "libx264",
    #         "-pix_fmt", "yuv420p",
    #         "-y",  # Overwrite output file
    #     ])

    #     prev_end = end_time

    commands.extend([
    "-loop", "1",
    "-i", image_path,
    "-i", audio_path,
    "-map", "0:v",
    "-map", "1:a",
    "-c:v", "libx264",
    "-c:a", "aac",
    # "-b:a", "-b:a 192k"
    "-shortest",
    # "-t", "5",
    "-vf", f"scale=1920:1080",
    "-y"
    ])

    # Combine commands and execute FFmpeg
    final_command = ["ffmpeg"] + commands + [output_video_path]

    try:
        process = subprocess.Popen(
            final_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stdout and stderr
            text=True,  # Decode output as text
            bufsize=1, # Line-buffered output
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output, end='')  # Print output to console

        return_code = process.poll()
        if return_code == 0:
            print(f"\nVideo generated successfully: {output_video_path}")
        else:
            print(f"\nFFmpeg exited with error code: {return_code}")

    except FileNotFoundError:
        print("Error: FFmpeg not found. Make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    

def main():
    srt_file_path = "test/subtitle.srt"  # Replace with your SRT file
    image_path = "test/image.jpg"  # Replace with your image file
    audio_path = "test/video.mp4"
    output_video_path = "test/output.mp4"
    image_width = 100
    image_height = 100


    audio_path = extract_audio(audio_path, True)

    try:
        generate_ffmpeg_commands(srt_file_path, image_path, audio_path, output_video_path, image_width, image_height)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()