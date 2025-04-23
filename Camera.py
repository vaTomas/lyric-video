import cv2
import json
import time
import datetime
import numpy as np
from Scene import Scene
from Element import Element
from typing import List, Optional, Tuple
from scipy.interpolate import PchipInterpolator
from moviepy import ImageSequenceClip, AudioFileClip, VideoClip, CompositeAudioClip, ImageClip
from moviepy.video.fx import Crop


def interpolate_keyframes_cubic(
    keyframes: List[Tuple[float, float]],
    query_times: Optional[np.ndarray] = None,
    num_query: Optional[int] = None,
) -> List[Tuple[float, float]]:
    # sort
    keyframes = sorted(keyframes, key=lambda tp: tp[0])
    times = np.array([t for t, _ in keyframes], dtype=float)
    positions = np.array([p for _, p in keyframes], dtype=float)

    # build a *monotonic* piecewise-cubic interpolator
    pchip = PchipInterpolator(times, positions)  # :contentReference[oaicite:0]{index=0}

    # query times
    if query_times is not None:
        qt = np.asarray(query_times, dtype=float)
    elif num_query is not None:
        qt = np.linspace(times[0], times[-1], num_query)
    else:
        raise ValueError("Either `query_times` or `num_query` must be provided")

    # evaluate and pack
    interp_positions = pchip(qt)
    return list(zip(qt.tolist(), interp_positions.tolist()))


def interpolate_keyframes_linear(
    keyframes: List[Tuple[float, float]],
    query_times: Optional[np.ndarray] = None,
    num_query: Optional[int] = None,
) -> List[Tuple[float, float]]:
    """
    Given a list of (time_ms, position) pairs, perform piecewise *linear*
    interpolation and return a list of (time, interpolated_position).

    You must supply *either*:
      - `query_times`: a 1D array of times (in ms) at which to interpolate, OR
      - `num_query`: an integer count of equally‐spaced samples from first to last time.
    """
    # 1) Sort input by time
    keyframes = sorted(keyframes, key=lambda tp: tp[0])
    times = np.array([t for t, _ in keyframes], dtype=float)
    positions = np.array([p for _, p in keyframes], dtype=float)

    # 2) Determine the times at which we'll sample
    if query_times is not None:
        qt = np.asarray(query_times, dtype=float)
    elif num_query is not None:
        qt = np.linspace(times[0], times[-1], num_query, dtype=float)
    else:
        raise ValueError("Either `query_times` or `num_query` must be provided")

    # 3) Do the linear interpolation
    #    np.interp will:
    #      - For qt within [times[0], times[-1]] interpolate linearly
    #      - For qt < times[0] or qt > times[-1], return positions[0] or positions[-1]
    interp_positions = np.interp(qt, times, positions)

    # 4) Return paired list
    return list(zip(qt.tolist(), interp_positions.tolist()))


def get_frame(image, viewbox, target_size=None):
    """
    Crop out `viewbox` from `image`, then pad/crop the result to `target_size`
    (height, width). If target_size is None, it just returns the raw crop.
    """
    # Round to ints
    left, top, right, bottom = [int(round(c)) for c in viewbox]
    frame = image[top:bottom, left:right]

    if target_size is not None:
        th, tw = target_size
        fh, fw = frame.shape[:2]
        if (fh, fw) != (th, tw):
            # create a black canvas of exactly target_size
            channels = frame.shape[2] if frame.ndim == 3 else 1
            shape = (th, tw, channels) if channels > 1 else (th, tw)
            new = np.zeros(shape, dtype=frame.dtype)
            # copy in as much as will fit
            new[: min(th, fh), : min(tw, fw)] = frame[: min(th, fh), : min(tw, fw)]
            frame = new

    return frame


def frame_to_ms(frame, framerate):
    return frame / framerate * 1000


def make_frame_factory(big_image, interpolated_keyframes, box, target_size, framerate):
    """
    Returns a function f(t) that returns the RGB frame at time t (in seconds).
    """
    times_ms = [kf[0] for kf in interpolated_keyframes]
    # Precompute the mapping from frame index → viewbox
    viewboxes = [
        box.calculate_absolute_box(tuple(kf[1]), box.object_box)
        for kf in interpolated_keyframes
    ]

    def make_frame(t):
        # convert time (seconds) → frame index
        frame_idx = min(int(round(t * framerate)), len(viewboxes) - 1)

        # crop & pad to target_size
        vb = viewboxes[frame_idx]
        l, top, r, b = [int(round(c)) for c in vb]
        crop = big_image[top:b, l:r]

        # pad if needed
        th, tw = target_size
        fh, fw = crop.shape[:2]
        if (fh, fw) != (th, tw):
            padded = np.zeros((th, tw, 3), dtype=crop.dtype)
            padded[:fh, :fw] = crop
            crop = padded

        # BGR→RGB for MoviePy
        return cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

    return make_frame

