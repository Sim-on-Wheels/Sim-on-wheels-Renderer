import glm
import numpy as np
from PIL import Image, ImageOps
from models.utils import load_shader_program, load_texture
from models.show import ShowObjects
import moderngl_window as mglw

class Background:
    def __init__(self, app):
        self.app = app
        tex_img = Image.open('assets/textures/background.png')
        self.update_texture(tex_img)
        vbo = self.load_buffer(app)
        prog = load_shader_program(app.ctx, shader_program_name='background', shader_dir='shaders')
        self.vao = app.ctx.vertex_array(
                prog,
                [(vbo, '2f 2f', *['in_uv', 'in_xy'])],
                skip_errors=True
            )
        self.program = self.vao.program
        self.on_init()

    def load_buffer(self, app):
        vertices_xy = self.get_vertices_for_quad_2d(size=(2.0, 2.0), bottom_left_corner=(-1.0, -1.0))
        vertices_uv = self.get_vertices_for_quad_2d(size=(1.0, 1.0), bottom_left_corner=(0.0, 0.0))
        vertex_data = np.hstack([vertices_uv, vertices_xy])
        vbo = app.ctx.buffer(vertex_data)
        return vbo

    def get_vertices_for_quad_2d(self, size=(2.0, 2.0), bottom_left_corner=(-1.0, -1.0)) -> np.array:
        # A quad is composed of 2 triangles: https://en.wikipedia.org/wiki/Polygon_mesh
        w, h = size
        x_bl, y_bl = bottom_left_corner
        vertices = np.array([[x_bl,     y_bl + h],
                             [x_bl,     y_bl],
                             [x_bl + w, y_bl],

                             [x_bl,     y_bl + h],
                             [x_bl + w, y_bl],
                             [x_bl + w, y_bl + h]], dtype=np.float32)
        return vertices

    def on_init(self):
        # texture
        self.program['texture0'].value = 0
        self.texture.use(0)

        # mvp
        eye = np.eye(4, dtype=np.float32)
        self.program['m_model'].write(glm.mat4(eye))

    def update_texture(self, image):
        image = image.convert('RGB')
        image_flip = ImageOps.flip(image)
        self.texture = self.app.ctx.texture(image_flip.size, 3, image_flip.tobytes())

    def update(self):
        self.program['texture0'].value = 0
        self.texture.use(0)

    def render(self):
        self.update()
        self.vao.render()
    
    def render_depth(self):
        pass

class Show(ShowObjects):
    aspect_ratio = 1408/376
    window_size = (1408, 376)
    def __init__(self, **kwargs):
        super().__init__(config='configs/debug.yaml', **kwargs)
        bg = Background(self)
        self.objects = [bg]

def main():
    mglw.run_window_config(Show)

if __name__ == '__main__':
    main()