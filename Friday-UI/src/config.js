export const config = {
  sphere: {
    // Center position of the particle sphere
    position: { x: -2.5, y: 0, z: 0 },
    // Base radius before noise displacement
    radius: 1.0,
    // Total number of particles
    particleCount: 5500
  },
  camera: {
    // Initial camera position (adjusting Z acts as the fixed zoom distance)
    position: { x: 0, y: 8, z: 4 }
  },
  controls: {
    // Allow the user to zoom in and out with the mouse wheel
    enableZoom: false
  }
};
