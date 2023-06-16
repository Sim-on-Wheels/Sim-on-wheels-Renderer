#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec4 shadowCoord;
in vec3 light_dir;

vec2 poissonDisk[4] = vec2[](
  vec2( -0.94201624, -0.39906216 ),
  vec2( 0.94558609, -0.76890725 ),
  vec2( -0.094184101, -0.92938870 ),
  vec2( 0.34495938, 0.29387760 )
);


struct Light {
    vec3 Ia;
    vec3 Id;

    float shadow_poisson_sampling_denominator;
    float gamma_correction_coefficient;
    float shadow_intensity;
};
uniform Light light;
uniform sampler2D u_texture_0;
uniform sampler2D shadowMap;


vec3 getLight(vec3 color) {
    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    float diff = max(0, dot(normalize(light_dir), normalize(Normal)));
    vec3 diffuse = diff * light.Id;

    // shadow
    return color * (ambient + diffuse);
}


void main() {
    float gamma = light.gamma_correction_coefficient;
    float bias = 0.005;
    vec3 color = texture(u_texture_0, uv_0).rgb;
    color = pow(color, vec3(gamma));
    float visibility = 1.0;

    for (int i = 0; i < 4 ; i++) {
        if ((shadowCoord.x < 0) || (shadowCoord.x > 1) || (shadowCoord.y < 0) || (shadowCoord.y > 1))
            continue;
        if (texture( shadowMap, shadowCoord.xy + poissonDisk[i] / light.shadow_poisson_sampling_denominator ).r  <  shadowCoord.z-bias ){
            visibility -= light.shadow_intensity;
        }
    }
    //float l = max(dot(normalize(light_dir), normalize(normal)), 0.0);
    //fragColor = vec4(color, 1.0) * (0.25 + abs(l) * 0.9) * visibility;

    color = getLight(color);
    color = pow(color, 1 / vec3(gamma)) * visibility;
    fragColor = vec4(color, 1.0);
}










