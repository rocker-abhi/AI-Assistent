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
    
    while (messagesContainer.children.length > 25) {
      messagesContainer.removeChild(messagesContainer.firstChild);
    }
    
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

  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 512;
  analyser.connect(audioCtx.destination);
  
  const micAnalyser = audioCtx.createAnalyser();
  micAnalyser.fftSize = 512;
  
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      const micSource = audioCtx.createMediaStreamSource(stream);
      micSource.connect(micAnalyser);
    }).catch(err => {
      console.warn("Mic access denied/unavailable. Chat visualizer will be flat.", err);
    });
  }
  
  const canvas = document.getElementById('audio-visualizer');
  const canvasCtx = canvas.getContext('2d');
  
  const chatCanvas = document.getElementById('chat-audio-visualizer');
  const chatCanvasCtx = chatCanvas.getContext('2d');
  
  const resizeCanvas = () => {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    chatCanvas.width = chatCanvas.parentElement.clientWidth;
    chatCanvas.height = chatCanvas.parentElement.clientHeight;
  };
  window.addEventListener('resize', resizeCanvas);
  setTimeout(resizeCanvas, 100);

  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);
  
  const micBufferLength = micAnalyser.frequencyBinCount;
  const micDataArray = new Uint8Array(micBufferLength);
  
  const drawVisualizer = () => {
    requestAnimationFrame(drawVisualizer);
    
    analyser.getByteTimeDomainData(dataArray);
    micAnalyser.getByteTimeDomainData(micDataArray);
    
    // Draw on main visualizer
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.lineWidth = 4;
    canvasCtx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
    canvasCtx.beginPath();
    
    const sliceWidth = canvas.width * 1.0 / bufferLength;
    let x = 0;
    
    for(let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = v * canvas.height / 2;
      
      if(i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }
      x += sliceWidth;
    }
    
    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
    
    // Draw on chat visualizer
    chatCanvasCtx.clearRect(0, 0, chatCanvas.width, chatCanvas.height);
    chatCanvasCtx.lineWidth = 2; // thinner line for the smaller chat window
    chatCanvasCtx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
    chatCanvasCtx.beginPath();
    
    const chatSliceWidth = chatCanvas.width * 1.0 / micBufferLength;
    let chatX = 0;
    
    for(let i = 0; i < micBufferLength; i++) {
      const v = micDataArray[i] / 128.0;
      const y = v * chatCanvas.height / 2;
      
      if(i === 0) {
        chatCanvasCtx.moveTo(chatX, y);
      } else {
        chatCanvasCtx.lineTo(chatX, y);
      }
      chatX += chatSliceWidth;
    }
    
    chatCanvasCtx.lineTo(chatCanvas.width, chatCanvas.height / 2);
    chatCanvasCtx.stroke();
  };
  drawVisualizer();
  // ----------------------------------------

  const playNextAudio = async () => {
    if (audioQueue.length === 0) {
      isPlayingAudio = false;
      return;
    }
    isPlayingAudio = true;
    const base64Audio = audioQueue.shift();
    
    try {
      if (audioCtx.state === 'suspended') {
        await audioCtx.resume();
      }
      
      const binaryString = window.atob(base64Audio);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      const audioBuffer = await audioCtx.decodeAudioData(bytes.buffer);
      const source = audioCtx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(analyser);
      
      source.onended = playNextAudio;
      source.start(0);
    } catch (e) {
      console.error("Audio playback error:", e);
      playNextAudio();
    }
  };

  const setProcessing = (isProcessing) => {
    const sendBtn = document.getElementById('chat-send');
    const loadingBtn = document.getElementById('chat-loading');
    const thinkingBanner = document.getElementById('thinking-banner');
    
    if (isProcessing) {
      if (sendBtn) sendBtn.style.display = 'none';
      if (loadingBtn) loadingBtn.style.display = 'block';
      if (thinkingBanner) thinkingBanner.style.display = 'block';
    } else {
      if (sendBtn) sendBtn.style.display = 'block';
      if (loadingBtn) loadingBtn.style.display = 'none';
      if (thinkingBanner) thinkingBanner.style.display = 'none';
    }
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'history') {
        if (data.data && Array.isArray(data.data)) {
          const historyMessages = data.data.slice(-25);
          for (const msg of historyMessages) {
            addMessage(msg.content, msg.role === 'user');
          }
        }
      } else if (data.type === 'text') {
        if (!currentSystemMessageDiv) {
          currentSystemMessageDiv = document.createElement('div');
          currentSystemMessageDiv.className = 'message system-msg';
          messagesContainer.appendChild(currentSystemMessageDiv);
          
          while (messagesContainer.children.length > 25) {
            messagesContainer.removeChild(messagesContainer.firstChild);
          }
        }
        currentSystemMessageDiv.textContent += data.data;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      } else if (data.type === 'audio') {
        audioQueue.push(data.data);
        if (!isPlayingAudio) {
          playNextAudio();
        }
      } else if (data.type === 'done') {
        setProcessing(false);
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
      setProcessing(true); // Show thinking UI
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
