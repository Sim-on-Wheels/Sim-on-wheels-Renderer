import os
import numpy as np 
import trimesh

import moderngl as mgl
import moderngl_window as mglw
import glm
from omegaconf import OmegaConf

from light import Light
from camera import Camera
from models.utils import get_model_matrix
from models.objects.base_object_pbr import ObjectConst
from models.objects.cube import Cube
from models.show import ShowObjects

class BenzObject(ObjectConst):
    def __init__(self, 
        app,
        m_model
    ):
        object_path = 'assets/objects/benz/benz.glb'
        default_albedo = [0, 0, 0]
        default_metallic = 1.0
        default_roughness = 0.4
        super().__init__(app, m_model, object_path, 
            default_albedo, default_metallic, default_roughness) 
    
    def get_align_matrix(self):
        transform = get_model_matrix(
            pos   = (0, 0, 0),
            rot   = (0, 0, 0),
            scale = (1.5, 1.5, 1.5) 
        )
        return np.array(transform)


class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        benz = BenzObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ))
        self.objects = [benz, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()