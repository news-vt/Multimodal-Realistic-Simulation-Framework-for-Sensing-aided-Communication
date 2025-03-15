function [rays, tx, txArray, num_vehicle, bsArrayOrientation] = GetNetworkInfo(gpsEpiPath, inputfilename, mapname, txPos, bsArrayOrientation)
    % This function calculates network information using ray tracing.
    % Inputs:
    % - gpsEpiPath: Path to the GPS data directory
    % - inputfilename: Name of the input GPS data file
    % - mapname: Name of the 3D map file
    % - txPos: Position of the transmitter (base station)
    % - bsArrayOrientation: Orientation of the base station antenna
    % Outputs:
    % - rays: Ray tracing results
    % - tx: Transmitter site object
    % - txArray: Transmitter antenna array
    % - num_vehicle: Number of vehicles in the simulation
    % - bsArrayOrientation: Orientation of the base station antenna
    
    % Load GPS data from the input file
    gpsfilePath = fullfile(gpsEpiPath, inputfilename);
    data = readtable(gpsfilePath);
    
    % Initialize the site viewer for visualization
    viewer = siteviewer(SceneModel=mapname, ShowEdges=false, ShowOrigin=false);
    
    % Transmitter (Tx) parameters
    fc = 28e9; % Carrier frequency (28 GHz)
    c = physconst('LightSpeed'); % Speed of light (m/s)
    lambda = c / fc; % Wavelength
    bsAntSize = [8 8]; % Base station antenna size (8x8 elements)
    
    % Define the base station antenna array for beamforming
    txArray = phased.URA('Size', bsAntSize, 'ElementSpacing', 0.5*lambda*[1 1]);
    tx = txsite("cartesian", Antenna=txArray, AntennaAngle=bsArrayOrientation, ...
        AntennaPosition=txPos, AntennaHeight=4, TransmitterFrequency=fc);
    
    % Define the propagation model for ray tracing
    pm = propagationModel("raytracing", ...
        CoordinateSystem="cartesian", ...
        AngularSeparation="High", ...
        MaxNumDiffractions=1, Method="sbr", ...
        MaxNumReflections=1, MaxAbsolutePathLoss=120);
    
    % User Equipment (UE) antenna parameters
    ueAntSize = [2 2]; % UE antenna size (2x2 elements)
    num_vehicle = size(data); % Number of vehicles in the GPS data
    
    % Initialize receiver (Rx) site objects
    rxArray = cell(1, num_vehicle(1)); % Cell array to store UE antenna arrays
    rx = repmat(rxsite, 1, num_vehicle(1)); % Array of Rx site objects
    
    % Iterate through each vehicle in the GPS data
    for i_v = 1:num_vehicle(1)
        iter_Z = 2; % Default height offset for vehicles
    
        % Define a mapping of vehicle IDs to height offsets
        keys = {
            'vehicle.audi.a2', 'vehicle.audi.etron', 'vehicle.audi.tt', ...
            'vehicle.bmw.grandtourer', 'vehicle.carlamotors.carlacola', ...
            'vehicle.carlamotors.firetruck', 'vehicle.chevrolet.impala', ...
            'vehicle.citroen.c3', 'vehicle.dodge.charger_2020', ...
            'vehicle.dodge.charger_police', 'vehicle.ford.ambulance', ...
            'vehicle.ford.mustang', 'vehicle.lincoln.mkz_2017', ...
            'vehicle.lincoln.mkz_2020', 'vehicle.mercedes.coupe', ...
            'vehicle.mercedes.coupe_2020', 'vehicle.micro.microlino', ...
            'vehicle.mini.cooper_s', 'vehicle.mini.cooper_s_2021', ...
            'vehicle.mitsubishi.fusorosa', 'vehicle.nissan.micra', ...
            'vehicle.nissan.patrol', 'vehicle.nissan.patrol_2021', ...
            'vehicle.seat.leon', 'vehicle.tesla.cybertruck', ...
            'vehicle.toyota.prius', 'vehicle.volkswagen.t2'
        };
    
        values = [
            1.7, 1.8, 1.6, 1.7, 2.6, 4.0, 1.5, 1.7, 1.7, 1.7, ...
            1.6, 1.4, 1.7, 1.7, 1.8, 1.6, 1.5, 1.6, 1.8, 4.5, ...
            1.7, 2.0, 2.2, 1.6, 2.3, 1.6, 2.2
        ];
    
        % Create a map object for vehicle heights
        vehicleMap = containers.Map(keys, values);
    
        % Search for the height offset of the current vehicle
        searchKey = string(data.Vehicle_ID(i_v));
        if isKey(vehicleMap, searchKey)
            iter_Z = vehicleMap(searchKey);
        end
    
        % Define the receiver position (X, Y, Z + height offset)
        rxPos = [data.X(i_v); data.Y(i_v); data.Z(i_v) + iter_Z];
        rxArray{i_v} = phased.URA('Size', ueAntSize, 'ElementSpacing', 0.5*lambda*[1 1]);
        rx(i_v) = rxsite("cartesian", Antenna=rxArray{i_v}, AntennaPosition=rxPos);
    end
    
    % Perform ray tracing between the transmitter and receivers
    tic
    rays = raytrace(tx, rx, pm, Type="power");
    toc
    
    % Close the site viewer
    viewer.close
    end