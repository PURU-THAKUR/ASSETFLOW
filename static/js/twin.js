// ============================================
// AssetFlow AI - Digital Twin JavaScript
// Three.js 3D Visualization
// ============================================

let scene, camera, renderer, controls;
let assetObjects = [];
let selectedAsset = null;
let autoRotate = true;

// ============================================
// Initialize Three.js Scene
// ============================================
function initTwinScene() {
    const container = document.getElementById('threejs-container');
    if (!container) return;
    
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    
    // Camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 1000);
    camera.position.set(12, 10, 12);
    camera.lookAt(0, 0, 0);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.appendChild(renderer.domElement);
    
    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.0;
    controls.minDistance = 3;
    controls.maxDistance = 30;
    controls.target.set(0, 0, 0);
    controls.update();
    
    // Lights
    setupLights();
    
    // Ground
    createGround();
    
    // Grid
    createGrid();
    
    // Load assets
    loadTwinAssets();
    
    // Resize handler
    window.addEventListener('resize', onResize);
    
    // Start animation loop
    animate();
    
    console.log('🌌 Digital Twin scene initialized');
}

// ============================================
// Setup Lighting
// ============================================
function setupLights() {
    // Ambient
    const ambient = new THREE.AmbientLight(0x404060, 0.6);
    scene.add(ambient);
    
    // Main directional light
    const mainLight = new THREE.DirectionalLight(0xffffff, 1.2);
    mainLight.position.set(10, 20, 10);
    mainLight.castShadow = true;
    mainLight.shadow.mapSize.width = 1024;
    mainLight.shadow.mapSize.height = 1024;
    scene.add(mainLight);
    
    // Fill light
    const fillLight = new THREE.DirectionalLight(0x6C63FF, 0.4);
    fillLight.position.set(-10, 5, -10);
    scene.add(fillLight);
    
    // Rim light
    const rimLight = new THREE.DirectionalLight(0x00D4FF, 0.3);
    rimLight.position.set(0, -5, 10);
    scene.add(rimLight);
}

// ============================================
// Create Ground
// ============================================
function createGround() {
    const groundGeometry = new THREE.PlaneGeometry(20, 20);
    const groundMaterial = new THREE.MeshStandardMaterial({
        color: 0x0a0a1a,
        roughness: 0.8,
        metalness: 0.2,
        transparent: true,
        opacity: 0.8
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.5;
    ground.receiveShadow = true;
    scene.add(ground);
}

// ============================================
// Create Grid
// ============================================
function createGrid() {
    const gridHelper = new THREE.GridHelper(16, 16, 0x6C63FF, 0x2a2a4a);
    gridHelper.position.y = -0.45;
    scene.add(gridHelper);
}

// ============================================
// Load Assets for Digital Twin
// ============================================
function loadTwinAssets() {
    fetch('/digital-twin/api/assets')
        .then(response => response.json())
        .then(data => {
            assetObjects = data;
            createAssetObjects(data);
            updateStats(data);
        })
        .catch(() => {
            // Fallback: generate sample assets
            assetObjects = generateSampleAssets();
            createAssetObjects(assetObjects);
            updateStats(assetObjects);
        });
}

// ============================================
// Create 3D Asset Objects
// ============================================
function createAssetObjects(assetData) {
    const colors = {
        'Available': 0x00E676,
        'Allocated': 0x00D4FF,
        'Maintenance': 0xFFB300,
        'Lost': 0xFF1744
    };
    
    const spacing = 2.5;
    const cols = 8;
    
    assetData.forEach((asset, index) => {
        const row = Math.floor(index / cols);
        const col = index % cols;
        
        const x = (col - (cols - 1) / 2) * spacing;
        const z = (row - (assetData.length / cols - 1) / 2) * spacing;
        
        // Create geometry based on asset type
        let geometry;
        const size = 0.6;
        const category = asset.category || 'Laptop';
        
        switch(category.toLowerCase()) {
            case 'laptop':
            case 'desktop':
                geometry = new THREE.BoxGeometry(size, size * 0.6, size * 0.8);
                break;
            case 'printer':
                geometry = new THREE.BoxGeometry(size * 0.8, size * 0.5, size * 0.6);
                break;
            case 'projector':
                geometry = new THREE.BoxGeometry(size * 0.7, size * 0.4, size * 0.9);
                break;
            case 'tablet':
                geometry = new THREE.BoxGeometry(size * 0.5, size * 0.7, size * 0.3);
                break;
            case 'vehicle':
                geometry = new THREE.BoxGeometry(size * 0.8, size * 0.4, size * 1.2);
                break;
            default:
                geometry = new THREE.SphereGeometry(size * 0.5, 16, 16);
        }
        
        const color = colors[asset.status] || 0x6C63FF;
        const material = new THREE.MeshStandardMaterial({
            color: color,
            roughness: 0.3,
            metalness: 0.7,
            emissive: new THREE.Color(color).multiplyScalar(0.1),
            emissiveIntensity: 0.3
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(x, 0, z);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData = asset;
        
        // Add glow ring
        const ringGeometry = new THREE.RingGeometry(size * 0.6, size * 0.8, 32);
        const ringMaterial = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.2,
            side: THREE.DoubleSide
        });
        const ring = new THREE.Mesh(ringGeometry, ringMaterial);
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = -0.4;
        mesh.add(ring);
        
        // Add label (sprite)
        const label = createLabel(asset.tag);
        label.position.y = size * 0.8 + 0.3;
        mesh.add(label);
        
        // Click handler
        mesh.userData.clickHandler = function() {
            selectAsset(asset);
        };
        
        scene.add(mesh);
    });
}

// ============================================
// Create Label Sprite
// ============================================
function createLabel(text) {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 48;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.beginPath();
    ctx.roundRect(0, 0, 128, 48, 8);
    ctx.fill();
    
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 18px Inter, sans-serif';
    ctx.fillText(text, 64, 26);
    
    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: false
    });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(2, 0.75, 1);
    
    return sprite;
}

