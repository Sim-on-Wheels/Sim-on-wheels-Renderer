#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 light_dir;
in vec3 view_dir;
in vec3 albedo; 
in float metallic;
in float roughness;
in vec4 shadowCoord;

struct Light {
    vec3 direction;
    vec3 color;
    float light_intensity;
    float ambient_intensity;
    float shadow_intensity;
    float shadow_poisson_sampling_denominator;
    float gamma_correction;
};
uniform Light light;
uniform sampler2D shadowMap;

// Constants 
const float PI = 3.14159265359;
vec2 poissonDisk[4] = vec2[](
  vec2( -0.94201624, -0.39906216 ),
  vec2( 0.94558609, -0.76890725 ),
  vec2( -0.094184101, -0.92938870 ),
  vec2( 0.34495938, 0.29387760 )
);

vec3 fresnelSchlick(float cosTheta, vec3 F0)
{
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

float DistributionGGX(vec3 N, vec3 H, float roughness)
{
    float a      = roughness*roughness;
    float a2     = a*a;
    float NdotH  = max(dot(N, H), 0.0);
    float NdotH2 = NdotH*NdotH;
	
    float num   = a2;
    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;
	
    return num / denom;
}

float GeometrySchlickGGX(float inner_prod, float roughness)
{
    float r = (roughness + 1.0);
    float k = (r*r) / 8.0;

    float num   = inner_prod;
    float denom = inner_prod * (1.0 - k) + k;
	
    return num / denom;
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness)
{
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    float ggx2  = GeometrySchlickGGX(NdotV, roughness);
    float ggx1  = GeometrySchlickGGX(NdotL, roughness);
	
    return ggx1 * ggx2;
}

void main() {
    // Parameters
    vec3 radiance = light.color * light.light_intensity;

    vec3 N = normalize(normal);
    vec3 L = normalize(light.direction);
    vec3 V = normalize(view_dir);
    vec3 H = normalize(L + V);
    
    // Reflection ratio 
    vec3 F0 = vec3(0.04); 
    F0      = mix(F0, albedo, metallic);
    vec3 F  = fresnelSchlick(max(dot(H, V), 0.0), F0);

    // Specular 
    float NDF = DistributionGGX(N, H, roughness);
    float G   = GeometrySmith(N, V, L, roughness);
    vec3 numerator    = NDF * G * F;
    float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0)  + 0.0001;
    vec3 specular     = numerator / denominator;
    
    // Aggregate
    vec3 ks = F;
    vec3 kd = vec3(1.0) - ks;
    kd *= 1.0 - metallic;

    float NdotL = max(dot(N, L), 0.0);        
    vec3 Lo = (kd * albedo / PI + specular) * radiance * NdotL;
    vec3 ambient = vec3(light.ambient_intensity) * albedo;
    vec3 color = Lo + ambient;

    // Gamma correction
    color = color / (color + vec3(1.0));
    color = pow(color, vec3(light.gamma_correction)); 

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
    color = color * visibility;

    fragColor = vec4(color, 1.0);
}










