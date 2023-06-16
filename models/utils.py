import os
import numpy as np
import moderngl as mgl
import moderngl_window as mglw
import glm
from PIL import Image, ImageOps

def load_shader_program(
        ctx,
        shader_program_name: str,
        shader_dir: str
    ):
    vert_shader_path = os.path.join(shader_dir, '{}.vert'.format(shader_program_name))
    frag_shader_path = os.path.join(shader_dir, '{}.frag'.format(shader_program_name))
    
    with open(vert_shader_path) as file:
        vertex_shader = file.read()
    with open(frag_shader_path) as file:
        fragment_shader = file.read()

    program = ctx.program(
            vertex_shader=vertex_shader, 
            fragment_shader=fragment_shader
    )
    return program

def get_model_matrix(pos = (0, 0, 0), rot = (0, 0, 0), scale = (1, 1, 1)):
    rot = glm.vec3([glm.radians(a) for a in rot])
    m_model = glm.mat4()
    # translate
    m_model = glm.translate(m_model, pos)
    # rotate
    m_model = glm.rotate(m_model, rot.z, glm.vec3(0, 0, 1))
    m_model = glm.rotate(m_model, rot.y, glm.vec3(0, 1, 0))
    m_model = glm.rotate(m_model, rot.x, glm.vec3(1, 0, 0))
    # scale
    m_model = glm.scale(m_model, scale)
    return m_model

def get_model_matrix_from_config(config):
    matrix = get_model_matrix(
        pos   = list(config['pos']),
        rot   = list(config['rot']),
        scale = list(config['scale'])
    )
    return matrix

def load_texture(app, image, anisotropy=32.0):
    img = image.convert('RGB')
    im_flip = ImageOps.flip(img)
    texture = app.ctx.texture(im_flip.size, 3, im_flip.tobytes())

    # mipmaps
    texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
    texture.build_mipmaps()
    # AF
    texture.anisotropy = anisotropy
    return texture

def get_bounding_box(points):
    '''
    Args:
        points: (n, 3)
    '''
    x_min, y_min, z_min = np.min(points, axis=0)
    x_max, y_max, z_max = np.max(points, axis=0)
    
    vertices = [
        (x_min, y_min, z_max), (x_max, y_min, z_max), (x_max, y_max, z_max), (x_min, y_max, z_max),
        (x_min, y_max, z_min), (x_min, y_min, z_min), (x_max, y_min, z_min), (x_max, y_max, z_min)
    ]

    indices = [(0, 2, 3), (0, 1, 2),
               (1, 7, 2), (1, 6, 7),
               (6, 5, 4), (4, 7, 6),
               (3, 4, 5), (3, 5, 0),
               (3, 7, 4), (3, 2, 7),
               (0, 6, 1), (0, 5, 6)]
    return vertices, indices

def rigid_transform(points, transform):
    '''
    Args
        points: (n, 3)
        transform: (4, 4)
    '''
    points_h = np.ones((points.shape[0], 4))
    points_h[:, :3] = points 
    points_h_new = points_h @ transform.T
    points_new = points_h_new[:, :3]
    return points_new