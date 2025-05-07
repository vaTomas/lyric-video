import cv2
import numpy as np
from moviepy import AudioFileClip, VideoClip
from scipy.interpolate import PchipInterpolator
from .camera import Camera

def render(
    big_image: np.ndarray,
    camera: Camera,
    framerate: float,
    audio_path: str = None,
):
    """
    Returns a MoviePy VideoClip that pans/zooms/rotates around `big_image`
    according to `keyframes`, using cv2.warpAffine for subpixel transforms.
    """
    # Unpack keyframe times and params

    # Build smooth, monotonic interpolators

    w, h = camera.resolution
    duration = camera.position_keyframes[-1].time

    def make_frame(t):
        # 1) sample parameters at time t
        cx, cy = camera.get_position(t)
        angle = camera.get_angle(t)  # in degrees
        zoom = camera.get_zoom(t)  # zoom >1 == “zoom in”

        # 2) build affine matrix via getRotationMatrix2D
        # start with a rotation+scale about the CENTER of the output image:
        M = cv2.getRotationMatrix2D((-cx, -cy), angle, zoom)

        # then shift so that that center-of‐frame point in the source
        # (which currently maps to (w/2,h/2) after R+S) moves to (cx,cy):
        M[0, 2] += cx - (w / 2)
        M[0, 2] = -M[0, 2]

        M[1, 2] += cy - (h / 2)
        M[1, 2] = -M[1, 2]

        # 3) warp
        out = cv2.warpAffine(
            big_image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
        )

        # 4) BGR→RGB for MoviePy
        return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.with_fps(framerate)

    if audio_path:
        audio = AudioFileClip(audio_path).with_duration(duration)
        clip = clip.with_audio(audio)

    return clip
