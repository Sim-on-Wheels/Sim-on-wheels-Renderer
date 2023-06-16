import numpy as np
import trimesh

def test():
    glb_path = 'assets/objects/building/old_buildings.glb'
    glb = trimesh.load(glb_path)
    keys = list(glb.geometry.keys())
    
    for key in keys:
        print('\n\nKey:{}'.format(key))
        mesh = glb.geometry[key]
        mat = mesh.visual.material
        print('name:{}'.format(mat.name))
        print('main_color:', mat.main_color)
        print('baseColorFactor:', mat.baseColorFactor)
        print('baseColorTexture:', mat.baseColorTexture)
        print('metallicFactor:', mat.metallicFactor)
        print('roughnessFactor:', mat.roughnessFactor)
        print('metallicRoughnessTexture:', mat.metallicRoughnessTexture)

if __name__ == '__main__':
    test()