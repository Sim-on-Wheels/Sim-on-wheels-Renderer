import numpy as np 
from pathlib import Path
import pywavefront
import math
from pyrr import Matrix44, matrix44, Vector3

import moderngl as mgl
import moderngl_window as mglw
from moderngl_window import geometry
import glm
import rospkg, os, sys
rospack = rospkg.RosPack()
rendering_lib_path = os.path.join(rospack.get_path('hil'), 'src', 'HIL_realtime_rendering')
sys.path.append(rendering_lib_path)
# os.chdir(rendering_lib_path)
from constants import T_blender2opengl
from base import CameraWindow

class ShadowMapping(CameraWindow):
    gl_version = (3, 3)
    window_size = (1280, 720)
    resource_dir = (Path(__file__) / '../../models').resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.camera.projection.update(near=1, far=200)
        self.wnd.mouse_exclusivity = True

        # Offscreen buffer
        offscreen_size = 1024, 1024
        self.offscreen_depth = self.ctx.depth_texture(offscreen_size)
        self.offscreen_depth.compare_func = ''
        self.offscreen_depth.repeat_x = False
        self.offscreen_depth.repeat_y = False
        self.offscreen_color = self.ctx.texture(offscreen_size, 4)

        self.offscreen = self.ctx.framebuffer(
            color_attachments=[self.offscreen_color],
            depth_attachment=self.offscreen_depth,
        )
        
        self.floor = geometry.cube(size=(25.0, 1.0, 25.0))
        self.wall = geometry.cube(size=(1.0, 5, 25), center=(-12.5, 2, 0))
        self.sphere = geometry.sphere(radius=5.0, sectors=64, rings=32)
        self.sun = geometry.sphere(radius=1.0)

        self.basic_light = self.load_program('programs/directional_light.glsl')
        self.basic_light['shadowMap'].value = 0
        self.basic_light['color'].value = 1.0, 1.0, 1.0, 1.0
        self.shadowmap_program = self.load_program('programs/shadowmap.glsl')
        self.texture_prog = self.load_program('programs/texture.glsl')
        self.texture_prog['texture0'].value = 0
        self.sun_prog = self.load_program('programs/cube_simple.glsl')
        self.sun_prog['color'].value = 1, 1, 0, 1

    def render(self, time, frametime):
        self.ctx.clear(0, 0, 0)
        self.lightpos = Vector3((-80.28080582452887, 53.62739968525941, -26.05943627866365,), dtype='f4')
        # self.lightpos = Vector3((math.sin(time) * 20, 5, math.cos(time) * 20), dtype='f4')
        scene_pos = Vector3((0, -5, -32), dtype='f4')

        # --- PASS 1: Render shadow map
        self.offscreen.clear()
        self.offscreen.use()

        depth_projection = Matrix44.orthogonal_projection(-20, 20, -20, 20, -20, 40, dtype='f4')
        depth_view = Matrix44.look_at(self.lightpos, (0, 0, 0), (0, 1, 0), dtype='f4')
        depth_mvp = depth_projection * depth_view
        self.shadowmap_program['mvp'].write(depth_mvp)

        self.floor.render(self.shadowmap_program)
        self.wall.render(self.shadowmap_program)
        self.sphere.render(self.shadowmap_program)

        # --- PASS 2: Render scene to screen
        self.wnd.use()
        self.basic_light['m_proj'].write(self.camera.projection.matrix)
        self.basic_light['m_camera'].write(self.camera.matrix)
        self.basic_light['m_model'].write(Matrix44.from_translation(scene_pos, dtype='f4'))
        bias_matrix = Matrix44(
            [[0.5, 0.0, 0.0, 0.0],
             [0.0, 0.5, 0.0, 0.0],
             [0.0, 0.0, 0.5, 0.0],
             [0.5, 0.5, 0.5, 1.0]],
            dtype='f4',
        )
        self.basic_light['m_shadow_bias'].write(matrix44.multiply(depth_mvp, bias_matrix))
        self.basic_light['lightDir'].write(self.lightpos)
        self.offscreen_depth.use(location=0)
        self.floor.render(self.basic_light)
        self.wall.render(self.basic_light)
        self.sphere.render(self.basic_light)

        # Render the sun position
        self.sun_prog['m_proj'].write(self.camera.projection.matrix)
        self.sun_prog['m_camera'].write(self.camera.matrix)
        self.sun_prog['m_model'].write(Matrix44.from_translation(self.lightpos + scene_pos, dtype='f4'))
        self.sun.render(self.sun_prog)

def main():
    mglw.run_window_config(ShadowMapping)

if __name__ == '__main__':
    main()