import cv2
import numpy as np
import moviepy as mp
from moviepy import ImageSequenceClip
from scipy.signal import convolve2d

def apply_motion_blur(image, kernel_size=5):
    """Applies motion blur to an image."""
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = 1
    kernel = kernel / kernel_size
    blurred = cv2.filter2D(image, -1, kernel)
    return blurred

def animate_image_scrolling_moviepy_motion_blur(image_path, timeline_points, output_path="animated_scroll_moviepy_blur.mp4", fps=30, visible_width=800, visible_height=600, blur_kernel_size=5):
    """
    Animates scrolling through a large image using MoviePy with motion blur.

    Args:
        image_path (str): Path to the input image.
        timeline_points (list): A list of tuples, where each tuple represents a timeline point.
                               Each tuple should contain (x_start, y_start, duration_seconds).
                               x_start and y_start are the top-left coordinates of the visible region.
                               duration_seconds is the time in seconds to use for the transition to that point.
        output_path (str, optional): Path to save the output video. Defaults to "animated_scroll_moviepy_blur.mp4".
        fps (int, optional): Frames per second of the animation. Defaults to 30.
        visible_width (int, optional): The width of the visible region. Defaults to 800.
        visible_height (int, optional): The height of the visible region. Defaults to 600.
        blur_kernel_size(int, optional): Kernel size for motion blur. Defaults to 5.
    """

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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
            t = frame_num / fps
            x = int(prev_x + (x_start - prev_x) * (t / duration))
            y = int(prev_y + (y_start - prev_y) * (t / duration))

            x = max(0, min(x, width - visible_width))
            y = max(0, min(y, height - visible_height))

            visible_region = img_rgb[y:y + visible_height, x:x + visible_width]

            # Apply motion blur (only during movement)
            if duration > 0: #Do not blur still frames.
              visible_region = apply_motion_blur(visible_region, blur_kernel_size)

            frames.append(visible_region)

    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, fps=fps)

# Example usage:
image_path = "test/lyric_image.png"
timeline_points = [
    (100, 100, 2),
    (500, 200, 1),
    (800, 600, 1.5),
    (800, 600, 3),
    (200, 900, 2),
    (0,0, 1)
]

animate_image_scrolling_moviepy_motion_blur(image_path, timeline_points, blur_kernel_size=10, visible_height=1080, visible_width=1920) #Increased blur for effect.