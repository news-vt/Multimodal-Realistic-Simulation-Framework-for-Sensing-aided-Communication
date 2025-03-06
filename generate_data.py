import carla
import argparse
import os
import time
import pandas as pd
import numpy as np
import config

rgb_count = 0
lidar_count = 0
radar_count = 0
END_EPI = False

def save_image_gps(_image, _world, _client, _path, _x, _y):
    no_vehicle = True
    vehicles = _world.get_actors().filter('vehicle.*')
    for vehicle in vehicles:
        if _x[0] < vehicle.get_transform().location.x and vehicle.get_transform().location.x < _x[1] and _y[0] < -vehicle.get_transform().location.y and -vehicle.get_transform().location.y < _y[1]:
            no_vehicle = False
            break

    global END_EPI
    global rgb_count
    if rgb_count == config.GlobalConfig.MAX_STEP or no_vehicle:
        actor_list = _world.get_actors()
        for actor in actor_list:
            if actor.type_id == "sensor.camera.rgb":
                _client.apply_batch([carla.command.DestroyActor(actor.id)])
        END_EPI = True
        return
    rgb_count += 1
    #print(vehicles[0].get_veloctity())
    # 엑셀로 저장
    pd.DataFrame([{ #object_type
        "Timestamp": time.time(),
        "Vehicle_ID": vehicle.type_id,
        "X": vehicle.get_transform().location.x,
        "Y": -vehicle.get_transform().location.y,
        "Z": vehicle.get_transform().location.z,
        "Yaw": vehicle.get_transform().rotation.yaw,
        "Pitch": vehicle.get_transform().rotation.pitch,
        "Roll": vehicle.get_transform().rotation.roll,
        #"Speed": vehicle.get_veloctity()
    }
    for vehicle in vehicles
    if _x[0] < vehicle.get_transform().location.x and vehicle.get_transform().location.x < _x[1] and _y[0] < -vehicle.get_transform().location.y and -vehicle.get_transform().location.y < _y[1]
    ]).to_csv(config.GlobalConfig.SAVE_ROOT + "_out_gps" + _path + "/%06d.csv" % _image.frame, mode='a', index=False)
    _image.save_to_disk(config.GlobalConfig.SAVE_ROOT + '_out_rgb' + _path + '/%06d.png' % _image.frame)
    return

def save_lidar(_client, _world, _lidar, _path):
    global lidar_count
    if lidar_count == config.GlobalConfig.MAX_STEP:
        actor_list = _world.get_actors()
        for actor in actor_list:
            if actor.type_id == "sensor.lidar.ray_cast":
                _client.apply_batch([carla.command.DestroyActor(actor.id)])
        return
    lidar_count += 1
    _lidar.save_to_disk(config.GlobalConfig.SAVE_ROOT + '_out_lidar' + _path + '/%06d.ply' % _lidar.frame)
    return

def save_radar(_client, _world, _radar, _path):
    global radar_count
    if radar_count == config.GlobalConfig.MAX_STEP:
        actor_list = _world.get_actors()
        for actor in actor_list:
            if actor.type_id == "sensor.other.radar":
                _client.apply_batch([carla.command.DestroyActor(actor.id)])
        return
    radar_count += 1

    points = np.frombuffer(_radar.raw_data, dtype=np.dtype('f4'))
    points = np.reshape(points, (len(_radar), 4))

    # Radar 데이터를 .npy 파일로 저장
    np.save(config.GlobalConfig.SAVE_ROOT + '_out_radar' + _path + '/%06d.npy' % _radar.frame, points)
    return

def set_basestation(world):
    basestation = carla.Transform()
    basestation.location = carla.Location(*config.GlobalConfig.bs_location)
    basestation.rotation = carla.Rotation(*config.GlobalConfig.bs_rotation)
    world.get_spectator().set_transform(basestation)
    return

