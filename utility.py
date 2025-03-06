import carla
import math

def calculate_coordinates(detect):
    global spawn_trans
    # 탐지된 값 (radar_data 객체의 한 항목)
    azimuth = math.radians(detect.azimuth)  # 방위각을 라디안 단위로 변환
    altitude = math.radians(detect.altitude)  # 고도각을 라디안 단위로 변환
    depth = detect.depth  # 탐지된 물체까지의 거리

    # 레이더 탐지 값을 기준으로 3D 벡터 생성
    x = depth * math.cos(altitude) * math.cos(azimuth)
    y = depth * math.cos(altitude) * math.sin(azimuth)
    z = depth * math.sin(altitude)

    # 좌표를 센서의 현재 위치와 회전을 반영해 변환
    local_location = carla.Location(x=x, y=y, z=z)
    world_location = spawn_trans.transform(local_location)

    return world_location

def print_radar(world, radar_data):
    velocity_range = 1.5 # m/s
    current_rot = radar_data.transform.rotation
    print(len(radar_data))
    for detect in radar_data:
        azi = math.degrees(detect.azimuth)
        alt = math.degrees(detect.altitude)
        # The 0.25 adjusts a bit the distance so the dots can
        # be properly seen
        fw_vec = carla.Vector3D(x=detect.depth - 0.25)
        carla.Transform(
            carla.Location(),
            carla.Rotation(
                pitch=current_rot.pitch + alt,
                yaw=current_rot.yaw + azi,
                roll=current_rot.roll)).transform(fw_vec)

        def clamp(min_v, max_v, value):
            return max(min_v, min(value, max_v))

        norm_velocity = detect.velocity / velocity_range # range [-1, 1]
        r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
        g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
        b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
        world.debug.draw_point(
            radar_data.transform.location + fw_vec,
            size=0.075,
            life_time=0.06,
            persistent_lines=False,
            color=carla.Color(r, g, b))
