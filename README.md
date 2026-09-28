# CameraTest

## 6crickets

This is a response to 6crickets Interview Phase 2, General Coding Problem.

Given a bunch of hardware cameras, can they together cover every
(subject distance, light level) combo our software camera needs to support?

## Run it

    python main.py

Runs the tests. Python 3.7+, standard library only.

## Use it

    from software_camera import Range, Camera, cameras_cover_target

    target_distance = Range(0, 10)
    target_light = Range(0, 100)

    cameras = [
        Camera(Range(0, 5), Range(0, 100)),
        Camera(Range(5, 10), Range(0, 100)),
    ]

    cameras_cover_target(target_distance, target_light, cameras)  # True

## How it works

Each camera is a rectangle (distance x light). The target is a rectangle.
We're checking whether the camera rectangles fully cover the target.

We can't check infinitely many points, but coverage only changes at camera
edges. So per axis, we test:

1. every camera edge that falls inside the target
2. the midpoint between each pair of neighboring edges (this catches gaps
   _between_ edges)

Then we check every combo of distance sample x light sample. If any point
has no camera, there's a gap and we return False.
