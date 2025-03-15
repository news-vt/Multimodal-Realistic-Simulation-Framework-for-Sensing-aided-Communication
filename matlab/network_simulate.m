function [] = network_simulate(saveroot, blenderpath, txPos, bsArrayOrientation)
    % Transpose the transmitter position and base station orientation for compatibility
    txPos = txPos.';
    bsArrayOrientation = bsArrayOrientation.';

    % Load beamforming weights from the pre-saved file
    load_weights = load('beam_weights.mat', 'beam_weights');
    weight_list = [load_weights.beam_weights.single_beam; ...
                   load_weights.beam_weights.double_beam; ...
                   load_weights.beam_weights.triple_beam];

    % Set the Python environment for Blender
    pyenv('Version', blenderpath);

    % Define the root folder path for GPS and network data
    folderPath = saveroot;
    gpsPath = folderPath + "\_out_gps\";
    contents = dir(gpsPath);

    % Filter out only subfolders, excluding '.' and '..'
    subFolders = contents([contents.isdir] & ~ismember({contents.name}, {'.', '..'}));

    % Iterate through each subfolder
    for i = 1:length(subFolders)
        gpsEpiPath = gpsPath + subFolders(i).name; % Path to GPS data for the current episode
        netEpiPath = folderPath + "\_out_net\" + subFolders(i).name; % Path to save network data

        % Create the network output folder if it doesn't exist
        if ~isfolder(netEpiPath)
            mkdir(netEpiPath);
        end

        % Get the list of CSV files in the current GPS folder
        csvFiles = dir(fullfile(gpsEpiPath, '*.csv'));

        % Process each CSV file in the folder
        for k = 1:length(csvFiles)
            inputfilename = string(csvFiles(k).name);

            % Skip processing if the output file already exists
            if isfile(netEpiPath + "\" + inputfilename + ".mat")
                disp(inputfilename + " already exists.");
                continue
            end

            % Combine 3D map data using Blender
            tic
            py.bpy_combine.main(saveroot, string(subFolders(i).name) + "/" + inputfilename, ...
                                "Town10_2lane.glb", "temp_map.glb");
            toc

            % Perform ray tracing and network simulation
            [rays_result, ~, txArray, num_vehicle, bsArrayOrientation] = ...
                GetNetworkInfo(gpsEpiPath, inputfilename, "temp_map.glb", txPos, bsArrayOrientation);

            % Initialize variables for RSS (Received Signal Strength) calculation
            tic
            list_RSS = zeros(num_vehicle(1) + 1, length(weight_list)); % RSS values for each beam
            best_RSS_dB = -inf; % Best RSS value (initialized to negative infinity)

            % Iterate through each beamforming weight
            for i_w = 1:length(weight_list)
                txArray.Taper = weight_list{i_w}; % Apply the current beamforming weight
                arrayResponse = phased.ArrayResponse('SensorArray', txArray, ...
                                                     'PropagationSpeed', physconst('LightSpeed'));
                avg_RSS_dB = 0; % Average RSS for the current weight
                vehicle_iter = 1; % Vehicle index

                % Process each ray tracing result
                for ray = rays_result
                    total_RSS_linear = 0; % Total RSS in linear scale

                    % Process each ray path
                    for i_ray = 1:length(ray{1})
                        i_pathloss = ray{1,1}(1,i_ray).PathLoss; % Path loss for the ray
                        incidentAngle = ray{1,1}(1,i_ray).AngleOfDeparture; % Angle of departure
                        incidentAngle = incidentAngle + bsArrayOrientation; % Adjust for base station orientation

                        % Normalize angles to the range [-180, 180]
                        if incidentAngle(1, 1) > 180
                            incidentAngle(1, 1) = incidentAngle(1, 1) - 360;
                        end
                        if incidentAngle(1, 1) < -180
                            incidentAngle(1, 1) = incidentAngle(1, 1) + 360;
                        end

                        % Calculate the array response for the incident angle
                        response = arrayResponse(28e9, incidentAngle);
                        abs_rsp = abs(response);

                        % Convert the response magnitude to dB
                        magnitude = mag2db(abs_rsp);
                        RSS_dB = magnitude - i_pathloss;

                        % Convert RSS to linear scale and accumulate
                        total_RSS_linear = total_RSS_linear + 10^(RSS_dB / 10);
                    end

                    % Convert total RSS back to dB
                    if total_RSS_linear == 0
                        total_RSS_dB = -200; % Assign a very low value if no signal is received
                    else
                        total_RSS_dB = 10 * log10(total_RSS_linear);
                    end

                    % Store the RSS value for the current vehicle and weight
                    list_RSS(vehicle_iter, i_w) = total_RSS_dB;
                    avg_RSS_dB = avg_RSS_dB + total_RSS_dB;
                    vehicle_iter = vehicle_iter + 1;
                end

                % Calculate the average RSS for the current weight
                avg_RSS_dB = avg_RSS_dB / length(rays_result);
                list_RSS(num_vehicle(1) + 1, i_w) = avg_RSS_dB;

                % Update the best RSS value if the current one is better
                if avg_RSS_dB > best_RSS_dB
                    best_RSS_dB = avg_RSS_dB;
                end
            end

            % Save the results to a .mat file
            fprintf('Done and Save: %s\n', fullfile(netEpiPath + "\" + inputfilename + ".mat"));
            save(fullfile(netEpiPath + "\" + inputfilename + ".mat"), 'rays_result', 'list_RSS');
            toc
        end
    end
end