#version 330
in vec2 fragment_uv;
uniform sampler2D texture0;
out vec4 fragment_color;
void main() {
    fragment_color = texture(texture0, fragment_uv);
}