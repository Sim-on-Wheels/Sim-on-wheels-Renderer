import glm
import numpy as np
import trimesh
from abc import ABC, abstractmethod
from models.utils import load_shader_program, load_texture, rigid_transform, get_bounding_box

class BaseObjectPBR(ABC):
    def __init__(self,
                 app,
                 object_path,
                 # shader
                 object_shader_name,
                 shadow_shader_name,
                 shader_dir,
                 # buffer
                 buffer_format,
                 buffer_attrib,
                 # object poses
                 m_model=glm.mat4()
    ):
        self.app = app
        self.object_path = object_path
        self.buffer_format = buffer_format
        self.buffer_attrib = buffer_attrib

        # Construct VBO, VAO
        object_prog = load_shader_program(self.app.ctx, object_shader_name, shader_dir)
        shadow_prog = load_shader_program(self.app.ctx, shadow_shader_name, shader_dir)
        self.buffer = self.load_buffer()

        self.object_vao = self.get_vao(self.buffer, object_prog)
        self.shadow_vao = self.get_vao(self.buffer, shadow_prog)

        self.object_prog = self.object_vao.program
        self.shadow_prog = self.shadow_vao.program

        # pose
        self.m_model = m_model
        self.initialize_params()

    @property
    def position(self):
        m_model = np.array(self.m_model)
        pos = m_model[:3, -1]
        return pos

    @property 
    def transform_matrix(self):
        transform = np.array(self.m_model)
        return transform
    
    def update_pose(self, m_model):
        self.m_model = m_model

    def get_vao(self, buffer, program):
        vao = self.app.ctx.vertex_array(
                program,
                [(buffer, self.buffer_format, *self.buffer_attrib)],
                skip_errors=True)
        return vao

    def load_glb_file(self, glb_path):
        glb = trimesh.load(glb_path)
        # Apply transformation to each components
        graph = glb.graph 
        for node_name in graph.nodes_geometry:
            transform, geometry_name = graph[node_name]
            mesh = glb.geometry[geometry_name]
            mesh.apply_transform(transform)
        return glb

    def should_contain(self, name, mesh):
        return True

    @abstractmethod
    def load_mesh_data(self, mesh): ...

    def get_align_matrix(self):
        return np.eye(4)

    def align(self, data):
        transform = self.get_align_matrix()
        points = data[:, :3]
        points_new = rigid_transform(points, transform)
        data[:, :3] = points_new
        return data

    def load_buffer(self): 
        glb = self.load_glb_file(self.object_path) 
        data = []
        for name, mesh in glb.geometry.items():
            if self.should_contain(name, mesh):
                mesh_data = self.load_mesh_data(mesh)
                data.append(mesh_data)
        data = np.concatenate(data, axis=0).astype(np.float32)
        data = self.align(data)
        buffer = self.app.ctx.buffer(data)
        return buffer
    
    @abstractmethod
    def initialize_texture(self): ...

    def initialize_params(self):
        # texture 
        self.initialize_texture()
        # mvp
        self.object_prog['m_proj'].write(self.app.camera.m_proj)
        self.object_prog['m_view'].write(self.app.camera.m_view)
        self.object_prog['m_model'].write(self.m_model)
        self.object_prog['cam_pos'].write(self.app.camera.position)
        # light
        self.object_prog['light.direction'].write(np.float32(self.app.light.direction))
        self.object_prog['light.color'].write(np.float32(self.app.light.color))
        self.object_prog['light.light_intensity'].write(np.float32(self.app.light.light_intensity))
        self.object_prog['light.ambient_intensity'].write(np.float32(self.app.light.ambient_intensity))
        self.object_prog['light.shadow_intensity'].write(np.float32(self.app.light.shadow_intensity))
        self.object_prog['light.shadow_poisson_sampling_denominator'].write(np.float32(self.app.light.shadow_poisson_sampling_denominator))
        self.object_prog['light.gamma_correction'].write(np.float32(self.app.light.gamma_correction))
        # shadow
        self.object_prog['m_ortho_proj'].write(self.app.camera.m_ortho_proj)
        self.object_prog['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_prog['m_model'].write(self.m_model)
        self.shadow_prog['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_prog['m_proj'].write(self.app.camera.m_ortho_proj)

    @abstractmethod
    def update_texture(self): ...

    def update(self):
        self.update_texture()
        self.object_prog['m_proj'].write(self.app.camera.m_proj)
        self.object_prog['m_view'].write(self.app.camera.m_view)
        self.object_prog['m_model'].write(self.m_model)
        self.object_prog['cam_pos'].write(self.app.camera.position)
        self.object_prog['m_ortho_proj'].write(self.app.camera.m_ortho_proj)
        self.object_prog['m_view_light'].write(self.app.light.m_view_light)

    def render(self):
        self.update()
        self.object_vao.render()

    def update_depth(self, m_view_light, m_proj):
        self.shadow_prog['m_model'].write(self.m_model)
        self.shadow_prog['m_view_light'].write(self.app.light.m_view_light if m_view_light is None else m_view_light)
        self.shadow_prog['m_proj'].write(self.app.camera.m_ortho_proj if m_proj is None else m_proj)

    def render_depth(self, m_view_light=None, m_proj=None):
        self.update_depth(m_view_light, m_proj)
        self.shadow_vao.render()

    def destroy(self):
        self.buffer.release()
        self.object_vao.release()
        self.shadow_vao.release()
class ObjectConst(BaseObjectPBR):
    def __init__(self, 
        app, 
        m_model,
        object_path, 
        default_albedo = [0, 0, 0], 
        default_metallic = 0.0, 
        default_roughness = 1.0
    ): 
        self.default_albedo = default_albedo
        self.default_metallic = default_metallic
        self.default_roughness = default_roughness
        # shader
        object_shader_name = 'objects/pbr'
        shadow_shader_name = 'shadow'
        shader_dir = 'shaders'
        # buffer
        buffer_format = '3f 3f 3f 1f 1f'
        buffer_attrib = ['in_position', 'in_normal', 'in_albedo', 'in_metallic', 'in_roughness']
        super().__init__(app, object_path, object_shader_name, shadow_shader_name, shader_dir,
            buffer_format, buffer_attrib, m_model)        
    
    def initialize_texture(self): 
        self.object_prog['shadowMap'] = 0
        self.app.offscreen_depth.use(location=0)
    
    def update_texture(self):
        self.app.offscreen_depth.use(location=0)

    def load_mesh_data(self, mesh):
        vertices = np.array(mesh.vertices) # (v, 3)
        normals = np.array(mesh.vertex_normals) # (v, 3)
        faces = np.array(mesh.faces).flatten() # (f * 3)
        n = faces.shape[0]
        
        material = mesh.visual.material
        base_color = material.baseColorFactor
        albedo = base_color[:3] if base_color is not None else self.default_albedo
        metallic = material.metallicFactor if material.metallicFactor is not None else self.default_metallic
        roughness = material.roughnessFactor if material.roughnessFactor is not None else self.default_roughness

        d = 3 + 3 + 3 + 2 # vert, normal, rgb, metallic+roughness
        mesh_data = np.zeros((n, d))
        mesh_data[:, :3] = vertices[faces]
        mesh_data[:, 3:6] = normals[faces]
        mesh_data[:, 6:9] = np.array(albedo) / 255
        mesh_data[:, 9] = metallic
        mesh_data[:, 10] = roughness
        return mesh_data.astype(np.float32)

class ObjectUV(BaseObjectPBR):
    def __init__(self, 
        app, 
        m_model,
        object_path, 
        texture_key
    ):
        self.texture_key = texture_key
        # shader
        object_shader_name = 'objects/pbr_uv'
        shadow_shader_name = 'shadow'
        shader_dir = 'shaders'
        # buffer
        buffer_format = '3f 3f 2f'
        buffer_attrib = ['in_position', 'in_normal', 'in_texcoord_0']
        super().__init__(app, object_path, object_shader_name, shadow_shader_name, shader_dir,
            buffer_format, buffer_attrib, m_model)
    
    def initialize_texture(self):
        self.object_prog['shadowMap'] = 0
        self.app.offscreen_depth.use(location=0)

        glb = self.load_glb_file(self.object_path)
        mesh = glb.geometry[self.texture_key]
        mat = mesh.visual.material
        self.tex_rgb = load_texture(self.app, mat.baseColorTexture)
        self.object_prog['u_rgb'] = 1
        self.tex_rgb.use(location=1)
        self.tex_metallic_roughness = load_texture(self.app, mat.metallicRoughnessTexture)
        self.object_prog['u_metallic_roughness'] = 2
        self.tex_metallic_roughness.use(location=2)

    def update_texture(self):
        self.app.offscreen_depth.use(location=0)
        self.tex_rgb.use(location=1)
        self.tex_metallic_roughness.use(location=2)

    def load_mesh_data(self, mesh):
        vert = np.array(mesh.vertices)
        normal = np.array(mesh.vertex_normals)
        uv = np.array(mesh.visual.uv)
        faces = np.array(mesh.faces).flatten()
        
        vert = vert[faces]
        normal = normal[faces]
        uv = uv[faces]
        mesh_data = np.concatenate([vert, normal, uv], axis=1)
        return mesh_data.astype(np.float32)

class ObjectUVConstMR(BaseObjectPBR):
    def __init__(self, 
        app, 
        m_model,
        object_path, 
        texture_key,
        default_metallic = 0.0, 
        default_roughness = 1.0
    ):
        self.texture_key = texture_key
        self.default_metallic = default_metallic
        self.default_roughness = default_roughness
        # shader
        object_shader_name = 'objects/pbr_uv_const_mr'
        shadow_shader_name = 'shadow'
        shader_dir = 'shaders'
        # buffer
        buffer_format = '3f 3f 2f 1f 1f'
        buffer_attrib = ['in_position', 'in_normal', 'in_texcoord_0', 'in_metallic', 'in_roughness']
        super().__init__(app, object_path, object_shader_name, shadow_shader_name, shader_dir,
            buffer_format, buffer_attrib, m_model)
    
    def initialize_texture(self):
        self.object_prog['shadowMap'] = 0
        self.app.offscreen_depth.use(location=0)

        glb = self.load_glb_file(self.object_path)
        mesh = glb.geometry[self.texture_key]
        mat = mesh.visual.material
        self.tex_rgb = load_texture(self.app, mat.baseColorTexture)
        self.object_prog['u_rgb'] = 1
        self.tex_rgb.use(location=1)

    def update_texture(self):
        self.app.offscreen_depth.use(location=0)
        self.tex_rgb.use(location=1)

    def load_mesh_data(self, mesh):
        vert = np.array(mesh.vertices)
        normal = np.array(mesh.vertex_normals)
        uv = np.array(mesh.visual.uv)
        faces = np.array(mesh.faces).flatten()
        
        material = mesh.visual.material
        metallic = material.metallicFactor if material.metallicFactor is not None else self.default_metallic
        roughness = material.roughnessFactor if material.roughnessFactor is not None else self.default_roughness

        d = 2 + 3 + 3 + 1 + 1
        mesh_data = np.zeros((faces.shape[0], d))
        mesh_data[:, :3] = vert[faces]
        mesh_data[:, 3:6] = normal[faces]
        mesh_data[:, 6:8] = uv[faces]
        mesh_data[:, 8] = metallic 
        mesh_data[:, 9] = roughness
        return mesh_data.astype(np.float32)

class ObjectAlbedo(BaseObjectPBR):
    def __init__(self,
        app, 
        m_model,
        object_path
    ):
        # shader
        object_shader_name = 'objects/albedo'
        shadow_shader_name = 'shadow'
        shader_dir = 'shaders'
        # buffer
        buffer_format = '3f 3f'
        buffer_attrib = ['in_position', 'in_color']
        super().__init__(app, object_path, object_shader_name, shadow_shader_name, shader_dir,
            buffer_format, buffer_attrib, m_model)
        
    def initialize_texture(self):
        self.object_prog['shadowMap'] = 0
        self.app.offscreen_depth.use(location=0)
    
    def initialize_params(self):
        # texture
        self.initialize_texture()
        # mvp
        self.object_prog['m_proj'].write(self.app.camera.m_proj)
        self.object_prog['m_view'].write(self.app.camera.m_view)
        self.object_prog['m_model'].write(self.m_model)
        # light
        self.object_prog['light.shadow_intensity'].write(np.float32(self.app.light.shadow_intensity))
        self.object_prog['light.shadow_poisson_sampling_denominator'].write(np.float32(self.app.light.shadow_poisson_sampling_denominator))
        # shadow
        self.object_prog['m_ortho_proj'].write(self.app.camera.m_ortho_proj)
        self.object_prog['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_prog['m_proj'].write(self.app.camera.m_ortho_proj)
        self.shadow_prog['m_view_light'].write(self.app.light.m_view_light)
        self.shadow_prog['m_model'].write(self.m_model)
    
    def update_texture(self):
        self.app.offscreen_depth.use(location=0)
    
    def update(self):
        self.update_texture()
        self.object_prog['m_proj'].write(self.app.camera.m_proj)
        self.object_prog['m_view'].write(self.app.camera.m_view)
        self.object_prog['m_model'].write(self.m_model)
        self.object_prog['m_ortho_proj'].write(self.app.camera.m_ortho_proj)
        self.object_prog['m_view_light'].write(self.app.light.m_view_light)
    
    def load_mesh_data(self, mesh):
        vert = np.array(mesh.vertices)
        faces = np.array(mesh.faces).flatten()
        vert = vert[faces]

        mat = mesh.visual.material
        color = np.array(mat.emissiveFactor)
        mesh_data = np.zeros((vert.shape[0], 6))
        mesh_data[:, :3] = vert
        mesh_data[:, 3:] = color
        return mesh_data.astype(np.float32)