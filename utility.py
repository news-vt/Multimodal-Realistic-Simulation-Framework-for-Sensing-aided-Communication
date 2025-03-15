import carla
import math

def calculate_coordinates(detect):
    global spawn_trans
    # Extract radar detection data
    # - azimuth: Angle in the horizontal plane (converted to radians)
    # - altitude: Angle in the vertical plane (converted to radians)
    # - depth: Distance to the detected object
    azimuth = math.radians(detect.azimuth)  # Convert azimuth to radians
    altitude = math.radians(detect.altitude)  # Convert altitude to radians
    depth = detect.depth  # Distance to the detected object

    # Calculate 3D coordinates based on radar detection
    x = depth * math.cos(altitude) * math.cos(azimuth)
    y = depth * math.cos(altitude) * math.sin(azimuth)
    z = depth * math.sin(altitude)

    # Transform the local coordinates to world coordinates
    # using the sensor's current position and rotation
    local_location = carla.Location(x=x, y=y, z=z)
    world_location = spawn_trans.transform(local_location)

    return world_location

def print_radar(world, radar_data):
    # Define the velocity range for normalization
    velocity_range = 1.5  # m/s

    # Get the current rotation of the radar sensor
    current_rot = radar_data.transform.rotation

    # Print the number of detected objects
    print(len(radar_data))

    # Iterate through each detection in the radar data
    for detect in radar_data:
        # Convert azimuth and altitude to degrees for debugging
        azi = math.degrees(detect.azimuth)
        alt = math.degrees(detect.altitude)

        # Adjust the depth slightly for better visualization
        fw_vec = carla.Vector3D(x=detect.depth - 0.25)

        # Transform the forward vector based on the radar's rotation
        carla.Transform(
            carla.Location(),
            carla.Rotation(
                pitch=current_rot.pitch + alt,
                yaw=current_rot.yaw + azi,
                roll=current_rot.roll)).transform(fw_vec)

        # Helper function to clamp a value between a minimum and maximum
        def clamp(min_v, max_v, value):
            return max(min_v, min(value, max_v))

        # Normalize the velocity to the range [-1, 1]
        norm_velocity = detect.velocity / velocity_range

        # Calculate RGB color values based on the normalized velocity
        r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
        g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
        b = int(abs(clamp(-1.0, 0.0, -1.0 - norm_velocity)) * 255.0)

        # Draw the radar detection point in the world
        # - Location: Transformed location of the detection
        # - Size: Size of the point
        # - Life time: Duration the point remains visible
        # - Persistent lines: Whether the point persists over time
        # - Color: RGB color based on velocity
        world.debug.draw_point(
            radar_data.transform.location + fw_vec,
            size=0.075,
            life_time=0.06,
            persistent_lines=False,
            color=carla.Color(r, g, b))