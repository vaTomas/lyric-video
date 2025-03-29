import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def animate_image_scrolling(image_path, timeline_points, output_path="animated_scroll.gif", fps=10):
    """
    Animates scrolling through a large image based on specified timeline points.

    Args:
        image_path (str): Path to the input image.
        timeline_points (list): A list of tuples, where each tuple represents a timeline point.
                               Each tuple should contain (x_start, y_start, frame_count).
                               x_start and y_start are the top-left coordinates of the visible region.
                               frame_count is the number of frames to use for the transition to that point.
        output_path (str, optional): Path to save the animated GIF. Defaults to "animated_scroll.gif".
        fps (int, optional): Frames per second of the animation. Defaults to 10.
    """

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB for matplotlib

    fig, ax = plt.subplots()
    im = ax.imshow(img_rgb[0:100, 0:100]) #Initial small display so matplotlib doesn't complain about empty data.

    def update(frame_num):
        """Updates the frame based on the timeline."""
        current_point_index = 0
        total_frames = 0

        for i, point in enumerate(timeline_points):
            total_frames += point[2]
            if frame_num < total_frames:
                current_point_index = i
                break

        x_start, y_start, frame_count = timeline_points[current_point_index]

        if current_point_index == 0:
            prev_x, prev_y = 0, 0 #For the first point, start from (0,0)
        else:
            prev_x, prev_y, prev_frames = timeline_points[current_point_index-1]
            total_prev_frames = 0
            for j in range(current_point_index):
                total_prev_frames += timeline_points[j][2]
            prev_frame_num = frame_num - total_prev_frames
            
            if prev_frame_num > timeline_points[current_point_index][2]:
                prev_frame_num = timeline_points[current_point_index][2]

        if frame_count == 0: #If no movement is required for a point, just show the point.
            x = x_start
            y = y_start
        else:
            x = int(prev_x + (x_start - prev_x) * (prev_frame_num / frame_count))
            y = int(prev_y + (y_start - prev_y) * (prev_frame_num / frame_count))

        # Ensure the visible region stays within the image bounds
        height, width, _ = img_rgb.shape
        visible_width = min(width - x, width)
        visible_height = min(height - y, height)

        visible_region = img_rgb[y:y + visible_height, x:x + visible_width]
        im.set_array(visible_region)
        return im,

    ani = animation.FuncAnimation(fig, update, frames=sum(point[2] for point in timeline_points), interval=1000/fps, blit=True)
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close() #Prevent showing the last frame as a static plot.

# Example usage:
image_path = "output.png"  # Replace with your image path
timeline_points = [
    (100, 100, 50),   # Show region starting at (100, 100) for 50 frames.
    (500, 200, 30),   # Move to (500, 200) over 30 frames.
    (800, 600, 40),   # Move to (800, 600) over 40 frames.
    (200, 900, 60),   # Move to (200, 900) over 60 frames.
    (0,0,20) #Return to the start.
]

animate_image_scrolling(image_path, timeline_points)