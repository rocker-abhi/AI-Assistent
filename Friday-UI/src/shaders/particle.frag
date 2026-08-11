precision highp float;

varying vec3 vColor;
varying float vDisplacement;

void main() {
    // Create a circular particle
    float distanceToCenter = distance(gl_PointCoord, vec2(0.5));
    if (distanceToCenter > 0.5) {
        discard;
    }
    
    // Soft edge for glow effect
    float alpha = 1.0 - (distanceToCenter * 2.0);
    alpha = pow(alpha, 2.0) * 0.7; // sharper falloff and lower max opacity to prevent whiteout

    // Mix color based on displacement (brighter at peaks)
    vec3 finalColor = vColor;
    if (vDisplacement > 0.2) {
        finalColor += vec3(0.2) * (vDisplacement - 0.2);
    }
    
    gl_FragColor = vec4(finalColor, alpha);
}
