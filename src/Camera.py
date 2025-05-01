import cv2
import json
import random
import datetime
import numpy as np
from typing import Tuple
from Scene import Scene
from elements import Element
from moviepy import AudioFileClip, VideoClip
from scipy.interpolate import PchipInterpolator
from Keyframe import Keyframe


class Camera:
    @property
    def resolution(self) -> Tuple[int, int]:
        return self._resolution
    
    @resolution.setter
    def resolution(self, r: Tuple[int, int]) -> None:
        if not len(r) == 2:
            raise ValueError
        
        for coord in r:    
            if not isinstance(coord, int):
                raise TypeError
            
        self._resolution = r

    @property
    def position_keyframes(self):
        return self._position_keyframes
    
    @position_keyframes.setter
    def position_keyframes(self, keyframes):
        for keyframe in keyframes:
            if not isinstance(keyframe, Keyframe):
                raise TypeError
            
            if not len(keyframe.position) == 2:
                raise ValueError
            
            if not isinstance(keyframe.time, int):
                raise TypeError
            
            



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


def main():
    datetime_now = datetime.datetime.now()
    datetime_now = datetime_now.strftime("%Y_%m_%d_%H%M%S")
    image_path = "test/2025_04_20_003315_run_output.png"
    json_path = "test/2025_04_20_003315_run_output.json"
    output_path = f"test/{datetime_now}_run_output.mp4"
    audio_path = "test/video_audio_extracted.mka"
    target_size = (1080, 1920)  # height, width
    resolution = (1920, 1080)

    duration = 3 * 60 + 31  # seconds
    framerate = 60  # frames per second

    json_data = None
    with open(json_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    # print(json_data)

    scene_text = Scene(**json_data["scene_text"])
    scene_images = Scene(**json_data["scene_images"])

    keyframes = []
    for text_element in scene_text.elements:
        # keyframes.append((text_element["start"], text_element["position"]))
        # keyframes.append((text_element["end"], text_element["position"]))
        keyframes.append(
            (
                (text_element["end"] + text_element["start"]) / 2 / 1000,  # time
                text_element["position"],  # position
                random.uniform(-3, 3),  # rotation deg
                random.uniform(0.88, 1.12),  # zoom mult
            )
        )

    big_image = cv2.imread(image_path)
    image_size = big_image.shape[:2]  # height, width

    keyframes.append(
        (
            0,
            (
                scene_text.elements[0]["position"][0] - resolution[0],
                scene_text.elements[0]["position"][1],
            ),
            0,
            1.2,
        )
    )
    keyframes.append(
        (
            duration,
            scene_text.elements[-1]["position"],
            0,
            max(resolution) / min(image_size),
        )
    )

    keyframes = sorted(keyframes, key=lambda tp: tp[0])
    # keyframes = keyframes[0:4]

    clip = make_warp_affine_clip(
        big_image=big_image,
        keyframes=keyframes,
        resolution=resolution,
        framerate=framerate,
        audio_path=audio_path,
    )

    clip.write_videofile(output_path, fps=framerate)


if __name__ == "__main__":
    main()
