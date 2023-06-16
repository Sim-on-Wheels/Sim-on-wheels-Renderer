#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;

out vec2 uv_0;
out vec3 normal;
out vec4 shadowCoord;
out vec3 light_dir;

uniform mat4 m_proj;
uniform mat4 m_ortho_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;
uniform mat4 m_model;
uniform vec3 lightDir;

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
    light_dir = (m_view * vec4(lightDir, 0.0)).xyz;

    mat4 shadowMVP = m_ortho_proj * m_view_light * m_model;
    shadowCoord = m_shadow_bias * shadowMVP * vec4(in_position, 1.0); // remap ranges from -1, 1 to 0, 1
}