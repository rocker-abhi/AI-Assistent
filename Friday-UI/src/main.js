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
  
  // Expose a method to change background color based on status
  const updateBackgroundStatus = (isOffline) => {
    // 0x330000 is a dark red color. 0x000000 is black.
    scene.background.setHex(isOffline ? 0x220000 : 0x000000);
  };

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
  controls.enableRotate = false;
  controls.enablePan = false;
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
  
  // Initialize chat and pass the background updater callback
  setupChat(updateBackgroundStatus);
};

// --- WebSocket and Chat UI Integration ---
const setupChat = (onStatusChange) => {
  // Connect to the FastAPI backend we just set up
  const wsUrl = `ws://127.0.0.1:8000/ws/friday-frontend`;
  const ws = new WebSocket(wsUrl);

  // Safely close the websocket if Vite hot-reloads the file (prevents zombie connections)
  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      ws.close();
    });
  }

  const messagesContainer = document.getElementById('chat-messages');
  const inputElement = document.getElementById('chat-input');
  const sendButton = document.getElementById('chat-send');

  // Clear the hardcoded mock messages from index.html
  if (messagesContainer) {
    messagesContainer.innerHTML = '';
  }

  // Helper to dynamically append messages to the chat UI
  const addMessage = (text, isUser) => {
    if (!messagesContainer) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-msg' : 'system-msg'}`;
    msgDiv.textContent = text;
    messagesContainer.appendChild(msgDiv);
    
    // Auto-scroll to the latest message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  };

  // WebSocket Event Listeners
  ws.onopen = () => {
    onStatusChange(false);
    const banner = document.getElementById('status-banner');
    if (banner) banner.style.display = 'none';
    const chat = document.getElementById('chat-container');
    if (chat) chat.style.display = 'flex';
  };

  let currentSystemMessageDiv = null;
  const audioQueue = [];
  let isPlayingAudio = false;

  const playNextAudio = () => {
    if (audioQueue.length === 0) {
      isPlayingAudio = false;
      return;
    }
    isPlayingAudio = true;
    const base64Audio = audioQueue.shift();
    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    audio.onended = playNextAudio;
    audio.play().catch(e => {
      console.error("Audio playback error:", e);
      playNextAudio();
    });
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'text') {
        if (!currentSystemMessageDiv) {
          currentSystemMessageDiv = document.createElement('div');
          currentSystemMessageDiv.className = 'message system-msg';
          messagesContainer.appendChild(currentSystemMessageDiv);
        }
        currentSystemMessageDiv.textContent += data.data;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      } else if (data.type === 'audio') {
        audioQueue.push(data.data);
        if (!isPlayingAudio) {
          playNextAudio();
        }
      } else if (data.message && data.status !== "received") {
        addMessage(data.message, false);
      }
    } catch (e) {
      // Fallback if the backend sends raw text
      addMessage(event.data, false);
    }
  };

  ws.onclose = () => {
    onStatusChange(true);
    const banner = document.getElementById('status-banner');
    if (banner) banner.style.display = 'block';
    const chat = document.getElementById('chat-container');
    if (chat) chat.style.display = 'none';
  };
  
  ws.onerror = () => {
    onStatusChange(true);
    const banner = document.getElementById('status-banner');
    if (banner) banner.style.display = 'block';
    const chat = document.getElementById('chat-container');
    if (chat) chat.style.display = 'none';
  };

  // UI Event Listeners for sending messages
  const sendMessage = () => {
    const text = inputElement.value.trim();
    if (text && ws.readyState === WebSocket.OPEN) {
      addMessage(text, true); // Instantly show user message
      currentSystemMessageDiv = null; // Reset system bubble for next response
      const messagePayload = {
        type: "message",
        message_type: "text",
        message_id: "msg_" + Date.now(),
        content: { text: text },
        timestamp: new Date().toISOString()
      };
      ws.send(JSON.stringify(messagePayload)); // Send to FastAPI backend
      inputElement.value = ''; // Clear input
    }
  };

  if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
  }
  
  if (inputElement) {
    inputElement.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  }
};

// Start the application
init();
