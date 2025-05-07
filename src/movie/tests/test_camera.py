import pytest
import numpy as np
from datetime import timedelta
from movie import Camera, Keyframe
from collection_validator import ValidationError


def test_add_and_overwrite_position_keyframes():
    cam = Camera((640, 480))
    # Add two keyframes
    kf1 = cam.add_position_keyframe(0.0, (0, 0))
    kf2 = cam.add_position_keyframe(2.0, (2, 4))
    assert isinstance(kf1, Keyframe)
    assert isinstance(kf2, Keyframe)
    # List sorted and length 2
    times = [kf.time for kf in cam.position_keyframes]
    assert times == [0.0, 2.0]
    # Overwrite existing
    cam.add_position_keyframe(2.0, (3, 6))
    assert len(cam.position_keyframes) == 2
    # Value updated for time=2
    val = [kf.value for kf in cam.position_keyframes if kf.time == 2.0][0]
    assert val == (3.0, 6.0)


def test_add_rotation_and_zoom_keyframes_and_modulo():
    cam = Camera((100, 100))
    # Rotation mod 360
    kf_rot = cam.add_rotation_keyframe(1.0, 370)
    assert kf_rot.value == pytest.approx(10.0)
    # Zoom
    kf_zoom = cam.add_zoom_keyframe(1.5, 2)
    assert kf_zoom.value == pytest.approx(2.0)
    # Sorted tracks
    rot_times = [kf.time for kf in cam.rotation_keyframes]
    zoom_times = [kf.time for kf in cam.zoom_keyframes]
    assert rot_times == [1.0]
    assert zoom_times == [1.5]


def test_get_interpolators_default_and_interpolation():
    cam = Camera((50, 50))
    # No keyframes -> defaults
    assert cam.get_position(0) == (0.0, 0.0)
    assert cam.get_angle(0) == pytest.approx(0.0)
    assert cam.get_zoom(0) == pytest.approx(1.0)

    # Add linear keyframes
    cam.add_position_keyframe(0.0, (0, 0))
    cam.add_position_keyframe(2.0, (4, 8))
    cam.add_rotation_keyframe(0.0, 0)
    cam.add_rotation_keyframe(2.0, 90)
    cam.add_zoom_keyframe(0.0, 1.0)
    cam.add_zoom_keyframe(2.0, 3.0)

    # Remake interpolators
    cam.make_position_interpolator()
    cam.make_rotation_interpolator()
    cam.make_zoom_interpolator()

    # Midpoint t=1.0 should interpolate to (2,4), rotation ~45, zoom ~2
    pos_mid = cam.get_position(1.0)
    rot_mid = cam.get_angle(1.0)
    zoom_mid = cam.get_zoom(1.0)

    assert pos_mid[0] == pytest.approx(2.0)
    assert pos_mid[1] == pytest.approx(4.0)
    assert rot_mid == pytest.approx(45.0)
    assert zoom_mid == pytest.approx(2.0)


def test_invalid_resolution():
    with pytest.raises(ValueError):
        Camera((640, -480))

    with pytest.raises(ValueError):
        Camera((640,))


def test_invalid_keyframes():
    cam = Camera((10,10))
    with pytest.raises(TypeError):
        cam.add_position_keyframe('a', (0,0))
    with pytest.raises(TypeError):
        cam.add_rotation_keyframe(0.0, 'angle')
    with pytest.raises(TypeError):
        cam.add_zoom_keyframe(0.0, None)
