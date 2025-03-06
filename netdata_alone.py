import matlab.engine
import config

# Start MATLAB engine
eng = matlab.engine.start_matlab()
eng.cd('.\matlab')  # 경로 설정

bs_location = config.GlobalConfig.bs_location
bs_location[1] *= -1
bs_rotation = config.GlobalConfig.bs_rotation
bs_rotation[0] += 90

# Call the MATLAB function
eng.my_function(config.GlobalConfig.MAT_SAVE_ROOT,
                config.GlobalConfig.BLENDER_PATH,
                matlab.double(bs_location)[0],
                matlab.double(bs_rotation)[0],
                nargout=0)

# Close MATLAB engine
eng.quit()