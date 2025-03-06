class GlobalConfig:
    MAX_STEP = 200 # maximum step of each episode
    SAVE_ROOT = './out/'
    EPI_NAME = '/episode_x'
    MAT_SAVE_ROOT = '../out/'
    BLENDER_PATH = 'D:/Program Files/Blender Foundation/Blender 4.2/4.2/python/bin/python.exe' # Your Blender Path

    # 2 Lane Scenario
    MAP_X = [-90, 115]
    MAP_Y = [0, 120]
    bs_location = [26.252628, -86.328842, 21.305660]
    bs_rotation = [-40, 90, 0]
    
    '''# 3 Lane Scenario
    MAP_X = [-30, 135]
    MAP_Y = [-190, 150]
    bs_location = [126.502670, 21.093103, 11.288552]
    bs_rotation = [-12, 180, 0]'''