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
  },
  vad: {
    // Enable or disable Voice Activity Detection
    enabled: true,
    // Sensitivity of the Voice Activity Detection (0.0 to 1.0). Lower is more sensitive. Default is 0.5.
    positiveSpeechThreshold: 0.9,
    // Must be lower than positiveSpeechThreshold
    negativeSpeechThreshold: 0.8,
    // Minimum number of consecutive frames (approx 30ms each) to be considered speech. Increase to filter short noises.
    minSpeechFrames: 10,
    // Number of frames of silence to allow before ending the speech segment.
    redemptionFrames: 10
  }
};
