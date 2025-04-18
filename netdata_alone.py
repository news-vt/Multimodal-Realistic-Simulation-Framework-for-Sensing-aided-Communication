import matlab.engine
import config

def do_matlab():
    # Start MATLAB engine
    eng = matlab.engine.start_matlab()
    
    # Change the working directory to the 'matlab' folder
    eng.cd('.\matlab')  

    # Retrieve the base station location from the configuration
    bs_location = config.GlobalConfig.bs_location
    # Adjust the y-coordinate (invert its sign)
    bs_location[1] *= -1

    # Retrieve the base station rotation from the configuration
    bs_rotation = config.GlobalConfig.bs_rotation
    # Adjust the x-axis rotation by adding 90 degrees
    bs_rotation[1] += 90
    bs_rotation = bs_rotation[1:]

    # Call the MATLAB function with the required parameters
    # - MAT_SAVE_ROOT: Path to save MATLAB output
    # - BLENDER_PATH: Path to Blender files
    # - bs_location: Adjusted base station location
    # - bs_rotation: Adjusted base station rotation
    eng.network_simulate(config.GlobalConfig.MAT_SAVE_ROOT,
                    config.GlobalConfig.BLENDER_PATH,
                    matlab.double(bs_location)[0],
                    matlab.double(bs_rotation)[0],
                    nargout=0)

    # Close the MATLAB engine after execution
    eng.quit()