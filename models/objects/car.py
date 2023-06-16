import numpy as np
import moderngl as mgl
import moderngl_window as mglw

from models.utils import get_model_matrix
from models.objects.base_object_pbr import ObjectConst, ObjectUV
from models.objects.cube import Cube
from models.show import ShowObjects

class CarExt(ObjectUV):
    def __init__(self, 
        app,
        m_model,
        object_path = 'assets/objects/car-suv/car.glb'
    ):  
        texture_key = 'Body_Body_0'
        super().__init__(app, m_model, object_path, texture_key)

    def should_contain(self, name, mesh):
        if 'Shadow' in name:
            return False
        mat = mesh.visual.material
        if mat.baseColorTexture is None:
            return False
        return True

class CarInt(ObjectConst):
    def __init__(self, 
        app,
        m_model,
        object_path = 'assets/objects/car-suv/car.glb'
    ):  
        default_albedo = [0, 0, 0]
        default_metallic = 0.0
        default_roughness = 1.0
        super().__init__(app, m_model, object_path, 
            default_albedo, default_metallic, default_roughness) 

    def should_contain(self, name, mesh):
        if 'Shadow' in name or 'Glass' in name:
            return False
        mat = mesh.visual.material
        if mat.baseColorTexture is not None:
            return False
        return True

class CarObject:
    def __init__(self, 
        app,
        m_model
    ):
        object_path = 'assets/objects/car-suv/car.glb'
        self.car_int = CarInt(app, m_model, object_path)
        self.car_ext = CarExt(app, m_model, object_path)
    
    @property
    def position(self):
        return self.car_ext.position

    @property 
    def transform_matrix(self):
        return self.car_ext.transform_matrix

    def update_pose(self, m_model):
        self.car_int.update_pose(m_model)
        self.car_ext.update_pose(m_model)
    
    def render(self):
        self.car_int.render()
        self.car_ext.render()
    
    def render_depth(self, m_view_light=None, m_proj=None):
        self.car_int.render_depth(m_view_light, m_proj)
        self.car_ext.render_depth(m_view_light, m_proj)

class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        car_pbr = CarObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ))
        self.objects = [car_pbr, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()