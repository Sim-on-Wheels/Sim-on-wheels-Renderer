#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec3 in_normal;

uniform mat4 m_model;
uniform mat4 m_camera;
uniform mat4 m_proj;
uniform mat4 m_shadow_bias;
uniform vec3 lightDir;

out vec3 light_dir;
out vec3 normal;
out vec4 ShadowCoord;

void main() {
    mat4 m_view = m_camera * m_model;
    vec4 p = m_view * vec4(in_position, 1.0);
    gl_Position =  m_proj * p;
    mat3 m_normal = inverse(transpose(mat3(m_view)));
    normal = m_normal * normalize(in_normal);
    light_dir = (m_view * vec4(lightDir, 0.0)).xyz;
    ShadowCoord = m_shadow_bias * vec4(in_position, 1.0);
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

uniform vec4 color;
uniform sampler2D shadowMap;

in vec3 light_dir;
in vec3 normal;
in vec4 ShadowCoord;

vec2 poissonDisk[4] = vec2[](
  vec2( -0.94201624, -0.39906216 ),
  vec2( 0.94558609, -0.76890725 ),
  vec2( -0.094184101, -0.92938870 ),
  vec2( 0.34495938, 0.29387760 )
);

void main() {
    float bias = 0.005;
    float visibility = 1.0;
    // if (texture(shadowMap, ShadowCoord.xy ).r <  ShadowCoord.z - bias){
    //     visibility = 0.5;
    // }
    for (int i = 0; i < 4 ; i++){
        if ( texture( shadowMap, ShadowCoord.xy + poissonDisk[i]/800.0 ).r  <  ShadowCoord.z-bias ){
            visibility -= 0.12;
        }
    }
    float l = max(dot(normalize(light_dir), normalize(normal)), 0.0);
    fragColor = color * (0.25 + abs(l) * 0.9) * visibility;
}
#endif