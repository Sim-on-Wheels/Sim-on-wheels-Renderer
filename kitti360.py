from argparse import Namespace
import os
from re import X
from matplotlib import pyplot as plt
import glm
import pygame as pg
from constants import SHADOW_CONTRAST
from camera import Camera
from light import Light
import moderngl as mgl
import numpy as np
import moderngl_window as mglw
from dataloader_kitti360 import DataLoader
from models.scenarios import *
from misc.canvas import Background
DEBUG = False
USE_SUNLIGHT_DIR = False
DEFAULT_ARGS = Namespace(
        window='headless',
        fullscreen=False,
        vsync=None,
        resizable=None,
        samples=None,
        cursor=None,
        size=None,
        size_mult=1.0
    )
import torch
from PIL import Image, ImageOps
from omegaconf import OmegaConf, DictConfig, ListConfig
from matplotlib import pyplot as plt

config_path = 'configs/kitti360.yaml'
data_root = 'kitti360'

class HIL_rendering(mglw.WindowConfig):
    gl_version = (3, 3)
    aspect_ratio = 1408/376
    window_size = (1408, 376)
    def __init__(self, using_ros, custom_config, **kwargs):
        super().__init__(**kwargs)
        self.config = custom_config
        self.window_size = tuple(self.config.window_size)

        self.using_ros = using_ros

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.device = self.config.device

        # Offscreen buffer
        self.create_offscreen_buffer()

        # light
        self.light = Light(**self.config.light_config)
        # camera
        self.camera = Camera(self)

        self.scenarios = self.load_scenarios()
        self.world_scenario = self.load_world()
        # self.scenarios.append(self.world_scenario)

        # TODO: bhargav, this needs to replace by ros input
        self.dataloader = DataLoader(
            root_dir=data_root,
            frame_start=self.config.kitti.frame_start,
            frame_end=self.config.kitti.frame_end,
            debug=DEBUG, 
            window_size=self.window_size)
        self.sensor_data = None
        # TODO: only necessary for visualization purpose. can be commented out during production mode
        self.background = Background(self)

        self.clock = pg.time.Clock()
        self.i = 0

    def load_world(self):
        return WorldScenario(self, self.config.scenario_configs.world)

    def load_scenarios(self):
        res = []
        if self.config.scenario_configs.intersection.is_activated:
            res.append(IntersectionScenario(self, self.config.scenario_configs.intersection))
        if self.config.scenario_configs.jaywalking.is_activated:
            res.append(JaywalkingScenario(self, self.config.scenario_configs.jaywalking))
        if self.config.scenario_configs.static_objects.is_activated:
            res.append(StaticObjectScenario(self, self.config.scenario_configs.static_objects))

        return res

    def render_single_frame(self, sensor_data):
        """
        Render background first then compose objects, should be easier to integrate with anti-aliasing 
        but currently generates strange patterns in images. 
        Returns virtual depth and composited rgb after rendering if using ros
        """
        dir_origin, dir_insert = self.render_folders()
        m_view = glm.mat4(*list(np.array(sensor_data['pose']).T.astype(np.float32).flatten()))
        self.camera.m_view = m_view
        self.light.update_target_position(m_view)
        image_bg = (sensor_data['rgb'] * 255).astype(np.uint8)
        self.background.update_texture(Image.fromarray(image_bg))
        for scenario in self.scenarios:
            scenario.update()
        for scenario in self.scenarios:
            scenario.render()
        img_gt = self.take_screenshot()
        img_gt.save(os.path.join(dir_origin, '{:0>5d}.png'.format(self.dataloader.start_frame + self.i)))
        self.ctx.clear(0, 0, 0)
        self.offscreen.clear()
        self.wnd.use()
        self.background.render()
        # img_origin = self.take_screenshot()
        # img_origin.save(os.path.join(dir_origin, '{:0>5d}.png'.format(self.i)))

        for scenario in self.scenarios:
            scenario.render()
        no_ground = np.array(self.take_screenshot())
        no_ground = torch.from_numpy(no_ground).to(self.device).float() / 255

        # render plane, no shadow pass
        self.world_scenario.render_plane()
        no_shadow = np.array(self.take_screenshot())
        no_shadow = torch.from_numpy(no_shadow).to(self.device).float() / 255

        # shadow pass
        self.ctx.clear(0, 0, 0)
        self.render_depth('from_light')     # from light direction
        self.wnd.use()
        self.background.render()
        self.world_scenario.render_plane()
        for scenario in self.scenarios:
            scenario.render()

        with_shadow = np.array(self.take_screenshot())
        with_shadow = torch.from_numpy(with_shadow).to(self.device).float() / 255


        # final = background + foreground + shadow
        shadow = (with_shadow - no_shadow) * SHADOW_CONTRAST
        composited_rgb = no_ground + shadow
        composited_rgb = torch.clip(composited_rgb, 0, 1).cpu().numpy()
        
        img_path = os.path.join(dir_insert, '{:0>5d}.png'.format(self.dataloader.start_frame + self.i))
        plt.imsave(img_path, composited_rgb)
        # render scene on window
        self.ctx.clear(0, 0, 0)
        self.wnd.use()
        im_flip = Image.fromarray((composited_rgb * 255.).astype(np.uint8))
        self.background.update_texture(im_flip)
        self.background.render()
        return None

    def render_folders(self):
        dir_origin = os.path.join('outputs/kitti360/', self.config.name, 'gt')
        dir_insert = os.path.join('outputs/kitti360/', self.config.name, 'insert')
        os.makedirs(dir_origin, exist_ok=True)
        os.makedirs(dir_insert, exist_ok=True)
        config_path = 'configs/kitti360.yaml'
        # os.system('cp {} {}'.format(config_path, os.path.join('outputs/kitti360/', self.config.name)))
        return dir_origin, dir_insert

    def get_primary_obstacle_positions(self):
        """Assumes first index of self.scenarios contains the primary obstacle"""
        return self.scenarios[0].get_primary_obstacle_positions()

    def render(self, time, frame_time):
        if not self.using_ros:
            # quit if it runs out of data
            if self.i >= len(self.dataloader):
                # quit()
                # super().close()
                # cleanup_window_config(self, self.timer)
                return
            self.sensor_data = next(self.dataloader)

        self.render_single_frame(
            self.sensor_data
        )
        self.i += 1
        if not DEBUG:
            self.clock.tick(24)
        if time != 0:
            print('frame {}, FPS = {}, time: {}'.format(self.i, self.i / time, time))

    def take_screenshot(self):
        return Image.frombytes('RGB', self.window_size, self.wnd.fbo.read(), 'raw', 'RGB', 0, -1) #.show()

    def visualize_offscreen_buffer(self):
        depth = torch.from_numpy(np.frombuffer(self.offscreen_depth.read(), dtype=np.dtype('f4'))).to(self.device)
        normalized_depth = torch.flip(depth.reshape(self.window_size[1], self.window_size[0]), [0])
        plt.imshow(normalized_depth)
        plt.show()

    def render_depth(self, option):
        self.offscreen.clear()
        self.offscreen.use()
        self.world_scenario.render_depth(option)
        for scenario in self.scenarios:
            scenario.render_depth(option)

    def get_fpv_depth(self):
        self.render_depth("from_fpv")  # from first-person view
        depth = np.frombuffer(self.offscreen_depth.read(), dtype=np.dtype('f4')).copy()
        depth = torch.from_numpy(depth).to(self.device)
        normalized_depth = torch.flip(depth.reshape(self.window_size[1], self.window_size[0]), [0])

        zNorm = 2 * normalized_depth - 1
        virtual_depth = -(2 * self.config.camera_config.near * self.config.camera_config.far /
                          ((self.config.camera_config.far - self.config.camera_config.near) * zNorm -
                           self.config.camera_config.near - self.config.camera_config.far))
        return virtual_depth

    def create_offscreen_buffer(self):
        offscreen_size = self.window_size
        self.offscreen_depth = self.ctx.depth_texture(offscreen_size)
        self.offscreen_depth.compare_func = ''
        self.offscreen_depth.repeat_x = False
        self.offscreen_depth.repeat_y = False
        self.offscreen = self.ctx.framebuffer(depth_attachment=self.offscreen_depth)

