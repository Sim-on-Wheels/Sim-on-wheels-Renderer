import numpy as np
import torch
import moderngl as mgl
import moderngl_window as mglw
import glm
from omegaconf import OmegaConf
from PIL import Image
from matplotlib import pyplot as plt

from light import Light
from camera import Camera

class ShowObjects(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (1280, 720)

    def __init__(self, config='configs/debug.yaml', **kwargs):
        super().__init__(**kwargs)
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.create_offscreen_buffer()
        self.config = OmegaConf.load(config)
        
        self.light = Light(**self.config.light_config)
        self.camera = Camera(self)
        cam_pos = glm.vec3(3, 3, 3)
        origin = glm.vec3(0, 0, 0)
        up = glm.vec3(0, 1, 0)
        m_view = glm.lookAt(cam_pos, origin, up)
        self.camera.m_view = m_view
        self.objects = []

    def update_camera_pose(self, pose):
        self.camera.m_view = pose

    def update_light_pose(self, pose):
        self.light.m_view_light = pose 

    def create_offscreen_buffer(self):
        offscreen_size = self.window_size
        self.offscreen_depth = self.ctx.depth_texture(offscreen_size)
        self.offscreen_depth.compare_func = ''
        self.offscreen_depth.repeat_x = False
        self.offscreen_depth.repeat_y = False
        self.offscreen = self.ctx.framebuffer(depth_attachment=self.offscreen_depth)
    
    def take_screenshot(self):
        return Image.frombytes('RGB', self.window_size, self.wnd.fbo.read(), 'raw', 'RGB', 0, -1) #.show()

    def visualize_offscreen_buffer(self):
        depth = torch.from_numpy(np.frombuffer(self.offscreen_depth.read(), dtype=np.dtype('f4')))
        normalized_depth = torch.flip(depth.reshape(self.window_size[1], self.window_size[0]), [0])
        plt.imshow(normalized_depth)
        plt.show()

    def render(self, time, frametime):
        self.ctx.clear(0, 0, 0)

        self.offscreen.clear()
        self.offscreen.use()
        for obj in self.objects:
            obj.render_depth()

        self.wnd.use()
        for obj in self.objects:
            obj.render()
    
    