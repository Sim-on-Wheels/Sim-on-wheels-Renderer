#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_color;

out vec3 albedo; 
out vec4 shadowCoord;

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
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
    albedo = in_color;

    mat4 shadowMVP = m_ortho_proj * m_view_light * m_model;
    shadowCoord = m_shadow_bias * shadowMVP * vec4(in_position, 1.0);
}