def show_tensor(tensor):
    img = (tensor.cpu().numpy() * 255.).astype(np.uint8)
    plt.axis('off')
    plt.imshow(img)
    plt.show()
    plt.close()

def show_array(array):
    plt.axis('off')
    plt.imshow(array)
    plt.show()
    plt.close()

def setup_window_config(config_cls: mglw.WindowConfig, values: Namespace, using_ros: bool, custom_config):
    mglw.setup_basic_logging(config_cls.log_level)
    window_cls = mglw.get_local_window_cls(values.window)

    # Calculate window size
    size = values.size or custom_config.window_size
    size = int(size[0] * values.size_mult), int(size[1] * values.size_mult)

    # Resolve cursor
    show_cursor = values.cursor
    if show_cursor is None:
        show_cursor = config_cls.cursor

    window = window_cls(
        title=config_cls.title,
        size=size,
        fullscreen=config_cls.fullscreen or values.fullscreen,
        resizable=values.resizable
        if values.resizable is not None
        else config_cls.resizable,
        gl_version=config_cls.gl_version,
        aspect_ratio=config_cls.aspect_ratio,
        vsync=values.vsync if values.vsync is not None else config_cls.vsync,
        samples=values.samples if values.samples is not None else config_cls.samples,
        cursor=show_cursor if show_cursor is not None else True,
    )
    window.print_context_info()
    mglw.activate_context(window=window)

    timer = mglw.Timer()
    config_obj = config_cls(using_ros, custom_config, ctx=window.ctx, wnd=window, timer=timer)
    # Avoid the event assigning in the property setter for now
    # We want the even assigning to happen in WindowConfig.__init__
    # so users are free to assign them in their own __init__.
    window._config = mglw.weakref.ref(config_obj)

    # Swap buffers once before staring the main loop.
    # This can trigged additional resize events reporting
    # a more accurate buffer size
    window.swap_buffers()
    window.set_default_viewport()
    return window, config_obj, timer

