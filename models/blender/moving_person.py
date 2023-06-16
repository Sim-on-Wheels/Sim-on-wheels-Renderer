import os
import bpy
import numpy as np
root = '/home/zhi-hao/Desktop/hil/HIL_realtime_rendering/'

def export_mesh(dir_path, n_frames):
    os.makedirs(dir_path, exist_ok=True)
    for i in range(n_frames):
        bpy.context.scene.frame_current = i + 1
        glb_path = os.path.join(dir_path, '{:0>5d}.glb'.format(i))
        bpy.ops.export_scene.gltf(
            filepath=glb_path, 
            export_animations=False,
            export_current_frame=True,
            export_apply=True,
            export_skins=False
        )


def main():
    dir_path = os.path.join(root, 'assets/human_animations/woman_walking/animation')
    n_frames = 30
    export_mesh(dir_path, n_frames)
    
def test():
    path = os.path.join(root, 'assets/test')
    export_mesh(path, 10)
        
if __name__ == '__main__':
    main()