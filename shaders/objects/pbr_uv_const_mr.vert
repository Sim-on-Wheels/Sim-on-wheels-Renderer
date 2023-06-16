#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord_0;
layout (location = 3) in float in_metallic;
layout (location = 4) in float in_roughness;

out vec2 uv_0;
out vec3 normal;
out vec3 view_dir;
out float metallic;
out float roughness;
out vec4 shadowCoord;

uniform vec3 cam_pos;
uniform mat4 m_proj;
uniform mat4 m_ortho_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;
uniform mat4 m_model;

// remap ranges from -1, 1 to 0, 1
mat4 m_shadow_bias = mat4(
    0.5, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.0,
    0.5, 0.5, 0.5, 1.0
); 

void main() {
    uv_0 = in_texcoord_0;
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
    vec3 vert_pos = (m_model * vec4(in_position, 1.0)).xyz;
    view_dir = cam_pos - vert_pos;

    metallic = in_metallic;
    roughness = in_roughness;

    mat4 shadowMVP = m_ortho_proj * m_view_light * m_model;
    shadowCoord = m_shadow_bias * shadowMVP * vec4(in_position, 1.0);
}