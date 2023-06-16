import os
import numpy as np
from PIL import Image 
import trimesh
from tqdm import tqdm

def compress_animation_files(dir_path):
    files = sorted([os.path.join(dir_path, file) for file in os.listdir(dir_path)])
    glb = trimesh.load(files[0])
    keys = list(glb.geometry.keys())
    mesh = glb.geometry[keys[0]]
    tex_rgb = mesh.visual.material.baseColorTexture
    tex_dir = os.path.join(dir_path, '../texture')
    os.makedirs(tex_dir, exist_ok=True)
    tex_rgb.save(os.path.join(tex_dir, 'rgb.png'))

    for file in tqdm(files):
        glb = trimesh.load(file)
        keys = list(glb.geometry.keys())
        mesh = glb.geometry[keys[0]]
        mesh.visual.material.baseColorTexture = None
        glb.export(file)

def test():
    path = 'assets/human_animations/lady_walking/animation'
    compress_animation_files(path)

if __name__ == '__main__':
    test()