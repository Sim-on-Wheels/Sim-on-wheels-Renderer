import numpy as np
import trimesh 
import moderngl as mgl
import moderngl_window as mglw

from models.utils import get_model_matrix
from models.objects.base_object_pbr import ObjectConst, ObjectUVConstMR
from models.objects.cube import Cube
from models.show import ShowObjects

class BabySkin(ObjectUVConstMR):
    def __init__(self, 
        app, 
        m_model,
        transform,
        object_path = 'assets/objects/baby/baby.glb'
    ):  
        self.transform = np.array(transform)
        texture_key = 'Object_0'
        default_metallic = 0.0
        default_roughness = 1.0
        super().__init__(app, m_model, object_path, texture_key, 
            default_metallic, default_roughness)

    def should_contain(self, name, mesh):
        mat = mesh.visual.material
        if mat.baseColorTexture is None:
            return False
        return True
    
    def get_align_matrix(self):
        return self.transform

class BabyCloth(ObjectConst):
    def __init__(self, 
        app,
        m_model,
        transform,
        object_path = 'assets/objects/baby/baby.glb',
    ):  
        self.transform = np.array(transform)
        default_albedo = np.array([0, 0, 0])
        default_metallic = 0.0
        default_roughness = 1.0
        super().__init__(app, m_model, object_path, 
            default_albedo, default_metallic, default_roughness) 

    def should_contain(self, name, mesh):
        mat = mesh.visual.material
        if mat.baseColorTexture is None:
            return True
        return False

    def get_align_matrix(self):
        return self.transform

class BabyObject:
    def __init__(self, 
        app,
        m_model 
    ):
        object_path = 'assets/objects/baby/baby.glb'
        # center = [0, 86.18, -135.2]
        center = get_model_matrix(pos = (0, -86.18, 135.2))
        align = get_model_matrix(
            pos   = (0, 0.8, 0),
            rot   = (0, 30, 0),
            scale = (0.01, 0.01, 0.01)
        )
        transform = np.array(align) @ np.array(center)

        self.baby_skin = BabySkin(app, m_model, transform, object_path)
        self.baby_cloth = BabyCloth(app, m_model, transform, object_path)
    
    @property
    def position(self):
        return self.baby_skin.position

    @property 
    def transform_matrix(self):
        return self.baby_skin.transform_matrix
    
    def update_pose(self, m_model):
        self.baby_skin.update_pose(m_model)
        self.baby_cloth.update_pose(m_model)

    def render(self):
        self.baby_skin.render()
        self.baby_cloth.render()
    
    def render_depth(self, m_view_light=None, m_proj=None):
        self.baby_skin.render_depth(m_view_light, m_proj)
        self.baby_cloth.render_depth(m_view_light, m_proj)

class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        baby = BabyObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ))
        self.objects = [baby, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()