function [] = network_simulate(saveroot, blenderpath, txPos, bsArrayOrientation)
    txPos = txPos.';
    bsArrayOrientation = bsArrayOrientation.';
    
    load_weights= load('beam_weights.mat', 'beam_weights');
    weight_list = [load_weights.beam_weights.single_beam; load_weights.beam_weights.double_beam; load_weights.beam_weights.triple_beam];
    pyenv('Version', blenderpath);
    
    % 지정된 폴더 경로
    folderPath = saveroot;
    gpsPath = folderPath + "\_out_gps\";
    contents = dir(gpsPath);
    % 폴더인 경우만 선택하고 '.' 및 '..' 제거
    subFolders = contents([contents.isdir] & ~ismember({contents.name}, {'.', '..'}));
    
    % 폴더 이름 출력
    for i = 1:length(subFolders)
        gpsEpiPath = gpsPath + subFolders(i).name;
        netEpiPath = folderPath + "\_out_net\" + subFolders(i).name;
    
        if ~isfolder(netEpiPath)
            mkdir(netEpiPath);
        end
        
        % 폴더 내 CSV 파일 목록 가져오기
        csvFiles = dir(fullfile(gpsEpiPath, '*.csv'));
    
        % 각 CSV 파일을 순서대로 불러오기
        for k = 1:length(csvFiles)
            inputfilename = string(csvFiles(k).name);
            if isfile(netEpiPath + "\" + inputfilename + ".mat")
                disp(inputfilename + " 파일이 존재합니다.");
                continue
            end
    
            tic
            py.bpy_combine.main(saveroot, string(subFolders(i).name) + "/" + inputfilename, "Town10_2lane.glb", "temp_map.glb");
            toc
    
            [rays_result, ~, txArray, num_vehicle, bsArrayOrientation] = GetNetworkInfo(gpsEpiPath, inputfilename, "temp_map.glb", txPos, bsArrayOrientation);
    
            tic
            list_RSS = zeros(num_vehicle(1) + 1, length(weight_list));
            best_RSS_dB = -inf;
            for i_w = 1:length(weight_list)
                txArray.Taper = weight_list{i_w};
                arrayResponse = phased.ArrayResponse('SensorArray', txArray, 'PropagationSpeed', physconst('LightSpeed'));
                avg_RSS_dB = 0;
                vehicle_iter = 1;
                for ray = rays_result
                    total_RSS_linear = 0;
                    for i_ray = 1:length(ray{1})
                        i_pathloss = ray{1,1}(1,i_ray).PathLoss;
                        incidentAngle = ray{1,1}(1,i_ray).AngleOfDeparture;
                        incidentAngle = incidentAngle + bsArrayOrientation;
                        if incidentAngle(1, 1) > 180
                            incidentAngle(1, 1) = incidentAngle(1, 1) - 360;
                        end
                        if incidentAngle(1, 1) < -180
                            incidentAngle(1, 1) = incidentAngle(1, 1) + 360;
                        end
                        response = arrayResponse(28e9, incidentAngle);
                        abs_rsp = abs(response);
    
                        % 세기의 절대값 계산
                        magnitude = mag2db(abs_rsp);
                        RSS_dB = magnitude - i_pathloss;
    
                        % 총합을 위해 RSS를 선형 공간으로 변환하고 합산
                        total_RSS_linear = total_RSS_linear + 10^(RSS_dB / 10);
                    end
                    if total_RSS_linear == 0
                        total_RSS_dB = -200;
                    else
                        total_RSS_dB = 10 * log10(total_RSS_linear);
                    end            
                    list_RSS(vehicle_iter, i_w) = total_RSS_dB;
                    avg_RSS_dB = avg_RSS_dB + total_RSS_dB;
                    vehicle_iter = vehicle_iter + 1;
                end
                avg_RSS_dB = avg_RSS_dB/length(rays_result);
                list_RSS(num_vehicle(1) + 1, i_w) = avg_RSS_dB;
                % fprintf('평균 RSS (dB): %.2f\n', avg_RSS_dB);
                if avg_RSS_dB > best_RSS_dB
                    best_RSS_dB = avg_RSS_dB;
                end
            end
            fprintf('Done and Save : %s', fullfile(netEpiPath + "\" + inputfilename + ".mat"));
            save(fullfile(netEpiPath + "\" + inputfilename + ".mat"), 'rays_result', 'list_RSS');
            toc
        end
    end
end

