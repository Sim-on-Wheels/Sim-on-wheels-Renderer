import numpy as np
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

class BusObject(ObjectUV):
    def __init__(self, 
        app,
        m_model
    ):
        object_path = 'assets/objects/bus/bus.glb'
        texture_key = 'legacy-sr2-xhd-prime_Material #35_0'
        super().__init__(app, m_model, object_path, texture_key)
    
    def get_align_matrix(self):
        transform = get_model_matrix(
            pos   = (0, 0, 0),
            rot   = (0, 0, 0),
            scale = (0.007, 0.007, 0.007) 
        )
        return np.array(transform)
class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cam_pos = glm.vec3(5, 5, 5)
        origin = glm.vec3(0, 0, 0)
        up = glm.vec3(0, 1, 0)
        m_view = glm.lookAt(cam_pos, origin, up)
        self.update_camera_pose(m_view)

        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        
        bus = BusObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ))
        self.objects = [bus, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()