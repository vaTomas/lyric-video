import cv2
import numpy as np
import moviepy as mp
from moviepy import ImageSequenceClip

def animate_image_scrolling_moviepy(image_path, timeline_points, output_path="animated_scroll_moviepy.mp4", fps=30, visible_width=800, visible_height=600):
    """
    Animates scrolling through a large image using MoviePy based on specified timeline points.

    Args:
        image_path (str): Path to the input image.
        timeline_points (list): A list of tuples, where each tuple represents a timeline point.
                               Each tuple should contain (x_start, y_start, duration_seconds).
                               x_start and y_start are the top-left coordinates of the visible region.
                               duration_seconds is the time in seconds to use for the transition to that point.
        output_path (str, optional): Path to save the output video. Defaults to "animated_scroll_moviepy.mp4".
        fps (int, optional): Frames per second of the animation. Defaults to 30.
        visible_width (int, optional): The width of the visible region. Defaults to 800.
        visible_height (int, optional): The height of the visible region. Defaults to 600.
    """

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB for moviepy.

    height, width, _ = img_rgb.shape
    frames = []
    total_duration = 0

    for i, (x_start, y_start, duration) in enumerate(timeline_points):
        total_duration += duration
        num_frames = int(duration * fps)

        if i == 0:
            prev_x, prev_y = 0, 0
        else:
            prev_x, prev_y, _ = timeline_points[i - 1]

        for frame_num in range(num_frames):
            t = frame_num / fps  # Time within the current transition
            x = int(prev_x + (x_start - prev_x) * (t / duration))
            y = int(prev_y + (y_start - prev_y) * (t / duration))

            # Ensure the visible region is within the image bounds
            x = max(0, min(x, width - visible_width))
            y = max(0, min(y, height - visible_height))

            visible_region = img_rgb[y:y + visible_height, x:x + visible_width]
            frames.append(visible_region)

    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, fps=fps)

def main():
    # Example usage:
    image_path = "test/lyric_image.png"  # Replace with your image path
    timeline_points = [
        (100, 100, 2),  # Show region starting at (100, 100) for 2 seconds.
        (500, 200, 1),  # Move to (500, 200) over 1 second.
        (800, 600, 1.5), # Move to (800, 600) over 1.5 seconds.
        (200, 900, 2),  # Move to (200, 900) over 2 seconds.
        (0,0, 1) #Return to start.
    ]

    animate_image_scrolling_moviepy(image_path, timeline_points, visible_width=1920, visible_height=1080, fps=60)


if __name__ == "__main__":
    main()