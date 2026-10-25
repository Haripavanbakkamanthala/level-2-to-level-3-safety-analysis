import math

def brake_outcome(speed_kmh, distance_m, delay_s, deceleration):
    """Point vehicle approaching a fixed conflict line on a level road."""
    if speed_kmh <= 0 or distance_m < 0 or delay_s < 0 or deceleration <= 0:
        raise ValueError("Use positive speed/deceleration and nonnegative distance/delay")
    v = speed_kmh / 3.6
    delay_distance = v * delay_s
    stopping_distance = delay_distance + v**2 / (2 * deceleration)
    clearance = distance_m - stopping_distance
    reaches_line = clearance < -1e-9
    if distance_m <= delay_distance:
        impact_speed = v
    else:
        impact_speed = math.sqrt(max(0, v**2 - 2 * deceleration * (distance_m - delay_distance)))
    return {"stopping_distance_m": stopping_distance,
            "clearance_m": clearance,
            "impact_speed_kmh": impact_speed * 3.6,
            "reaches_conflict_line": reaches_line}
