import numpy as np
import trimesh 
import moderngl as mgl
import moderngl_window as mglw
import glm
from omegaconf import OmegaConf

from light import Light
from camera import Camera
from models.utils import get_model_matrix, load_texture
from models.objects.base_object_pbr import ObjectUVConstMR
from models.objects.cube import Cube
from models.show import ShowObjects
class ScannedObject(ObjectUVConstMR):
    def __init__(self, 
        app, 
        name,
        m_model
    ):  
        object_path = 'assets/objects/scanned/{}.glb'.format(name)
        texture_key = 'mesh'
        default_metallic = 0.0
        default_roughness = 1.0
        super().__init__(app, m_model, object_path, texture_key, 
            default_metallic, default_roughness)

class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        obj = ScannedObject(self, 'albert', get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ))
        self.objects = [cube, obj]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()