import glm
from pyrr import Vector3
import math
import numpy as np
import datetime
import pvlib
from constants import T_blender2opengl, ORIGIN_LATITUDE, ORIGIN_LONGITUDE

class Light:
    def __init__(self,
                 direction,
                 color,
                 intensity_config,
                 shadow_poisson_sampling_denominator,
                 gamma_correction,
                 fixed_light_height=20
    ):
        self.direction = np.array(direction).astype(np.float32)
        self.direction = self.direction / np.linalg.norm(self.direction)
        self.color = np.array(color)
        # intensities
        self.light_intensity = intensity_config.light
        self.ambient_intensity = intensity_config.ambient
        self.shadow_intensity = intensity_config.shadow
        
        self.shadow_poisson_sampling_denominator = shadow_poisson_sampling_denominator
        self.gamma_correction = gamma_correction
        self.fixed_light_height = fixed_light_height
        self.update_target_position()

    def update_target_position(self, pose=None, target_position=(0, 0, 0)):
        if pose is None:
            target_position = np.array(target_position)
        else:
            pose = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 8],
                [0, 0, 0, 0],
            ]) @ pose
            target_position = -pose[:3, :3].T @ pose[:3, 3]
            target_position[1] = 0

        light_position = (target_position + (self.fixed_light_height / self.direction[1]) * self.direction)
        self.light_position = glm.vec3(*list(light_position.astype(np.float32)))
        self.target_position = glm.vec3(*list(target_position.astype(np.float32)))
        self.m_view_light = self.get_view_matrix()

    def get_sunlight_direction(timestamp: float):
        """Finds sun position relative to our Lat/Lon Origin constants
            at the given UTC seconds timestamp"""
        print("timestamp:", timestamp)
        # Based on figure + code here: https://assessingsolar.org/notebooks/solar_position.html
        date = datetime.datetime.utcfromtimestamp(timestamp)
        loc = pvlib.location.Location(ORIGIN_LATITUDE, ORIGIN_LONGITUDE)
        sun_pose = loc.get_solarposition(date)

        theta, phi = math.radians(sun_pose["zenith"].item()), math.radians(sun_pose["azimuth"].item())

        # Converting spherical coordinates to cartesian
        p = 1 # distance to sun, doesn't matter since we normalize at the end
        x = p * math.sin(theta) * math.sin(phi)
        y = p * math.sin(theta) * math.cos(phi)
        z = p * math.cos(theta)
        print("Initial Sun x,y,z:", [x,y,z])
        direction = np.array([-x,1,y]).astype(np.float32)
        direction = direction / np.linalg.norm(direction)
        print(direction)
        return direction.tolist()

    def get_view_matrix(self):
        return glm.lookAt(self.light_position, self.target_position, glm.vec3(0, 1, 0))