def delete_sensors(_client, _world):
    actor_list = _world.get_actors()
    for actor in actor_list:
        if actor.type_id == "sensor.camera.rgb" or actor.type_id == "sensor.lidar.ray_cast" or actor.type_id == "sensor.other.radar":
            _client.apply_batch([carla.command.DestroyActor(actor.id)])
    return

def run_sensor(client, world):
    original_settings = world.get_settings()
    settings = world.get_settings()
    settings.fixed_delta_seconds = 0.05 # 20 fps
    settings.synchronous_mode = True
    world.apply_settings(settings)

    bp_lib = world.get_blueprint_library()
    spawn_trans = world.get_spectator().get_transform()

    camera_bp = bp_lib.filter("sensor.camera.rgb")[0]
    lidar_bp = bp_lib.filter("sensor.lidar.ray_cast")[0]
    radar_bp = bp_lib.filter("sensor.other.radar")[0]

    # Configure the blueprints
    camera_bp.set_attribute("image_size_x", str(960))
    camera_bp.set_attribute("image_size_y", str(540))
    camera_bp.set_attribute('sensor_tick', '0.1')
    camera_bp.set_attribute('fov', '110')

    lidar_bp.set_attribute('upper_fov', str(25.5))
    lidar_bp.set_attribute('lower_fov', str(-22.5))
    lidar_bp.set_attribute('channels', str(32))
    lidar_bp.set_attribute('range', str(250))
    lidar_bp.set_attribute('rotation_frequency', str(20))
    lidar_bp.set_attribute('points_per_second', str(1500000))
    lidar_bp.set_attribute('sensor_tick', '0.1')

    radar_bp.set_attribute('horizontal_fov', str(150.0))
    radar_bp.set_attribute('vertical_fov', str(30.0))
    radar_bp.set_attribute('range', str(50))
    radar_bp.set_attribute('sensor_tick', '0.1')
    radar_bp.set_attribute('points_per_second',  str(20000))


    folderpath = config.GlobalConfig.SAVE_ROOT
    epsode_name = config.GlobalConfig.EPI_NAME
    if not os.path.isdir(folderpath + "_out_rgb" + epsode_name):
        os.makedirs(folderpath + "_out_rgb" + epsode_name)  # 폴더 생성
    if not os.path.isdir(folderpath + "_out_gps" + epsode_name):
        os.makedirs(folderpath + "_out_gps" + epsode_name)  # 폴더 생성
    if not os.path.isdir(folderpath + "_out_lidar" + epsode_name):
        os.makedirs(folderpath + "_out_lidar" + epsode_name)  # 폴더 생성
    if not os.path.isdir(folderpath + "_out_radar" + epsode_name):
        os.makedirs(folderpath + "_out_radar" + epsode_name)  # 폴더 생성

    # We create all the sensors and keep them in a list for convenience.
    sensor_list = []

    camera = world.spawn_actor(blueprint=camera_bp, transform=spawn_trans)
    camera.listen(lambda image: save_image_gps(image, world, client, epsode_name, config.GlobalConfig.MAP_X, config.GlobalConfig.MAP_Y))
    sensor_list.append(camera)

    lidar = world.spawn_actor(blueprint=lidar_bp, transform=spawn_trans)
    lidar.listen(lambda lidar: save_lidar(client, world, lidar, epsode_name))
    sensor_list.append(lidar)

    radar_trans = spawn_trans
    radar_trans.location.z = 5
    radar_trans.rotation.pitch = 0
    radar = world.spawn_actor(blueprint=radar_bp, transform=radar_trans)
    radar.listen(lambda radar: save_radar(client, world, radar, epsode_name))
    sensor_list.append(radar)

    try:
        # Main loop
        while not END_EPI:
            # Tick the server
            world.tick()
            w_frame = world.get_snapshot().frame
            print("\nWorld's frame: %d" % w_frame)
    finally:
        world.apply_settings(original_settings)
        for sensor in sensor_list:
            sensor.destroy()

    return

def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')

    args = argparser.parse_args()
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    world = client.get_world()

    set_basestation(world)
    run_sensor(client, world)

    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')