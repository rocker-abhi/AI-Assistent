import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { config } from './config.js';

import vertexShader from './shaders/particle.vert?raw';
import fragmentShader from './shaders/particle.frag?raw';

const init = () => {
  const container = document.getElementById('app');

  // Scene setup
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);

  // Camera setup
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(config.camera.position.x, config.camera.position.y, config.camera.position.z);

  // Renderer setup
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  // Controls
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.enableZoom = config.controls.enableZoom;
  controls.target.set(config.sphere.position.x, config.sphere.position.y, config.sphere.position.z);

  // Geometry (sphere distributed particles)
  const particleCount = config.sphere.particleCount;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);

  for (let i = 0; i < particleCount; i++) {
    // Math to distribute points on a sphere (Fibonacci sphere algorithm)
    const phi = Math.acos(1 - 2 * (i + 0.5) / particleCount);
    const theta = Math.PI * (1 + Math.sqrt(5)) * (i + 0.5);

    const r = config.sphere.radius;

    const x = r * Math.sin(phi) * Math.cos(theta);
    const y = r * Math.cos(phi);
    const z = r * Math.sin(phi) * Math.sin(theta);

    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  // Shader Material
  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0.0 }
    },
    transparent: true,
    depthWrite: false, // Prevents z-fighting for transparent particles
    blending: THREE.AdditiveBlending // Gives the glowing effect
  });

  const particles = new THREE.Points(geometry, material);
  
  // Apply position from config
  particles.position.set(config.sphere.position.x, config.sphere.position.y, config.sphere.position.z);
  
  scene.add(particles);

  // Handle window resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation Loop
  const clock = new THREE.Clock();

  const animate = () => {
    requestAnimationFrame(animate);

    const elapsedTime = clock.getElapsedTime();
    
    // Update uniforms
    material.uniforms.uTime.value = elapsedTime;

    // Optional: slowly rotate the whole system
    particles.rotation.y = elapsedTime * 0.1;
    particles.rotation.x = elapsedTime * 0.05;

    controls.update();
    renderer.render(scene, camera);
  };

  animate();
};

init();
