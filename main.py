from argparse import Namespace
import os
from re import X

import glm
import pygame as pg
from constants import SHADOW_CONTRAST
from camera import Camera
from light import Light
import moderngl as mgl
import numpy as np
import moderngl_window as mglw
from dataloader import DataLoader
from models.scenarios import *
from misc.canvas import Background
DEBUG = True
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
from omegaconf import OmegaConf
from matplotlib import pyplot as plt

config_path = "configs/exp_2/scen_1/path.yaml"
# config = OmegaConf.load(f"configs/{'debug' if DEBUG else 'production'}.yaml")
# config = OmegaConf.load(f"configs/debug.yaml")
data_root = 'ros_sequences/outdoor1_rgb_depth_sync'
# data_root = 'ros_sequences/static_path_1'
# data_root = 'ros_sequences/jaywalker'

class HIL_rendering(mglw.WindowConfig):
    gl_version = (3, 3)
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
        world_scenario = self.load_world()
        self.scenarios.append(world_scenario)

        # TODO: bhargav, this needs to replace by ros input
        if not using_ros:
            self.dataloader = DataLoader(root_path=data_root, debug=DEBUG, window_size=self.window_size)
            if USE_SUNLIGHT_DIR:
                sun_direction = Light.get_sunlight_direction(self.dataloader.start_timestamp)
                self.config.light_config.direction = sun_direction
                self.light = Light(**self.config.light_config)
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
        """Returns virtual depth and composited rgb after rendering if using ros"""
        m_view = glm.mat4(*list(np.array(sensor_data['pose']).T.astype(np.float32).flatten()))
        self.camera.m_view = m_view
        self.light.update_target_position(m_view)
        # self.camera.update()

        for scenario in self.scenarios:
            scenario.update()

        self.ctx.clear(0, 0, 0)
        self.offscreen.clear()
        self.wnd.use()
        for scenario in self.scenarios[:-1]:
            scenario.render()

        no_ground_without_building = self.take_screenshot()
        self.scenarios[-1].actors[0].render()
        no_ground_with_building = self.take_screenshot()
        building_mask = np.array(no_ground_without_building).sum(-1, keepdims=True) == np.array(no_ground_with_building).sum(-1, keepdims=True)
        buffer = no_ground_without_building * building_mask

        # mask = torch.from_numpy(np.array(buffer.convert("L")) < 1).to(self.device)[..., None]
        no_ground = torch.from_numpy(np.array(buffer)).to(self.device).float() / 255

        # render cube, no shadow pass
        self.scenarios[-1].render()
        no_shadow = torch.from_numpy(np.array(self.take_screenshot())).to(self.device).float() / 255

        self.ctx.clear(0, 0, 0)
        self.render_depth('from_light')     # from light direction
        # self.visualize_offscreen_buffer()

        self.wnd.use()
        for scenario in self.scenarios:
            scenario.render()
        shadow = torch.from_numpy(np.array(self.take_screenshot())).to(self.device).float() / 255
        
        # final render for depth
        virtual_depth = self.get_fpv_depth() # TODO: This variable gives virtual depth of virtual scene, might be helpful for albert
        if self.config.use_depth_occlusion:
            # virtual_mask = (no_ground.sum(-1, keepdims=True) != 0) * (
            #             virtual_depth < torch.nan_to_num(torch.from_numpy(sensor_data['depth']), torch.inf).to(
            #         self.device))[..., None]
            virtual_mask = (no_ground.sum(-1, keepdims=True) != 0) * (
                        virtual_depth < torch.from_numpy(np.nan_to_num(sensor_data['depth'], nan=np.inf, posinf=np.inf, neginf=np.inf)).to(
                    self.device))[..., None]
        else:
            virtual_mask = (no_ground.sum(-1, keepdims=True) != 0)

        # final = background + foreground + shadow
        composite = torch.from_numpy(sensor_data['rgb'] if sensor_data is not None else self.realworld_background).to(
            self.device) * ~virtual_mask + no_ground * virtual_mask + (shadow - no_shadow) * SHADOW_CONTRAST

        # depth_mask = (virtual_depth.cpu().numpy() < self.config.camera_config.far) * (virtual_depth.cpu().numpy() < sensor_data['depth'])
        #
        # composite_depth = np.nan_to_num(sensor_data['depth'], nan=self.config.camera_config.far,
        #                                 posinf=self.config.camera_config.far,
        #                                 neginf=self.config.camera_config.far) * ~depth_mask + depth_mask * virtual_depth.cpu().numpy()

        # TODO: bhargav, this is the output from inserting virtual scene on top of real world scene. probably need to publish this as a ros topic
        composited_rgb = torch.clip(composite, 0, 1).cpu().numpy()
        # print(self.get_primary_obstacle_position())
        # if not self.using_ros:
        #     img_path = os.path.join(data_root, 'outputs/{:0>5d}.png'.format(self.i))
        #     plt.imsave(img_path, composited_rgb)
        if self.using_ros:
            return composited_rgb, virtual_depth, self.get_primary_obstacle_positions()

        # render scene on window
        self.wnd.use()
        self.ctx.clear(0, 0, 0)
        self.background.render()
        im_flip = Image.fromarray((composited_rgb * 255.).astype(np.uint8))
        self.background.update_texture(im_flip)
        return None

    def get_primary_obstacle_positions(self):
        """Assumes first index of self.scenarios contains the primary obstacle"""
        return self.scenarios[0].get_primary_obstacle_positions()

    def render(self, time, frame_time):
        if not self.using_ros:
            # quit if it runs out of data
            if self.dataloader.i == len(self.dataloader):
                quit()
            # skip frames to match real timestamps of incoming ros messages
            while self.dataloader.timestamps[self.dataloader.i] < time:
                self.dataloader.i += 1
            self.sensor_data = next(self.dataloader)

        self.render_single_frame(
            self.sensor_data
        )
        self.i += 1
        if not DEBUG:
            self.clock.tick(24)

        print('frame {}, FPS = {}, time: {}, rostime: {}'.format(self.i, self.i / time, time, self.dataloader.timestamps[self.dataloader.i]))

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
        for scenario in self.scenarios:
            scenario.render_depth(option)

    def get_fpv_depth(self):
        self.render_depth("from_fpv")  # from first-person view
        depth = torch.from_numpy(np.frombuffer(self.offscreen_depth.read(), dtype=np.dtype('f4'))).to(self.device)
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
    window.destroy()
    if duration > 0:
        mglw.logger.info(
            "Duration: {0:.2f}s @ {1:.2f} FPS".format(
                duration, window.frames / duration
            )
        )

def custom_run_window_config(config_cls: mglw.WindowConfig, values: Namespace, timer=None, args=None) -> None:
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
    custom_config = OmegaConf.load(config_path)
    window, config_obj, timer = setup_window_config(config_cls, values, using_ros, custom_config)

    timer.start()

    while not window.is_closing:
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
    os.makedirs(os.path.join(data_root, 'outputs'), exist_ok=True)
    config_cls = HIL_rendering
    parser = mglw.create_parser()
    config_cls.add_arguments(parser)
    values = mglw.parse_args(args=None, parser=parser)
    config_cls.argv = values
    custom_run_window_config(config_cls, values)
    # mglw.run_window_config(HIL_rendering)
