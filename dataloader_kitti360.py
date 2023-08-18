from constants import T_blender2opengl, UTM_ORIGIN_EAST, UTM_ORIGIN_NORTH, ORIGIN_HEIGHT
from pathlib import Path
import numpy as np
import utm
from scipy.spatial.transform import Rotation as R
from PIL import Image
from tqdm import tqdm
import torch.nn.functional as F
import torch
import cv2
import os 
from models.utils import get_model_matrix

class DataLoader:
    def __init__(self, root_dir, frame_start, frame_end, debug=False, window_size=None):
        self.root_path = root_dir
        self.debug = debug
        self.window_size = window_size
        self.rgbs = []
        self.depths = []
        self.scale = 0.5
        seq_id = 0
        dir_seq = '2013_05_28_drive_{:0>4d}_sync'.format(seq_id)
        dir_rgb_0 = os.path.join(root_dir, 'data_2d_raw', dir_seq, 'image_00', 'data_rect')
        dir_poses = os.path.join(root_dir, 'data_poses', dir_seq)
        
        # Extrinsics
        pose_cam_0 = np.genfromtxt(os.path.join(dir_poses, 'cam0_to_world.txt')) #(n, 17)
        frame_id = pose_cam_0[:, 0]
        sample = np.logical_and(frame_id >= frame_start, frame_id <= frame_end)
        frame_id = frame_id[sample].astype(np.int32)

        cam2world = pose_cam_0[sample, 1:].reshape(-1, 4, 4)[:, :3]
        self.setup_poses(cam2world)

        for i in frame_id:
            path = os.path.join(dir_rgb_0, '{:0>10d}.png'.format(i))
            rgb = np.array(Image.open(path).resize(size=window_size, resample=Image.Resampling.BILINEAR))[..., :3].astype(np.float32) / 255
            self.rgbs.append(rgb)
        
        # Time for getting sunlight, gets filled in when calculate_poses is called
        self.start_timestamp = None
        self.i = 0
        self.start_frame = frame_start
        
    def __len__(self):
        return len(self.rgbs)

    def __getitem__(self, item):
        return {
            "rgb": self.rgbs[item],
            "pose": self.poses[item] 
        }

    def __next__(self):
        res = self[self.i]
        self.i = (self.i + 1) % len(self)
        return res
    
    def setup_poses(self, cam2world):
        n_pose = cam2world.shape[0]
        pos = cam2world[:, :, -1]
        center = np.mean(pos, axis=0)
        transform = get_model_matrix(
            pos=(0, 0, 0), 
            rot=(-90, 0, 0)
        )
        transform = np.array(transform)

        world2cam_gl = []
        for i in range(n_pose):
            c2w_cv = cam2world[i]
            c2w_cv[:, -1] -= center
            c2w_cv = np.concatenate([c2w_cv, np.array([[0, 0, 0, 1]])], axis=0)
            c2w_cv = transform @ c2w_cv
            w2c_cv = np.linalg.inv(c2w_cv)
            w2c_gl = np.eye(4)
            w2c_gl[0] = w2c_cv[0]
            w2c_gl[1:3] = -w2c_cv[1:3]
            world2cam_gl.append(w2c_gl)
        world2cam_gl = np.stack(world2cam_gl)
        self.poses = world2cam_gl

def test():
    dataloader = DataLoader(
        '/hdd/datasets/KITTI-360', 
        window_size=(1408, 376)
    )
    data = dataloader[0]
    img = data['rgb']
    pose = data['pose']
    print('image shape:', img.shape)
    print('pose:\n', pose)

if __name__ == '__main__':
    test()