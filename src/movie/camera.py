import numpy as np
from .keyframe import Keyframe
from typing import Tuple, Union, Optional, Callable
from scipy.interpolate import PchipInterpolator
from collection_validator import validate_collection


class Camera:
    def __init__(self, resolution: tuple[int, int]):
        self.resolution = resolution

        self._position_keyframes = []
        self._zoom_keyframes = []
        self._rotation_keyframes = []

    @property
    def resolution(self) -> Tuple[int, int]:
        """
        Returns a tuple representation of the camera resolution (Width, Height)
        """
        return self._resolution

    @resolution.setter
    def resolution(self, r: Tuple[int, int]) -> None:
        """
        (Width, Height)
        """
        validate_collection(
            value=r,
            collection_type=tuple,
            element_count=2,
            element_types=int,
        )

        for dim in r:
            if dim < 0:
                raise ValueError("Resolution must be a positive intiger.")

        self._resolution = r

    @property
    def position_keyframes(self):
        return self._position_keyframes

    # @position_keyframes.setter
    # def position_keyframes(self, keyframes):
    #     if keyframes is None:
    #         self._position_keyframes = []
    #         return

    #     for keyframe in keyframes:
    #         if not isinstance(keyframe, Keyframe):
    #             raise TypeError

    #         if not len(keyframe.position) == 2:
    #             raise ValueError

    #         if not isinstance(keyframe.time, (int, float)):
    #             raise TypeError

    #     self._position_keyframes = keyframes

    def add_position_keyframe(
        self,
        time: Union[int, float],
        position: Tuple[Union[float, int], Union[float, int]],
        sort_keyframes: bool = True,
    ) -> Keyframe:
        """
        Time in seconds.
        Position in x,y.
        """
        return self._add_keyframe(
            self._position_keyframes,
            time,
            position,
            element_types=(int, float),
            sort_keyframes=sort_keyframes,
            normalizer=lambda pos: (float(pos[0]), float(pos[1])),
        )

    @property
    def rotation_keyframes(self):
        return self._rotation_keyframes

    def add_rotation_keyframe(
        self,
        time: Union[int, float],
        angle: Union[float, int],
        sort_keyframes: bool = True,
    ) -> Keyframe:
        """
        Time in seconds.
        Angle in degrees.
        """
        return self._add_keyframe(
            self._rotation_keyframes,
            time,
            angle,
            element_types=(int, float),
            sort_keyframes=sort_keyframes,
            normalizer=lambda a: float(a) % 360,
        )

    @property
    def zoom_keyframes(self):
        return self._zoom_keyframes

    def add_zoom_keyframe(
        self,
        time: Union[int, float],
        zoom: Union[float, int],
        sort_keyframes: bool = True,
    ) -> Keyframe:
        """
        Time in seconds.
        Zoom in multiplier (1 is to scale, >1 is zoom-in, <1 is zoom-out).
        """
        return self._add_keyframe(
            self._zoom_keyframes,
            time,
            zoom,
            element_types=(int, float),
            sort_keyframes=sort_keyframes,
            normalizer=lambda z: float(z),
        )

    def add_keyframe(
        self,
        time: Union[int, float],
        position: Optional[Tuple[Union[float, int], Union[float, int]]],
        angle: Optional[Union[float, int]],
        zoom: Optional[Union[float, int]],
        sort_keyframes: bool = True,
    ):
        if position is not None:
            self.add_position_keyframe(
                time=time, position=position, sort_keyframes=sort_keyframes
            )

        if angle is not None:
            self.add_rotation_keyframe(
                time=time, angle=angle, sort_keyframes=sort_keyframes
            )

        if zoom is not None:
            self.add_zoom_keyframe(time=time, zoom=zoom, sort_keyframes=sort_keyframes)

    def sort_keyframes(self) -> None:
        self._position_keyframes.sort(key=lambda keyframe: keyframe.time)
        self._zoom_keyframes.sort(key=lambda keyframe: keyframe.time)
        self._rotation_keyframes.sort(key=lambda keyframe: keyframe.time)

    def _add_keyframe(
        self,
        keyframes: list[Keyframe],
        time: Union[int, float],
        value,
        *,
        element_types,
        sort_keyframes: bool = True,
        normalizer=lambda x: x,
    ) -> Keyframe:
        if not isinstance(time, (int, float)):
            raise TypeError("Time must be float or int")

        if isinstance(value, (tuple, list)):
            validate_collection(
                value=tuple(value),
                collection_type=tuple,
                element_count=2,
                element_types=element_types,
            )
        elif not isinstance(value, element_types):
            raise TypeError(
                f"Value must be one of types {element_types}, got {type(value)}"
            )

        value = normalizer(value)

        for keyframe in keyframes:
            if keyframe.time == time:
                keyframe.value = value
                break
        else:
            keyframe = Keyframe(time=time, value=value)
            keyframes.append(keyframe)

        if sort_keyframes:
            keyframes.sort(key=lambda keyframe: keyframe.time)

        return keyframe

    def _make_interpolator(
        self,
        keyframes: list[Keyframe],
        default_output: Union[float, Tuple[float, float]],
        axis: Optional[int] = None,
    ) -> Callable[[float], Union[float, Tuple[float, float]]]:
        """
        Build and return a PchipInterpolator on this keyframe track.

        - keyframes:        list of Keyframe(time:float, value:float or (x,y))
        - default_output:   what to return outside the keyframe range
        - axis:             if the value is vector (x,y), set axis=0 so interp on each component
        """
        if not keyframes:
            return lambda t: default_output

        keyframes.sort(key=lambda keyframe: keyframe.time)
        times = np.array([keyframe.time for keyframe in keyframes], dtype=float)
        values = np.array([keyframe.value for keyframe in keyframes], dtype=float)

        if axis is None:
            interpolator = PchipInterpolator(times, values, extrapolate=True)
        else:
            interpolator = PchipInterpolator(times, values, axis=axis, extrapolate=True)

        def f(t: float):
            t = float(t)
            if t <= times[0]:
                return values[0].tolist() if axis is not None else float(values[0])
            if t >= times[-1]:
                return values[-1].tolist() if axis is not None else float(values[-1])
            v = interpolator(t)
            return tuple(v.tolist()) if axis is not None else float(v)

        return f

    def make_position_interpolator(self) -> None:
        self._position_fn = self._make_interpolator(
            self._position_keyframes,
            default_output=(0.0, 0.0),
            axis=0,
        )

    def get_position(self, t: float) -> Tuple[float, float]:
        if not hasattr(self, "_position_fn"):
            self.make_position_interpolator()
        return self._position_fn(t)

    def make_rotation_interpolator(self) -> None:
        # Build an (x,y) track from your angle keyframes for uniform rotation
        xy_keyframes = []
        for kf in self._rotation_keyframes:
            θ_rad = np.deg2rad(kf.value)
            x = np.cos(θ_rad)
            y = np.sin(θ_rad)
            xy_keyframes.append(Keyframe(time=kf.time, value=(x, y)))

        # Default unit‐vector at 0° is (1,0)
        f_xy = self._make_interpolator(
            keyframes=xy_keyframes, default_output=(1.0, 0.0), axis=0
        )

        def f(t: float) -> float:
            x, y = f_xy(t)
            # atan2(y,x) → radians in [-π,π], convert to [0,360)
            ang = np.rad2deg(np.arctan2(y, x)) % 360
            return float(ang)

        self._angle_fn = f

    def get_angle(self, t: float) -> float:
        if not hasattr(self, "_angle_fn"):
            self.make_rotation_interpolator()
        return self._angle_fn(t)

    def make_zoom_interpolator(self) -> None:
        self._zoom_fn = self._make_interpolator(
            self._zoom_keyframes,
            default_output=1.0,
            axis=None,
        )

    def get_zoom(self, t: float) -> float:
        if not hasattr(self, "_zoom_fn"):
            self.make_zoom_interpolator()
        return self._zoom_fn(t)
