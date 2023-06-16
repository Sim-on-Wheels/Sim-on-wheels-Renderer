import numpy as np 
import moderngl as mgl
import moderngl_window as mglw
from models.objects.base_object_pbr import ObjectAlbedo

class WorldBuildingObject(ObjectAlbedo):
    def __init__(self, 
        app,
        m_model
    ):
        object_path = None
        super().__init__(app, m_model, object_path)

    def get_data(self, vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')
    
    def load_buffer(self):
        vertices = [(0, 0, 26), ( 77, 0,  26), (77,  7.5,  26), (0, 7.5,  26),
                    (0, 7.5, 0.5), (0, 0, 0.5), (77, 0, 0.5), (77, 7.5, 0.5)]

        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]
        vertex_data = self.get_data(vertices, indices)

        tex_coord_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                             (0, 2, 3), (0, 1, 2),
                             (0, 1, 2), (2, 3, 0),
                             (2, 3, 0), (2, 0, 1),
                             (0, 2, 3), (0, 1, 2),
                             (3, 1, 2), (3, 0, 1),]
        tex_coord_data = self.get_data(tex_coord_vertices, tex_coord_indices)

        normals = [( 0, 0, 1) * 6,
                   ( 1, 0, 0) * 6,
                   ( 0, 0,-1) * 6,
                   (-1, 0, 0) * 6,
                   ( 0, 1, 0) * 6,
                   ( 0,-1, 0) * 6,]
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        color = np.ones_like(vertex_data)
        data = np.concatenate([vertex_data, color], axis=1)
        buffer = self.app.ctx.buffer(np.float32(data))
        return buffer