def make_frame_factory_warpAffine(big_image, interpolated_keyframes, box, target_size, framerate):
    """
    Returns a function f(t) that returns the RGB frame at time t (in seconds),
    using cv2.warpAffine for smooth, subpixel translation.
    """
    # Precompute the viewboxes (as floats)
    viewboxes = [
        box.calculate_absolute_box(tuple(kf[1]), box.object_box)
        for kf in interpolated_keyframes
    ]
    duration = interpolated_keyframes[-1][0] / 1000.0
    th, tw = target_size

    def make_frame(t):
        # frame index from time
        idx = min(int(round(t * framerate)), len(viewboxes) - 1)
        left, top, right, bottom = viewboxes[idx]

        # build affine matrix to translate (left,top) → (0,0)
        M = np.array([[1, 0, -left],
                      [0, 1, -top]], dtype=np.float32)

        # warp the entire big_image into a (tw × th) window
        out = cv2.warpAffine(
            big_image, M, (tw, th),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT
        )
        # BGR→RGB
        return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

    return make_frame



def make_frame_factory_remap(big_image, interpolated_keyframes, box, target_size, framerate):
    """
    Returns a function f(t) that returns the RGB frame at time t (in seconds),
    using cv2.remap for arbitrary subpixel crops.
    """
    viewboxes = [
        box.calculate_absolute_box(tuple(kf[1]), box.object_box)
        for kf in interpolated_keyframes
    ]
    duration = interpolated_keyframes[-1][0] / 1000.0
    th, tw = target_size

    # Precompute base mapping grids
    xs, ys = np.meshgrid(
        np.arange(tw, dtype=np.float32),
        np.arange(th, dtype=np.float32)
    )

    def make_frame(t):
        idx = min(int(round(t * framerate)), len(viewboxes) - 1)
        left, top, right, bottom = viewboxes[idx]

        # shift the base grid by the viewbox offset
        map_x = xs + left
        map_y = ys + top

        # remap (bilinear) into a tw×th frame
        out = cv2.remap(
            big_image, map_x, map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT
        )
        return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

    return make_frame

def main():
    datetime_now = datetime.datetime.now()
    datetime_now = datetime_now.strftime("%Y_%m_%d_%H%M%S")
    image_path = "test/2025_04_20_003315_run_output.png"
    json_path = "test/2025_04_20_003315_run_output.json"
    output_path = f"test/{datetime_now}_run_output.mp4"
    audio_path = "test/video_audio_extracted.mka"
    target_size = (1080, 1920)  # height, width
    box = Element(
        object_box=(
            -target_size[1] / 2,
            -target_size[0] / 2,
            target_size[1] / 2,
            target_size[0] / 2,
        )
    )
    duration = (3 * 60 + 31) * 1000  # milliseconds
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
                (text_element["end"] + text_element["start"]) / 2,
                text_element["position"],
            )
        )

    keyframes.append((0, scene_text.elements[0]["position"]))
    keyframes.append((duration, scene_text.elements[-1]["position"]))

    keyframes = sorted(keyframes, key=lambda tp: tp[0])

    timeframes = np.linspace(0, duration, round((duration / 1000) * framerate))

    interpolated_keyframes = interpolate_keyframes_cubic(
        keyframes=keyframes, query_times=timeframes
    )

    # x_keyframes = []
    # y_keyframes = []
    # for keyframe in keyframes:
    #     x_keyframes.append((keyframe[0], keyframe[1][0]))
    #     y_keyframes.append((keyframe[0], keyframe[1][1]))

    # x_interpolated_keyframes = interpolate_keyframes_linear(
    #     keyframes=x_keyframes, query_times=timeframes
    # )
    # y_interpolated_keyframes = interpolate_keyframes_linear(
    #     keyframes=y_keyframes, query_times=timeframes
    # )

    # interpolated_keyframes = []
    # for i in range(len(x_interpolated_keyframes)):
    #     interpolated_keyframes.append(
    #         (
    #             x_interpolated_keyframes[i][0],
    #             (x_interpolated_keyframes[i][1], y_interpolated_keyframes[i][1]),
    #         )
    #     )

    big_image = cv2.imread(image_path)

    # frames = []
    # for keyframe in interpolated_keyframes:
    #     vb = box.calculate_absolute_box(tuple(keyframe[1]), box.object_box)
    #     if target_size is None:
    #         # determine target size from the first viewbox
    #         l, t, r, b = [int(round(c)) for c in vb]
    #         target_size = (b - t, r - l)

    #     frame = get_frame(big_image, vb, target_size)

    #     frame = cv2.cvtColor(
    #         frame, cv2.COLOR_BGR2RGB
    #     )  # Channel conversion for ImageSequenceClip

    #     frames.append(frame)

    make_frame = make_frame_factory(
        big_image, interpolated_keyframes, box, target_size, framerate
    )

    video_clip = VideoClip(make_frame, duration=duration / 1000)
    
    audio_clip = AudioFileClip(audio_path)

    new_audioclip = CompositeAudioClip([audio_clip])
    video_clip.audio = new_audioclip
    video_clip.write_videofile(output_path, fps=framerate)

if __name__ == "__main__":
    main()
