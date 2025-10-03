// 3D Earth Model for Aurora Prediction
let scene, camera, renderer, earth, raycaster, mouse
let selectedLat = null
let selectedLon = null
let marker = null
let isInitialized = false

const THREE = window.THREE // Declare the THREE variable

function initEarth3D() {
  console.log("[v0] initEarth3D called")
  console.log("[v0] THREE available:", typeof THREE !== "undefined")

  // Check if THREE is available
  if (typeof THREE === "undefined") {
    console.error("[v0] THREE.js not loaded yet, retrying...")
    setTimeout(initEarth3D, 100)
    return
  }

  const container = document.getElementById("earth3D")
  console.log("[v0] Earth container found:", !!container)
  console.log("[v0] Container dimensions:", container?.clientWidth, "x", container?.clientHeight)

  if (!container) {
    console.log("[v0] Earth container not found, will retry when page changes")
    return
  }

  if (container.querySelector("canvas")) {
    console.log("[v0] Removing existing canvas")
    container.innerHTML = ""
  }

  console.log("[v0] Initializing Earth 3D model...")

  // Scene setup
  scene = new THREE.Scene()

  // Camera setup
  const width = container.clientWidth
  const height = container.clientHeight
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.z = 3

  console.log("[v0] Camera setup with aspect:", width / height)

  // Renderer setup
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setClearColor(0x000000, 0)
  container.appendChild(renderer.domElement)

  console.log("[v0] Renderer created and canvas appended")
  console.log("[v0] Canvas dimensions:", renderer.domElement.width, "x", renderer.domElement.height)

  // Create Earth sphere
  const geometry = new THREE.SphereGeometry(1, 64, 64)

  const textureLoader = new THREE.TextureLoader()
  const earthTexture = textureLoader.load(
    "https://unpkg.com/three-globe@2.31.0/example/img/earth-blue-marble.jpg",
    () => {
      console.log("[v0] Earth texture loaded successfully")
    },
    undefined,
    (error) => {
      console.error("[v0] Error loading Earth texture:", error)
    },
  )

  const material = new THREE.MeshPhongMaterial({
    map: earthTexture,
    shininess: 10,
    transparent: false,
  })

  earth = new THREE.Mesh(geometry, material)
  scene.add(earth)

  // Add atmosphere glow
  const atmosphereGeometry = new THREE.SphereGeometry(1.05, 64, 64)
  const atmosphereMaterial = new THREE.MeshBasicMaterial({
    color: 0x64ffda,
    transparent: true,
    opacity: 0.2,
    side: THREE.BackSide,
  })
  const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial)
  scene.add(atmosphere)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 3, 5)
  scene.add(directionalLight)

  // Raycaster for click detection
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()

  // Event listeners
  renderer.domElement.addEventListener("click", onEarthClick)
  window.addEventListener("resize", onWindowResize)

  isInitialized = true
  console.log("[v0] Earth 3D initialization complete!")

  // Animation loop
  animate()
}

// Handle window resize
function onWindowResize() {
  const container = document.getElementById("earth3D")
  if (!container) return

  camera.aspect = container.clientWidth / container.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(container.clientWidth, container.clientHeight)
}

// Handle Earth click
function onEarthClick(event) {
  const container = document.getElementById("earth3D")
  const rect = container.getBoundingClientRect()

  // Calculate mouse position in normalized device coordinates
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  // Update raycaster
  raycaster.setFromCamera(mouse, camera)

  // Check for intersections
  const intersects = raycaster.intersectObject(earth)

  if (intersects.length > 0) {
    const point = intersects[0].point

    // Normalize the point to get direction vector
    const normalized = point.clone().normalize()

    // Convert 3D point to lat/lon using proper spherical coordinates
    // Latitude: angle from equator (-90 to +90)
    const lat = Math.asin(normalized.y) * (180 / Math.PI)

    // Longitude: angle around the equator (-180 to +180)
    const lon = Math.atan2(normalized.x, normalized.z) * (180 / Math.PI)

    selectedLat = lat
    selectedLon = lon

    // Add marker at clicked location
    addMarker(point)

    // Enable predict button
    document.getElementById("predictAuroraBtn").disabled = false

    console.log(`[v0] Selected location: Lat ${lat.toFixed(2)}, Lon ${lon.toFixed(2)}`)
    console.log(`[v0] 3D point:`, point)
    console.log(`[v0] Normalized:`, normalized)
  }
}

// Add marker at selected location
function addMarker(point) {
  // Remove existing marker
  if (marker) {
    earth.remove(marker)
  }

  // Create new marker
  const markerGeometry = new THREE.SphereGeometry(0.03, 16, 16)
  const markerMaterial = new THREE.MeshBasicMaterial({
    color: 0xff4081,
    emissive: 0xff4081,
    emissiveIntensity: 0.5,
  })
  marker = new THREE.Mesh(markerGeometry, markerMaterial)

  const localPoint = earth.worldToLocal(point.clone())
  marker.position.copy(localPoint).multiplyScalar(1.02)

  earth.add(marker)

  // Add pulsing animation to marker
  marker.userData.pulsePhase = 0
}

// Animation loop
function animate() {
  requestAnimationFrame(animate)

  // Rotate Earth slowly
  if (earth) {
    earth.rotation.y += 0.001
  }

  // Pulse marker
  if (marker) {
    marker.userData.pulsePhase += 0.05
    const scale = 1 + Math.sin(marker.userData.pulsePhase) * 0.3
    marker.scale.set(scale, scale, scale)
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

function checkAndInitEarth() {
  const predictionPage = document.getElementById("prediction")
  const container = document.getElementById("earth3D")

  console.log(
    "[v0] Checking Earth init - Page active:",
    predictionPage?.classList.contains("active"),
    "Container exists:",
    !!container,
    "Container visible:",
    container?.offsetParent !== null,
  )

  if (predictionPage && predictionPage.classList.contains("active")) {
    if (container && !container.querySelector("canvas")) {
      console.log("[v0] Prediction page is active, initializing Earth 3D...")
      setTimeout(initEarth3D, 200)
    }
  }
}

window.addEventListener("load", () => {
  console.log("[v0] Window loaded, checking for prediction page...")
  checkAndInitEarth()
})

document.addEventListener("DOMContentLoaded", () => {
  console.log("[v0] DOM loaded, setting up Earth observer...")

  // Check immediately
  checkAndInitEarth()

  // Watch for page changes
  const observer = new MutationObserver(() => {
    checkAndInitEarth()
  })

  const pages = document.querySelectorAll(".page")
  pages.forEach((page) => {
    observer.observe(page, { attributes: true, attributeFilter: ["class"] })
  })
})

window.initEarth3D = initEarth3D

// Export for use in main.js
window.getSelectedLocation = () => ({
  latitude: selectedLat,
  longitude: selectedLon,
})
