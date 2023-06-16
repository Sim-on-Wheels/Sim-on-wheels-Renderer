import numpy as np
import pywavefront
import trimesh 
import moderngl as mgl
import moderngl_window as mglw
import glm
from omegaconf import OmegaConf

from light import Light
from camera import Camera
from models.utils import get_model_matrix
from models.objects.base_object_pbr import ObjectUV
from models.objects.cube import Cube
from models.show import ShowObjects
from PIL import Image
from models.utils import load_texture
from misc.canvas import Background

class ConeObject(ObjectUV):
    def __init__(self, 
        app,
        m_model,
    ):  
        object_path = 'assets/objects/cone/cone.glb'
        texture_key = 'defaultMaterial.022'
        super().__init__(app, m_model, object_path, texture_key)

class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        m_model = get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        )
        cone = ConeObject(self, m_model)
        self.objects = [cone, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()