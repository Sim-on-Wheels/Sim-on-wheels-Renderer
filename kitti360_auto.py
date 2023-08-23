import numpy as np
from omegaconf import OmegaConf, DictConfig
from kitti360 import HIL_rendering, custom_run_window_config, DEFAULT_ARGS
import moderngl_window as mglw
BASE_KITTI_CONFIG_PATH = 'configs/kitti360_base.yaml'

ORIG_ANIM = ['lady_running', 'lady_walking', \
            'man_running', 'man_walking', \
            'woman_running', 'woman_walking' \
        ]
def gen_random_actor_cfg(n_actors: int):
    # actor_configs:
    # actor_0:
    #     animation_type: woman_walking
    #     object2scenario: 
    #       pos:   [-1.0, 0.0, 5.0] # in ego-vehicle coords, x is left -right of ego, y up-down, z is how far away
    #       rot:   [0.0, 180, 0.0]
    #       scale: [2.5, 2.5, 2.5]
    cfg = {}
    for i in range(n_actors):
        id = 'actor_' + repr(i)
        anim_types = [  
            'roth', 'martha', \
            'walking28', 'pete', \
            'walking23', 'alex', \
            'walking26', 'suzie', \
            'walking2', 'walking33', \
            'walking22', 'walking31', \
            'walking7', 'walking8', \
            'lady_running', 'lady_walking', \
            'man_running', 'man_walking', \
            'woman_running', 'woman_walking' \
        ]
        animation_type =  str(np.random.choice(anim_types).item())
        print(animation_type)
        x_val = np.random.uniform(-10.0, 5.0) # ranges based on kitti sidewalk limits
        if (animation_type not in ORIG_ANIM):
            x_val = np.random.uniform(-8.0, 3.0)
        z_val = np.random.uniform(4.0, 20.0)
        y_val = 0.0
        if (animation_type == 'walking7'):
            y_val = -0.1
        pos = [x_val, y_val, z_val]
        rot_angle = np.random.uniform(0, 360)
        if animation_type in ORIG_ANIM:
            if x_val < -2.5: # actor to the left of the car --> make angle so that actor faces right
                rot_angle = np.random.uniform(30, 150)
            else:
                rot_angle = np.random.uniform(-150, -45)
        rot = [0.0, rot_angle, 0.0]
        scale = [2.5, 2.5, 2.5]

    
        cfg[id] = {
                'animation_type': animation_type,
                'object2scenario': {
                    'pos' : pos,
                    'rot' : rot,
                    'scale' : scale
                }
            }
    print(cfg)
    return cfg

def auto_gen_kitti_config(frame_start) -> DictConfig:
    base_cfg = OmegaConf.load(BASE_KITTI_CONFIG_PATH)
    if np.random.random() > 0.7:
        actor_gen = gen_random_actor_cfg(np.random.randint(2, 6))
    else:
        actor_gen = gen_random_actor_cfg(np.random.randint(1, 3))
    base_cfg.scenario_configs.jaywalking.actor_configs = actor_gen
    base_cfg.scenario_configs.jaywalking.trigger_distance = np.random.uniform(10.0, 20.0)
    print(base_cfg.scenario_configs.jaywalking.actor_configs)
    base_cfg.kitti.frame_start = frame_start
    base_cfg.kitti.frame_end = frame_start + 20
    base_cfg.name = 'kitti-sow-dataset3' #'ped-' + repr(frame_start)+ '-' + repr(frame_start + 20)
    base_cfg.light_config.intensity_config.light = 7.0
    base_cfg.light_config.intensity_config.gamma_correction = 1.7
    base_cfg.device = 'cuda'
    print(base_cfg.display)
    base_cfg.display = 'headless'
    return base_cfg

if __name__ == '__main__':
    for i in range(1540, 5350, 20):
        custom_config = auto_gen_kitti_config(frame_start=i)
        config_cls = HIL_rendering
        parser = mglw.create_parser()
        config_cls.add_arguments(parser)
        values = mglw.parse_args(args=None, parser=parser)
        config_cls.argv = values
        values = DEFAULT_ARGS
        custom_run_window_config(custom_config, config_cls, values)
    for i in range(5900, 9040, 20):
        custom_config = auto_gen_kitti_config(frame_start=i)
        config_cls = HIL_rendering
        parser = mglw.create_parser()
        config_cls.add_arguments(parser)
        values = mglw.parse_args(args=None, parser=parser)
        config_cls.argv = values
        values = DEFAULT_ARGS
        custom_run_window_config(custom_config, config_cls, values)
    for i in range(9500, 11460, 20):
        custom_config = auto_gen_kitti_config(frame_start=i)
        config_cls = HIL_rendering
        parser = mglw.create_parser()
        config_cls.add_arguments(parser)
        values = mglw.parse_args(args=None, parser=parser)
        config_cls.argv = values
        values = DEFAULT_ARGS
        custom_run_window_config(custom_config, config_cls, values)
    print("done")