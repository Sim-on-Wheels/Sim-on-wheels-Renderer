import numpy as np 
import trimesh

import moderngl as mgl
import moderngl_window as mglw
import glm
from omegaconf import OmegaConf

from light import Light
from camera import Camera
from models.utils import get_model_matrix, load_texture
from models.objects.base_object_pbr import ObjectAlbedo, ObjectUV
from models.objects.cube import Cube
from models.show import ShowObjects

class TrafficLightPart(ObjectUV):
    def __init__(self, 
        app,
        m_model,
        object_path = 'assets/objects/traffic_lights/traffic_lights.glb',
        texture_key = '',
    ):  
        glb = self.load_glb_file(object_path)
        mesh = glb.geometry[texture_key]
        self.mat_name = mesh.visual.material.name
        super().__init__(app, m_model, object_path, texture_key)

    def should_contain(self, name, mesh):
        mat = mesh.visual.material
        if mat.name == self.mat_name:
            return True
        else:
            return False

class Signal(ObjectAlbedo):
    def __init__(self, 
        app,
        m_model,
        object_path= 'assets/objects/traffic_lights/lights_0.glb'
    ):
        super().__init__(app, m_model, object_path)

class TrafficLightObject:
    def __init__(self, 
        app, 
        m_model
    ):
        object_path= 'assets/objects/traffic_lights/traffic_lights.glb'
        self.pole = TrafficLightPart(
            app, m_model, object_path, texture_key = 'defaultMaterial',
        )
        self.lights = TrafficLightPart(
            app, m_model, object_path, texture_key = 'defaultMaterial.001',
        )
        self.signal_0 = Signal(
            app, m_model, object_path='assets/objects/traffic_lights/lights_0.glb'
        )
        self.signal_1 = Signal(
            app, m_model, object_path='assets/objects/traffic_lights/lights_1.glb'
        )

        self.signal_id = 0
        self.change_signal()

    @property
    def position(self):
        return self.pole.position

    @property
    def transform_matrix(self):
        return self.pole.transform_matrix
    
    def update_pose(self, m_model):
        for obj in [self.pole, self.lights, self.signal_0, self.signal_1]:
            obj.update_pose(m_model)
        
    def change_signal(self):
        self.signal_id = 1 - self.signal_id

    def render(self):
        self.pole.render()
        self.lights.render()
        if self.signal_id == 0:
            self.signal_0.render()
        else:
            self.signal_1.render()

    def render_depth(self, m_view_light=None, m_proj=None):
        self.pole.render_depth(m_view_light, m_proj)
        self.lights.render_depth(m_view_light, m_proj)
        if self.signal_id == 0:
            self.signal_0.render_depth(m_view_light, m_proj)
        else:
            self.signal_1.render_depth(m_view_light, m_proj)


class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cam_pos = glm.vec3(7, 7, 7)
        origin = glm.vec3(0, 0, 0)
        up = glm.vec3(0, 1, 0)
        m_view = glm.lookAt(cam_pos, origin, up)
        self.update_camera_pose(m_view)

        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        traffic_light = TrafficLightObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1.0, 1.0, 1.0)
        ))
        traffic_light.change_signal()
        self.objects = [cube, traffic_light]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()