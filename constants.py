import numpy as np

SHADOW_CONTRAST = 1
CAR_MODEL_NAME = 'car-suv'
HUMAN_ANIMATION = 'male_running_still'
T_blender2opengl = np.array([[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) @ np.array(
    [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])

# GPS Origin
ORIGIN_LATITUDE =  40.092924
ORIGIN_LONGITUDE = -88.235239
# UTM Origin, all in meters
UTM_ORIGIN_EAST, UTM_ORIGIN_NORTH, ORIGIN_HEIGHT = 394702.00, 4438802.00, 200.0
