#version 330
in vec2 in_uv;
in vec2 in_xy;
uniform mat4 m_model;
out vec2 fragment_uv;
void main() {
    vec4 p = vec4(in_xy, 0.999, 1.0);
    gl_Position = m_model * p;
    fragment_uv = in_uv;
}