// ============================================
// Select Asset
// ============================================
function selectAsset(asset) {
    selectedAsset = asset;
    updateAssetDetails(asset);
    
    // Highlight selected
    scene.children.forEach(child => {
        if (child.isMesh && child.userData && child.userData.id === asset.id) {
            child.material.emissiveIntensity = 0.8;
        } else if (child.isMesh) {
            child.material.emissiveIntensity = 0.1;
        }
    });
}

// ============================================
// Update Asset Details Panel
// ============================================
function updateAssetDetails(asset) {
    document.getElementById('detailName').textContent = asset.name || '-';
    document.getElementById('detailTag').textContent = asset.tag || '-';
    document.getElementById('detailStatus').textContent = asset.status || '-';
    document.getElementById('detailLocation').textContent = asset.location || '-';
    document.getElementById('detailDepartment').textContent = asset.department || '-';
    document.getElementById('detailHealth').textContent = asset.health_score ? `${asset.health_score}%` : '-';
}

// ============================================
// Update Stats
// ============================================
function updateStats(assetData) {
    const stats = {
        available: 0,
        allocated: 0,
        maintenance: 0,
        lost: 0
    };
    
    assetData.forEach(asset => {
        const status = asset.status?.toLowerCase() || '';
        if (stats.hasOwnProperty(status)) {
            stats[status]++;
        }
    });
    
    document.querySelector('.stat-item .green + span').textContent = `Available: ${stats.available}`;
    document.querySelector('.stat-item .blue + span').textContent = `Allocated: ${stats.allocated}`;
    document.querySelector('.stat-item .yellow + span').textContent = `Maintenance: ${stats.maintenance}`;
    document.querySelector('.stat-item .red + span').textContent = `Lost: ${stats.lost}`;
}

// ============================================
// Filter by Department
// ============================================
function filterDepartment(dept) {
    const btns = document.querySelectorAll('.twin-filters .filter-btn');
    btns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.trim().toLowerCase() === dept) {
            btn.classList.add('active');
        }
    });
    
    if (dept === 'all') {
        scene.children.forEach(child => {
            if (child.isMesh) child.visible = true;
        });
        return;
    }
    
    scene.children.forEach(child => {
        if (child.isMesh && child.userData && child.userData.department) {
            child.visible = child.userData.department.toLowerCase() === dept.toLowerCase();
        } else if (child.isMesh) {
            child.visible = false;
        }
    });
}

// ============================================
// Controls
// ============================================
function resetCamera() {
    camera.position.set(12, 10, 12);
    controls.target.set(0, 0, 0);
    controls.update();
}

function toggleAutoRotate() {
    autoRotate = !autoRotate;
    controls.autoRotate = autoRotate;
    const btn = document.querySelector('.twin-controls button:nth-child(2)');
    if (btn) {
        btn.textContent = autoRotate ? '⏸️ Auto Rotate' : '▶️ Auto Rotate';
    }
}

function toggleLabels() {
    let visible = true;
    scene.children.forEach(child => {
        if (child.isSprite) {
            visible = !child.visible;
            child.visible = visible;
        }
    });
}

// ============================================
// Resize Handler
// ============================================
function onResize() {
    const container = document.getElementById('threejs-container');
    if (!container) return;
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

// ============================================
// Animation Loop
// ============================================
function animate() {
    requestAnimationFrame(animate);
    
    // Animate floating effect
    const time = Date.now() * 0.001;
    scene.children.forEach((child, index) => {
        if (child.isMesh && child.userData && child.userData.id) {
            const offset = index * 0.1;
            child.position.y = Math.sin(time * 0.5 + offset) * 0.1;
            
            // Rotate ring
            const ring = child.children.find(c => c.isMesh && c.geometry.type === 'RingGeometry');
            if (ring) {
                ring.rotation.z = time * 0.2 + offset;
            }
        }
    });
    
    controls.update();
    renderer.render(scene, camera);
}

// ============================================
// Generate Sample Assets (Fallback)
// ============================================
function generateSampleAssets() {
    const departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations'];
    const statuses = ['Available', 'Allocated', 'Maintenance', 'Lost'];
    const categories = ['Laptop', 'Desktop', 'Printer', 'Projector', 'Tablet'];
    const locations = ['Floor 1', 'Floor 2', 'Floor 3', 'Floor 4'];
    
    const assets = [];
    for (let i = 0; i < 40; i++) {
        assets.push({
            id: i + 1,
            tag: `AF-${String(i + 1).padStart(4, '0')}`,
            name: `${categories[i % categories.length]} ${i + 1}`,
            category: categories[i % categories.length],
            status: statuses[i % statuses.length],
            department: departments[i % departments.length],
            location: locations[i % locations.length],
            health_score: Math.floor(Math.random() * 40) + 60
        });
    }
    return assets;
}

// ============================================
// Initialize on Page Load
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the digital twin page
    if (document.getElementById('threejs-container')) {
        // Load Three.js dynamically if not loaded
        if (typeof THREE === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
            script.onload = function() {
                loadOrbitControls();
            };
            document.head.appendChild(script);
        } else {
            loadOrbitControls();
        }
    }
});

function loadOrbitControls() {
    if (typeof THREE.OrbitControls === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js';
        script.onload = function() {
            initTwinScene();
        };
        document.head.appendChild(script);
    } else {
        initTwinScene();
    }
}

console.log('🌌 Digital Twin 3D module loaded successfully!');