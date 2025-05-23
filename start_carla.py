import time
import carla
import argparse
import logging
from numpy import random

def clean_objects(world):
    """
    Disable unnecessary environment objects in the CARLA world to optimize performance.
    This includes streetlights, foliage, food-related objects, and vehicles.
    """
    settings = world.get_settings()
    settings.fixed_delta_seconds = 0.05  # Set simulation to 20 FPS
    world.apply_settings(settings)

    # Disable specific environment objects
    env_objs = world.get_environment_objects()
    objects_to_toggle = []
    for obj in env_objs:
        if obj.name.startswith('BP_StreetLight_wall10'):  # Streetlights
            objects_to_toggle.append(obj.id)
        if obj.name.startswith('InstancedFoliageActor'):  # Foliage
            objects_to_toggle.append(obj.id)
        if 'Food' in obj.name:  # Food-related objects
            objects_to_toggle.append(obj.id)
    world.enable_environment_objects(objects_to_toggle, False)

    # Disable all cars in the environment
    env_vehicles = world.get_environment_objects(carla.CityObjectLabel.Car)
    objects_to_toggle = [obj.id for obj in env_vehicles]
    world.enable_environment_objects(objects_to_toggle, False)

    # Disable all motorcycles in the environment
    env_vehicles = world.get_environment_objects(carla.CityObjectLabel.Motorcycle)
    objects_to_toggle = [obj.id for obj in env_vehicles]
    world.enable_environment_objects(objects_to_toggle, False)
    return

def set_weather(world, _kind):
    """
    Set the weather conditions in the CARLA world based on the specified kind.
    Weather types:
    0 - Sunny
    1 - Night
    2 - Foggy
    3 - Rainy
    """
    weather = world.get_weather()
    if _kind == 0:  # Sunny weather
        weather.sun_altitude_angle = 40
        weather.cloudiness = 0
        weather.precipitation = 0
        weather.precipitation_deposits = 0
        weather.wetness = 0
        weather.wind_intensity = 0
        weather.fog_density = 0
    elif _kind == 1:  # Night
        weather.sun_altitude_angle = -30
    elif _kind == 2:  # Foggy
        weather.sun_altitude_angle = 90
        weather.fog_density = 70
    elif _kind == 3:  # Rainy
        weather.sun_altitude_angle = 40
        weather.cloudiness = 90
        weather.precipitation = 80
        weather.precipitation_deposits = 85.0
        weather.wetness = 100
        weather.wind_intensity = 90
        weather.fog_density = 5
    world.set_weather(weather)
    return

def get_actor_blueprints(world, filter, generation):
    """
    Retrieve actor blueprints from the CARLA blueprint library based on the specified filter and generation.
    Args:
        world: The CARLA world object.
        filter: A string filter to match blueprint IDs.
        generation: The generation of actors to include (e.g., "1", "2", "All").
    Returns:
        A list of blueprints matching the filter and generation.
    """
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If only one blueprint matches the filter, return it regardless of generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Filter blueprints by generation if valid
        if int_generation in [1, 2, 3]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []

