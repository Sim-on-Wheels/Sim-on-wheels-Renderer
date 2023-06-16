#version 330 core

layout (location = 0) out vec4 fragColor;

in vec3 albedo; 
in vec4 shadowCoord;

struct Light {
    float shadow_intensity;
    float shadow_poisson_sampling_denominator;
};
uniform Light light;
uniform sampler2D shadowMap;

// Constants 
vec2 poissonDisk[4] = vec2[](
  vec2( -0.94201624, -0.39906216 ),
  vec2( 0.94558609, -0.76890725 ),
  vec2( -0.094184101, -0.92938870 ),
  vec2( 0.34495938, 0.29387760 )
);

void main() {
    // shadow 
    float bias = 0.005;
    float visibility = 1.0;
    for (int i = 0; i < 4 ; i++) {
        if ((shadowCoord.x < 0) || (shadowCoord.x > 1) || (shadowCoord.y < 0) || (shadowCoord.y > 1))
            continue;
        if (texture( shadowMap, shadowCoord.xy + poissonDisk[i] / light.shadow_poisson_sampling_denominator ).r  <  shadowCoord.z-bias ){
            visibility -= light.shadow_intensity;
        }
    }
    vec3 color = albedo * visibility;

    fragColor = vec4(color, 1.0);
}










