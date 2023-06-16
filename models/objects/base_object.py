from abc import ABC, abstractmethod
from models.utils import load_shader_program
import glm
import numpy as np
import trimesh

class BaseObject(ABC):
    def __init__(self,
                 app,
                 # shader
                 object_shader_name='default',
                 shadow_shader_name='shadow',
                 shader_dir='shaders',
                 # texture
                 texture_path_map=None,
                 # buffer
                 buffer_format='2f 3f 3f',
                 buffer_attrib=['in_texcoord_0', 'in_normal', 'in_position'],
                 # object poses
                 m_model=glm.mat4()
                 ):
        self.app = app
        self.buffer_format = buffer_format
        self.buffer_attrib = buffer_attrib

        # Construct VBO, VAO
        object_prog = load_shader_program(self.app.ctx, object_shader_name, shader_dir)
        shadow_prog = load_shader_program(self.app.ctx, shadow_shader_name, shader_dir)
        self.buffer = self.load_buffer()

        self.object_vaos = self.get_vao(self.buffer, object_prog)
        self.shadow_vaos = self.get_vao(self.buffer, shadow_prog)

        self.object_progs = self.get_program(self.object_vaos)
        self.shadow_progs = self.get_program(self.shadow_vaos)

        # texture
        self.textures = {}
        for texture_key, texture_path in texture_path_map.items():
            self.textures[texture_key] = load_texture(self.app, texture_path)

        # pose
        self.m_model = m_model
        self.initialize_params()

    def get_vao(self, buffer, program):
        vaos = {}
        if isinstance(buffer, dict):
            for name, curr_vbo in buffer.items():
                vao = self.app.ctx.vertex_array(
                    program,
                    [(curr_vbo, self.buffer_format, *self.buffer_attrib)],
                    skip_errors=True
                )
                vaos[name] = vao
            return vaos
        else:
            return {'object': self.app.ctx.vertex_array(
                program,
                [(buffer, self.buffer_format, *self.buffer_attrib)],
                skip_errors=True
            )}
        
    def get_program(self, vao_dict):
        program = {}
        for name, vao in vao_dict.items():
            program[name] = vao.program
        return program

    @abstractmethod
    def load_buffer(self): ...

    def get_model_matrix(self, pos, rot, scale):
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

    def initialize_params(self):

        # shadow
        for name, shadow_prog in self.shadow_progs.items():
            shadow_prog['m_proj'].write(self.app.camera.m_ortho_proj)
            shadow_prog['m_view_light'].write(self.app.light.m_view_light)
            shadow_prog['m_model'].write(self.m_model)

        # texture
        for name, object_prog in self.object_progs.items():
            object_prog['u_texture_0'] = 0
            self.textures[name].use(location=0) # TODO: PBR

            object_prog['shadowMap'] = 1
            object_prog['m_view_light'].write(self.app.light.m_view_light)
            self.app.offscreen_depth.use(location=1)

            # light
            object_prog['lightDir'].write(self.app.light.direction)
            object_prog['light.Ia'].write(self.app.light.Ia)
            object_prog['light.Id'].write(self.app.light.Id)
            object_prog['light.shadow_poisson_sampling_denominator'].write(
                glm.float32(self.app.light.shadow_poisson_sampling_denominator))
            object_prog['light.gamma_correction_coefficient'].write(
                glm.float32(self.app.light.gamma_correction_coefficient))
            object_prog['light.shadow_intensity'].write(glm.float32(self.app.light.shadow_intensity))

    def update(self):
        for name, object_prog in self.object_progs.items():
            object_prog['m_ortho_proj'].write(self.app.camera.m_ortho_proj)
            object_prog['m_proj'].write(self.app.camera.m_proj)
            object_prog['m_view'].write(self.app.camera.m_view)
            object_prog['m_view_light'].write(self.app.light.m_view_light)
            object_prog['m_model'].write(self.m_model)

            self.textures[name].use(location=0)
            self.app.offscreen_depth.use(location=1)

    def render(self):
        self.update()
        for object_vao in self.object_vaos.values():
            object_vao.render()

    def update_depth(self, m_view_light, m_proj):
        for shadow_prog in self.shadow_progs.values():
            shadow_prog['m_model'].write(self.m_model)
            shadow_prog['m_proj'].write(self.app.camera.m_ortho_proj if m_proj is None else m_proj)
            shadow_prog['m_view_light'].write(self.app.light.m_view_light if m_view_light is None else m_view_light)

    def render_depth(self, m_view_light=None, m_proj=None):
        self.update_depth(m_view_light, m_proj)
        for shadow_vao in self.shadow_vaos.values():
            shadow_vao.render()

    def destroy(self):
        self.buffer.release()
        [shadow_vao.release() for shadow_vao in self.shadow_vaos.values()]
        [object_vao.release() for object_vao in self.object_vaos.values()]
        [tex.release() for tex in self.textures.values()]