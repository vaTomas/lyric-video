import cv2
import numpy as np
from moviepy import AudioFileClip, VideoClip
from scipy.interpolate import PchipInterpolator


def make_warp_affine_clip(
    big_image: np.ndarray,
    keyframes: list,
    resolution: tuple[int, int],
    framerate: float,
    audio_path: str = None,
):
    """
    Returns a MoviePy VideoClip that pans/zooms/rotates around `big_image`
    according to `keyframes`, using cv2.warpAffine for subpixel transforms.
    """
    # Unpack keyframe times and params
    times = np.array([kf[0] for kf in keyframes], dtype=float)  # in seconds
    centers = np.array([kf[1] for kf in keyframes], dtype=float)  # [[x,y],...]
    rots = np.array([kf[2] for kf in keyframes], dtype=float)  # degrees
    zooms = np.array([kf[3] for kf in keyframes], dtype=float)

    # Build smooth, monotonic interpolators
    fx = PchipInterpolator(times, centers[:, 0])
    fy = PchipInterpolator(times, centers[:, 1])
    frot = PchipInterpolator(times, rots)
    fzoom = PchipInterpolator(times, zooms)

    w, h = resolution
    duration = times[-1]

    def make_frame(t):
        # 1) sample parameters at time t
        cx, cy = float(fx(t)), float(fy(t))
        angle = float(frot(t))  # in degrees
        zoom = float(fzoom(t))  # zoom >1 == “zoom in”

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
