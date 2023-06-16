import numpy as np
import moderngl as mgl
import moderngl_window as mglw

from models.utils import get_model_matrix
from models.objects.base_object_pbr import ObjectUV
from models.objects.cube import Cube
from models.show import ShowObjects

class BuildingObject(ObjectUV):
    def __init__(self, 
        app,
        m_model
    ):  
        object_path = 'assets/objects/building/old_buildings.glb'
        texture_key = 'unnamed_unnamed_0'
        super().__init__(app, m_model, object_path, texture_key)

    def should_contain(self, name, mesh):
        if name == 'unnamed_unnamed_0':
            return True
        else:
            return False
    
    def get_align_matrix(self):
        matrix = get_model_matrix(
            pos=(0, 0, 0),
            rot=(0, 0, 0),
            scale=(0.03, 0.03, 0.03)
        )
        return np.array(matrix)

class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        building = BuildingObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ))
        self.objects = [building, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()