def cleanup_window_config(window, timer):
    _, duration = timer.stop()
    print("Cleanup")
    window.destroy()
    if duration > 0:
        mglw.logger.info(
            "Duration: {0:.2f}s @ {1:.2f} FPS".format(
                duration, window.frames / duration
            )
        )

def custom_run_window_config(custom_config: DictConfig, config_cls: mglw.WindowConfig, values: Namespace, timer=None, args=None) -> None:
    """
    Initially based on from https://moderngl-window.readthedocs.io/en/latest/_modules/moderngl_window.html#run_window_config
    Run an WindowConfig entering a blocking main loop

    Args:
        config_cls: The WindowConfig class to render
        values: argument values
    Keyword Args:
        window_name
        timer: A custom timer instance
        args: Override sys.args
    """
    using_ros = False
    window, config_obj, timer = setup_window_config(config_cls, values, using_ros, custom_config)

    timer.start()

    while not window.is_closing and config_obj.i < len(config_obj.dataloader):
        current_time, delta = timer.next_frame()

        if config_obj.clear_color is not None:
            window.clear(*config_obj.clear_color)

        # Always bind the window framebuffer before calling render
        window.use()

        window.render(current_time, delta)
        if not window.is_closing:
            window.swap_buffers()
    cleanup_window_config(window, timer)

def ros_custom_run(config_cls: mglw.WindowConfig):
    custom_run_window_config(config_cls, DEFAULT_ARGS)

if __name__ == '__main__':
    config_cls = HIL_rendering
    parser = mglw.create_parser()
    config_cls.add_arguments(parser)
    values = mglw.parse_args(args=None, parser=parser)
    config_cls.argv = values
    custom_config = OmegaConf.load(config_path)
    custom_run_window_config(custom_config, config_cls, values)
    # mglw.run_window_config(HIL_rendering)