def main():
    """
    Main function to initialize the CARLA simulation, configure the environment, and spawn actors.
    """
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
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=50,
        type=int,
        help='Number of vehicles (default: 50)')
    argparser.add_argument(
        '--wKind', '--kind-of-weather',
        metavar='WEATHER',
        default=0,
        type=int,
        help='Kind of weather (0:Sunny, 1:Night, 2:Fog, 3:Rainy)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filterv',
        metavar='PATTERN',
        default='vehicle.*',
        help='Filter vehicle model (default: "vehicle.*")')
    argparser.add_argument(
        '--generationv',
        metavar='G',
        default='All',
        help='Restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='Filter pedestrian type (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '--generationw',
        metavar='G',
        default='2',
        help='Restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='Port to communicate with Traffic Manager (default: 8000)')
    argparser.add_argument(
        '--asynch',
        action='store_true',
        help='Activate asynchronous mode execution')
    argparser.add_argument(
        '--hybrid',
        action='store_true',
        help='Activate hybrid mode for Traffic Manager')
    argparser.add_argument(
        '-s', '--seed',
        metavar='S',
        type=int,
        help='Set random device seed and deterministic mode for Traffic Manager')
    argparser.add_argument(
        '--seedw',
        metavar='S',
        default=0,
        type=int,
        help='Set the seed for pedestrians module')
    argparser.add_argument(
        '--car-lights-on',
        action='store_true',
        default=False,
        help='Enable automatic car light management')
    argparser.add_argument(
        '--hero',
        action='store_true',
        default=False,
        help='Set one of the vehicles as hero')
    argparser.add_argument(
        '--respawn',
        action='store_true',
        default=False,
        help='Automatically respawn dormant vehicles (only in large maps)')
    argparser.add_argument(
        '--no-rendering',
        action='store_true',
        default=False,
        help='Activate no rendering mode')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    vehicles_list = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    try:
        world = client.get_world()
        clean_objects(world)  # Clean unnecessary objects from the world
        set_weather(world, args.wKind)  # Set the weather based on user input

        # Configure Traffic Manager
        traffic_manager = client.get_trafficmanager(args.tm_port)
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        if args.respawn:
            traffic_manager.set_respawn_dormant_vehicles(True)
        if args.hybrid:
            traffic_manager.set_hybrid_physics_mode(True)
            traffic_manager.set_hybrid_physics_radius(70.0)
        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)

        # Configure synchronous or asynchronous mode
        settings = world.get_settings()
        if not args.asynch:
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            else:
                synchronous_master = False
        else:
            print("You are currently in asynchronous mode. If this is a traffic simulation, \
            you could experience some issues. If it's not working correctly, switch to synchronous \
            mode by using traffic_manager.set_synchronous_mode(True)")

        if args.no_rendering:
            settings.no_rendering_mode = True
        world.apply_settings(settings)

        # Retrieve and filter blueprints for vehicles and pedestrians
        blueprints = get_actor_blueprints(world, args.filterv, args.generationv)
        if not blueprints:
            raise ValueError("Couldn't find any vehicles with the specified filters")
        blueprintsWalkers = get_actor_blueprints(world, args.filterw, args.generationw)
        if not blueprintsWalkers:
            raise ValueError("Couldn't find any walkers with the specified filters")

        if args.safe:
            blueprints = [x for x in blueprints if x.get_attribute('base_type') == 'car']

        blueprints = sorted(blueprints, key=lambda bp: bp.id)

        # Get spawn points for vehicles
        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        # Spawn vehicles
        batch = []
        hero = args.hero
        for n, transform in enumerate(spawn_points):
            if n >= args.number_of_vehicles:
                break
            again = True
            while again:
                blueprint = random.choice(blueprints)
                again = False
                banlist = ['omafiets', 'century', 'crossbike', 'yzf', 'vespa', 'ninja', 'harley-davidson', 'charger_police_2020', 'crown', 'european_hgv', 'sprinter', 't2_2021']
                for tag in blueprint.tags:
                    for ban in banlist:
                        if ban == tag:
                            again = True
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            if hero:
                blueprint.set_attribute('role_name', 'hero')
                hero = False
            else:
                blueprint.set_attribute('role_name', 'autopilot')

            # Add the vehicle to the batch for spawning
            batch.append(carla.command.SpawnActor(blueprint, transform)
                .then(carla.command.SetAutopilot(carla.command.FutureActor, True, traffic_manager.get_port())))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Enable automatic vehicle lights if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)

        print('spawned %d vehicles, press Ctrl+C to exit.' % (len(vehicles_list)))

        # Set global speed difference for Traffic Manager
        traffic_manager.global_percentage_speed_difference(30.0)

        # Main simulation loop
        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

    finally:
        # Clean up and destroy all spawned vehicles
        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = 0.05
            world.apply_settings(settings)

        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        time.sleep(0.5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')