import numpy as np
import glm
import pywavefront
import trimesh
import moderngl_window as mglw
from models.objects.base_object import BaseObject
from models.objects.base_object_pbr import ObjectUVConstMR
from models.objects.cube import Cube
from models.show import ShowObjects
from models.utils import get_model_matrix, load_texture
from pathlib import Path

class PersonObject(ObjectUVConstMR):
    def __init__(self,
        app,
        m_model,
        object_path, 
        shared_texture=None
    ):
        self.shared_texture = shared_texture
        texture_key = 'Mesh'
        default_metallic = 0.0
        default_roughness = 1.0
        super().__init__(app, m_model, object_path, texture_key, 
            default_metallic, default_roughness)
    
    def initialize_texture(self):
        self.object_prog['shadowMap'] = 0
        self.app.offscreen_depth.use(location=0)

        if self.shared_texture == None:
            glb = self.load_glb_file(self.object_path)
            mesh = glb.geometry[self.texture_key]
            mat = mesh.visual.material
            self.tex_rgb = load_texture(self.app, mat.baseColorTexture)
        else:
            self.tex_rgb = self.shared_texture
        self.object_prog['u_rgb'] = 1
        self.tex_rgb.use(location=1)
class Show(ShowObjects):
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        cube = Cube(self, get_model_matrix(
            pos   = (0, -1, 0), 
            rot   = (0, 0, 0), 
            scale = (30, 1, 30)
        ))
        index = 20
        path = 'assets/baked_animations/woman_walking/animation/{:0>5d}.glb'.format(index)
        person = PersonObject(self, get_model_matrix(
            pos   = (0, 0, 0), 
            rot   = (0, 0, 0), 
            scale = (1, 1, 1)
        ), path)
        self.objects = [person, cube]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()