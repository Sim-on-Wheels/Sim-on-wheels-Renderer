from constants import T_blender2opengl, UTM_ORIGIN_EAST, UTM_ORIGIN_NORTH, ORIGIN_HEIGHT
from pathlib import Path
import numpy as np
import utm
from scipy.spatial.transform import Rotation as R
from PIL import Image
from tqdm import tqdm
import torch
import cv2


class DataLoader:

    def __init__(self, root_path, debug=False, window_size=None):
        self.root_path = root_path
        self.debug = debug
        self.window_size = window_size
        self.rgbs = []
        self.depths = []
        self.scale = 0.5
        for img_path in tqdm(sorted(list((Path(self.root_path) / 'img').glob('*.png')), key=lambda x: int(x.name[:-4].split('_')[-1]))):
            if not debug:
                rgb = np.array(Image.open(img_path).resize(size=window_size, resample=Image.Resampling.BILINEAR))[..., :3].astype(np.float32) / 255
                self.rgbs.append(rgb)
            else:
                self.rgbs.append(img_path)

        for depth_path in tqdm(sorted(list((Path(self.root_path) / 'depth_img').glob('*.npy')), key=lambda x: int(x.name[:-4].split('im')[-1]))):
            dm = np.nan_to_num(np.load(depth_path), nan=np.inf, posinf=np.inf, neginf=np.inf)
            h, w = dm.shape
            h_new, w_new = int(h * self.scale), int(w * self.scale)
            dm = cv2.resize(dm, (h_new, w_new))
            self.depths.append(dm)
        
        # Time for getting sunlight, gets filled in when calculate_poses is called
        self.start_timestamp = None

        raw_gpses = sorted(list((Path(self.root_path) / 'raw_gps').glob('*.npy')), key=lambda x: int(x.name[:-4].split('_')[-1]))
        assert len(self.rgbs) == len(raw_gpses) == len(self.depths)
        self.poses, self.timestamps = self.calculate_poses(raw_gpses)

        self.positions = -torch.bmm(torch.from_numpy(self.poses[:, :3, :3].transpose(0, 2, 1)),
                                    torch.from_numpy(self.poses[:, :3, 3:]))
        # offset = 500
        # self.poses = self.poses[offset:]
        # self.rgbs = self.rgbs[offset:]
        # self.depths = self.depths[offset:]
        self.i = 0

    def __len__(self):
        return len(self.rgbs)

    def __getitem__(self, item):
        return {
            "rgb": self.rgbs[item] if not self.debug else np.array(Image.open(self.rgbs[item]).resize(size=self.window_size, resample=Image.Resampling.BILINEAR))[..., :3].astype(np.float32) / 255,
            "pose": self.poses[item] @ T_blender2opengl,
            "depth": self.depths[item]
        }

    def __next__(self):
        res = self[self.i]
        self.i = (self.i + 1) % len(self)
        return res

    def calculate_poses(self, gps_paths):
        '''
        Calculate world2cam matrix in OpenGL convention
        gps data format:
            cur_gps.latitude,
            cur_gps.longitude,
            cur_gps.height,
            cur_gps.roll,
            cur_gps.pitch,
            cur_gps.azimuth
        coordinate definition:
            x: east
            y: north
            z: up (the opposite of gravity)
        '''
        n_frames = len(gps_paths)
        gps_data = np.stack([np.load(path) for path in gps_paths])
        lat = gps_data[:, 0]
        lon = gps_data[:, 1]
        height = gps_data[:, 2]
        roll = gps_data[:, 3]  # y, right-handed
        pitch = gps_data[:, 4]  # x, right-handed
        azimuth = gps_data[:, 5]  # z, left-handed
        timestamp = gps_data[:,6]
        self.start_timestamp = timestamp[0]
        timestamp -= self.start_timestamp
        # dates = np.array([datetime.datetime.utcfromtimestamp(stamp) for stamp in timestamp])
        # sites = np.array([pvlib.location.Location(lat, lon) for (lat,lon) in zip(lat,lon)])
        # sun_poses = [sites[i].get_solarposition(dates[i]) for i in range(n_frames)]
        # print(type(sun_poses[0]))
        utm_data = utm.from_latlon(lat, lon)
        east, north = utm_data[0], utm_data[1]

        # ----------------------------------------
        # normalize positions, center at (0, 0, 0)
        east -= UTM_ORIGIN_EAST
        north -= UTM_ORIGIN_NORTH
        height -= ORIGIN_HEIGHT
        pos = np.stack([east, north, height]).T  # position (n, 3)

        euler = np.stack([pitch, roll, -azimuth]).T
        r = R.from_euler('xyz', euler, degrees=True)
        rot = r.as_matrix()  # (n, 3, 3)

        cam2world = np.zeros((n_frames, 4, 4))
        cam2world[:, -1, -1] = 1
        cam2world[:, :3, :3] = rot  # rot.transpose((0, 2, 1))
        cam2world[:, :3, 3] = pos

        cv2gl = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, -1, 0, 0],
            [0, 0, 0, 1]
        ])
        world2cam_cv = np.zeros_like(cam2world)
        world2cam_gl = np.zeros_like(cam2world)
        for i in range(len(cam2world)):
            world2cam_cv[i] = np.linalg.inv(cam2world[i])
            world2cam_gl[i] = cv2gl @ world2cam_cv[i]
        return world2cam_gl, timestamp