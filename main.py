from dataclasses import dataclass
from typing import List
import unittest
from enum import Enum


@dataclass(frozen=True)
class Range:
    # An inclusive range [low, high].
    low: float
    high: float

    def __post_init__(self) -> None:
        if self.low > self.high:
            raise ValueError(f"Invalid range: low ({self.low}) > high ({self.high})")

    def contains(self, value: float) -> bool:
        return self.low <= value <= self.high


@dataclass(frozen=True)
class Camera:
    distance: Range
    light: Range

class Axis(Enum):
    DISTANCE = "distance"
    LIGHT = "light"

    def range_of(self, camera: "Camera") -> Range:
        match self:
            case Axis.DISTANCE:
                return camera.distance
            case Axis.LIGHT:
                return camera.light


def get_sample_points(target: Range, cameras: List[Camera], axis: Axis) -> List[float]:
    # Example Input/Output
    # Inputs
    # target: Range = [0, 10], 
    # cameras: List[Camera] = [{distance: [-1, 3]}, {distance: [4, 6]}, {distance: [6, 11]}], 
    # axis = Axis.DISTANCE

    # Output
    # sorted_points = [0, 3, 4, 6, 10]
    # midpoints = [1.5, 3.5, 5, 8]
    points = {target.low, target.high}

    for camera in cameras:
        camera_range = axis.range_of(camera)
        for edge in (camera_range.low, camera_range.high):
            if target.contains(edge):
                points.add(edge)

    sorted_points = sorted(points)

    # Midpoint of each consecutive pair
    midpoints = []
    for i in range(len(sorted_points) - 1):
        midpoints.append((sorted_points[i] + sorted_points[i + 1]) / 2)

    return sorted_points + midpoints


def is_covered_by_any(distance: float, light: float, cameras: List[Camera]) -> bool:
    # True if at least one camera supports this exact (distance, light) point.
    for camera in cameras:
        if camera.distance.contains(distance) and camera.light.contains(light):
            return True
    return False


def cameras_cover_target(
    target_distance: Range,
    target_light: Range,
    cameras: List[Camera],
) -> bool:
    if not cameras:
        return False

    distance_points = get_sample_points(target_distance, cameras, "distance")
    light_points = get_sample_points(target_light, cameras, "light")

    for d in distance_points:
        for l in light_points:
            if not is_covered_by_any(d, l, cameras):
                return False  # found a gap, no need to keep looking

    return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def cam(d_low, d_high, l_low, l_high) -> Camera:
    """Small helper so the tests are easier to read."""
    return Camera(Range(d_low, d_high), Range(l_low, l_high))


class TestCamerasCoverTarget(unittest.TestCase):
    def setUp(self):
        self.target_d = Range(0, 10)
        self.target_l = Range(0, 100)

    def check(self, cameras) -> bool:
        return cameras_cover_target(self.target_d, self.target_l, cameras)

    def test_no_cameras(self):
        self.assertFalse(self.check([]))

    def test_single_camera_exact_match(self):
        self.assertTrue(self.check([cam(0, 10, 0, 100)]))

    def test_single_camera_bigger_than_target(self):
        self.assertTrue(self.check([cam(-5, 20, -50, 500)]))

    def test_single_camera_too_small(self):
        self.assertFalse(self.check([cam(0, 9, 0, 100)]))

    def test_two_cameras_touching_at_edge(self):
        cameras = [cam(0, 5, 0, 100), cam(5, 10, 0, 100)]
        self.assertTrue(self.check(cameras))

    def test_two_cameras_with_gap(self):
        cameras = [cam(0, 4.9, 0, 100), cam(5, 10, 0, 100)]
        self.assertFalse(self.check(cameras))

    def test_four_quadrants_cover_target(self):
        cameras = [
            cam(0, 5, 0, 50),
            cam(5, 10, 0, 50),
            cam(0, 5, 50, 100),
            cam(5, 10, 50, 100),
        ]
        self.assertTrue(self.check(cameras))

    def test_missing_one_corner(self):
        # Top-right quadrant is missing
        cameras = [
            cam(0, 5, 0, 50),
            cam(5, 10, 0, 50),
            cam(0, 5, 50, 100),
        ]
        self.assertFalse(self.check(cameras))

    def test_overlapping_cameras(self):
        cameras = [cam(0, 6, 0, 100), cam(4, 10, 0, 100)]
        self.assertTrue(self.check(cameras))

    def test_camera_outside_target_is_ignored(self):
        cameras = [cam(20, 30, 0, 100)]
        self.assertFalse(self.check(cameras))

    def test_hole_in_the_middle(self):
        # Four cameras around the edges leave a hole in the center
        cameras = [
            cam(0, 10, 0, 40),
            cam(0, 10, 60, 100),
            cam(0, 4, 40, 60),
            cam(6, 10, 40, 60),
        ]
        self.assertFalse(self.check(cameras))

    def test_degenerate_target_single_point(self):
        self.assertTrue(cameras_cover_target(Range(5, 5), Range(50, 50), [cam(0, 10, 0, 100)]))
        self.assertFalse(cameras_cover_target(Range(5, 5), Range(50, 50), [cam(6, 10, 0, 100)]))

    def test_invalid_range_raises(self):
        with self.assertRaises(ValueError):
            Range(10, 0)


if __name__ == "__main__":
    unittest.main()