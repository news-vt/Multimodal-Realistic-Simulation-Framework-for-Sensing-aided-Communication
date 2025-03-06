function [rays, tx, txArray, num_vehicle, bsArrayOrientation] = GetNetworkInfo(gpsEpiPath, inputfilename, mapname, txPos, bsArrayOrientation)
gpsfilePath = fullfile(gpsEpiPath, inputfilename);
data = readtable(gpsfilePath);

viewer = siteviewer(SceneModel=mapname, ShowEdges=false, ShowOrigin=false);

% Tx Parameters
fc = 28e9; % Carrier frequency (28 GHz)
c = physconst('LightSpeed'); % Speed of light (m/s)
lambda = c / fc; % Wavelength
bsAntSize = [8 8]; % Number of rows and columns in rectangular array (base station)

% Define NR Rectangular Panel Array for Beamforming
txArray = phased.URA('Size', bsAntSize, 'ElementSpacing', 0.5*lambda*[1 1]);
tx = txsite("cartesian", Antenna=txArray, AntennaAngle=bsArrayOrientation, AntennaPosition=txPos, AntennaHeight=4, TransmitterFrequency=fc);
pm = propagationModel("raytracing", ...
    CoordinateSystem="cartesian", ...
    AngularSeparation="High", ...
    MaxNumDiffractions=1, Method="sbr", MaxNumReflections=1, MaxAbsolutePathLoss=120);

ueAntSize = [2 2]; % Number of rows and columns in rectangular array (UE)
num_vehicle = size(data);

% rxsite 객체 배열 초기화
rxArray = cell(1, num_vehicle(1));
rx = repmat(rxsite, 1, num_vehicle(1));
for i_v = 1:num_vehicle(1)
    iter_Z = 2;
    
    % 데이터 정의
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
    
    % Map 객체 생성
    vehicleMap = containers.Map(keys, values);
    
    % 특정 항목 검색
    searchKey = string(data.Vehicle_ID(i_v));
    if isKey(vehicleMap, searchKey)
        iter_Z = vehicleMap(searchKey);
    end

    rxPos = [data.X(i_v);data.Y(i_v);data.Z(i_v) + iter_Z];
    rxArray{i_v} = phased.URA('Size', ueAntSize, 'ElementSpacing', 0.5*lambda*[1 1]);
    rx(i_v) = rxsite("cartesian", Antenna=rxArray{i_v}, AntennaPosition=rxPos);
end

tic
rays = raytrace(tx, rx, pm, Type="power");
toc

viewer.close
end