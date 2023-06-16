import os
from .base_actor import Actor
from models.objects import PersonObject
import numpy as np
import glm
import trimesh
from PIL import Image
from pathlib import Path
from constants import T_blender2opengl
from models.utils import get_model_matrix, load_texture
from models.objects.cube import Cube
from models.show import ShowObjects
import moderngl_window as mglw
import time as time_module

class PersonActor(Actor):
    def __init__(self, app, actor_transform, animation_type, frame_step=3):
        super().__init__(app, is_dynamic=True, actor_transform=actor_transform)
        self.animation_type = animation_type
        self.object_id = 0
        self.frame_step = frame_step
        self.objects, self.move_transform = self.load_animation(app, animation_type)

    @property
    def position(self):
        return self.objects[self.move_id].position

    @property 
    def transform_matrix(self):
        return self.objects[self.move_id].transform_matrix
    
    @property
    def move_id(self):
        return self.object_id % len(self.objects)

    def load_animation(self, app, animation_type):
        # walking towards +z axis
        animation_root = os.path.join('assets/human_animations', animation_type)
        tex_path = os.path.join(animation_root, 'texture/rgb.png')
        tex_img = Image.open(tex_path)
        shared_texture = load_texture(app, tex_img)

        objects_dir = os.path.join(animation_root, 'animation')
        animation_objects = sorted([os.path.join(objects_dir, name) for name in os.listdir(objects_dir) if name.endswith('.glb')])
        objects = [
            PersonObject(
                app, 
                self.actor_transform, 
                object_path, 
                shared_texture) for object_path in animation_objects
        ]
        speed_txt = os.path.join(animation_root, 'speed.txt')
        speed = np.loadtxt(speed_txt)
        R = np.array(self.actor_transform)[:3, :3]
        speed = list(R @ speed * self.frame_step)
        move_transform = glm.translate(glm.mat4(), speed)
        return objects, move_transform

    def render(self):
        self.objects[self.move_id].render()

    def render_depth(self, option="from_light"):
        """
        @option: str    choose from ["from_light", "from_fpv"]
        """
        if option == 'from_light':
            self.objects[self.move_id].render_depth(m_view_light=self.app.light.m_view_light,
                                                     m_proj=self.app.camera.m_ortho_proj)
        elif option == 'from_fpv':
            self.objects[self.move_id].render_depth(m_view_light=self.app.camera.m_view,
                                                     m_proj=self.app.camera.m_proj)
        else:
            raise NotImplementedError

    def step(self):
        self.object_id = self.object_id + self.frame_step
        actor_transform_new = self.move_transform * self.actor_transform
        self.actor_transform = actor_transform_new
        self.objects[self.move_id].update_pose(actor_transform_new)
        
    def is_finished(self):
        return False
    
    def reset(self):
        self.object_id = 0

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

        actor_transform = get_model_matrix(
            pos=(-8, 0, -8),
            rot=(0, 0, 0),
            scale=(1, 1, 1)
        )  
        animation_type = 'lady_walking'
        person = PersonActor(self, actor_transform, animation_type, 1)
        self.objects = [person, cube]
    
    def render(self, time, frametime):
        self.ctx.clear(0, 0, 0)

        self.offscreen.clear()
        self.offscreen.use()
        for obj in self.objects:
            obj.render_depth()

        self.wnd.use()
        for obj in self.objects:
            obj.render()

        self.objects[0].step()
        time_module.sleep(0.1)

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()