from . import utils


def clean_action(scene, action, target_bones=None):
    # target_bones: bone names to keep. None keeps every bone in the action
    tolerance = scene.rsl_retargeting_clean_tolerance

    fcurves = utils.get_fcurves_from_action(action)
    for fcurve in list(fcurves):
        parts = fcurve.data_path.split('"')
        if len(parts) < 3:
            continue

        # Remove channels for bones that are not part of the retarget
        if target_bones is not None and parts[1] not in target_bones:
            fcurves.remove(fcurve)
            continue

        keyframes = fcurve.keyframe_points
        if not keyframes:
            fcurves.remove(fcurve)
            continue

        values = [kp.co.y for kp in keyframes]

        # Remove channels that never leave their default value, they have no effect
        default = get_default_value(fcurve)
        if all(abs(value - default) <= tolerance for value in values):
            fcurves.remove(fcurve)
            continue

        # Constant channels only need their first keyframe
        if all(abs(value - values[0]) <= tolerance for value in values):
            while len(keyframes) > 1:
                keyframes.remove(keyframes[len(keyframes) - 1], fast=True)
            fcurve.update()
            continue

        # Allowed change: the absolute tolerance or a percentage of the channel's value range, whichever is larger
        value_range = max(values) - min(values)
        allowed = max(tolerance, value_range * scene.rsl_retargeting_decimate_percent / 100)
        simplify_fcurve(fcurve, allowed)

        if scene.rsl_retargeting_smooth_iterations:
            smooth_fcurve(fcurve, scene.rsl_retargeting_smooth_iterations)

        if scene.rsl_retargeting_smooth_interpolation:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'

        fcurve.update()


def get_default_value(fcurve):
    if fcurve.data_path.endswith('rotation_quaternion'):
        return 1.0 if fcurve.array_index == 0 else 0.0
    if fcurve.data_path.endswith('scale'):
        return 1.0
    return 0.0


def simplify_fcurve(fcurve, tolerance):
    keyframes = list(fcurve.keyframe_points)
    points = [(kp.co.x, kp.co.y) for kp in keyframes]
    count = len(points)
    remove = [False] * count

    anchor = 0
    for i in range(1, count - 1):
        prev_y, y, next_y = points[i - 1][1], points[i][1], points[i + 1][1]

        # Peaks and valleys are focal points of the motion, always keep them
        if (y - prev_y) * (next_y - y) < 0:
            anchor = i
            continue

        x0, y0 = points[anchor]
        x1, y1 = points[i + 1]
        t = (points[i][0] - x0) / (x1 - x0) if x1 != x0 else 0.0
        if abs(y0 + (y1 - y0) * t - y) <= tolerance:
            remove[i] = True
        else:
            anchor = i

    # Remove from the end so the indices of the remaining keys stay valid
    for i in reversed(range(count)):
        if remove[i]:
            fcurve.keyframe_points.remove(fcurve.keyframe_points[i], fast=True)
    fcurve.update()


def smooth_fcurve(fcurve, passes):
    keyframes = list(fcurve.keyframe_points)
    for _ in range(passes):
        values = [kp.co.y for kp in keyframes]
        for i in range(1, len(keyframes) - 1):
            keyframes[i].co.y = (values[i - 1] + 2 * values[i] + values[i + 1]) / 4
    fcurve.update()
