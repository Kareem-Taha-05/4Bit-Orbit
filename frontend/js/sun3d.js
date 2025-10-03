let sunScene,
  sunCamera,
  sunRenderer,
  sun,
  sunSpots = [],
  solarFlares = []
let animationId = null
let isSunInitialized = false
const THREE = window.THREE

// Initialize 3D Sun
function initSun3D() {
  console.log("[v0] initSun3D called")

  if (typeof THREE === "undefined") {
    console.error("[v0] THREE.js not loaded yet for Sun, retrying...")
    setTimeout(initSun3D, 100)
    return
  }

  const container = document.getElementById("sun3D")
  if (!container) {
    console.log("[v0] Sun container not found")
    return
  }

  if (isSunInitialized && container.querySelector("canvas")) {
    console.log("[v0] Sun 3D already initialized")
    return
  }

  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.log("[v0] Sun container has no dimensions yet, retrying...")
    setTimeout(initSun3D, 200)
    return
  }

  console.log("[v0] Initializing Sun 3D model...")
  container.innerHTML = ""

  // Scene setup
  sunScene = new THREE.Scene()
  sunScene.background = null

  // Camera setup
  sunCamera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000)
  sunCamera.position.z = 4

  // Renderer setup
  sunRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  sunRenderer.setSize(container.clientWidth, container.clientHeight)
  sunRenderer.setClearColor(0x000000, 0)
  container.appendChild(sunRenderer.domElement)

  // Create Sun sphere
  const geometry = new THREE.SphereGeometry(1.5, 64, 64)
  const textureLoader = new THREE.TextureLoader()
  const sunTexture = textureLoader.load(
    "https://www.solarsystemscope.com/textures/download/2k_sun.jpg",
    () => console.log("[v0] Sun texture loaded"),
    undefined,
    (error) => {
      console.error("[v0] Error loading Sun texture:", error)
      sun.material.color.setHex(0xffd700)
    },
  )

  const material = new THREE.MeshBasicMaterial({
    map: sunTexture,
    emissive: 0xffd700,
    emissiveIntensity: 0.6,
  })

  sun = new THREE.Mesh(geometry, material)
  sunScene.add(sun)

  // Add corona glow layers
  const coronaGeometry = new THREE.SphereGeometry(1.7, 64, 64)
  const coronaMaterial = new THREE.MeshBasicMaterial({
    color: 0xffd700,
    transparent: true,
    opacity: 0.2,
    side: THREE.BackSide,
  })
  const corona = new THREE.Mesh(coronaGeometry, coronaMaterial)
  sunScene.add(corona)

  const glowGeometry = new THREE.SphereGeometry(1.9, 64, 64)
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0xffa500,
    transparent: true,
    opacity: 0.1,
    side: THREE.BackSide,
  })
  const glow = new THREE.Mesh(glowGeometry, glowMaterial)
  sunScene.add(glow)

  // Add point light for glow effect
  const pointLight = new THREE.PointLight(0xffd700, 2, 10)
  pointLight.position.set(0, 0, 0)
  sunScene.add(pointLight)

  addDefaultSunspots()

  window.addEventListener("resize", onSunWindowResize)

  isSunInitialized = true
  console.log("[v0] Sun 3D initialization complete!")

  animateSun()
}

function onSunWindowResize() {
  const container = document.getElementById("sun3D")
  if (!container || !sunCamera || !sunRenderer) return

  sunCamera.aspect = container.clientWidth / container.clientHeight
  sunCamera.updateProjectionMatrix()
  sunRenderer.setSize(container.clientWidth, container.clientHeight)
}

// Add sunspot to the Sun
function addSunspot(lat, lon, size, intensity) {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)
  const radius = 1.52

  const x = -(radius * Math.sin(phi) * Math.cos(theta))
  const y = radius * Math.cos(phi)
  const z = radius * Math.sin(phi) * Math.sin(theta)

  const spotGeometry = new THREE.SphereGeometry(size * 0.1, 16, 16)
  const spotMaterial = new THREE.MeshBasicMaterial({
    color: 0x331100,
    transparent: true,
    opacity: intensity,
  })
  const spot = new THREE.Mesh(spotGeometry, spotMaterial)
  spot.position.set(x, y, z)

  sunScene.add(spot)
  sunSpots.push(spot)

  return spot
}

// Add solar flare effect
function addSolarFlare(lat, lon, intensity, type) {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)
  const radius = 1.55

  const x = -(radius * Math.sin(phi) * Math.cos(theta))
  const y = radius * Math.cos(phi)
  const z = radius * Math.sin(phi) * Math.sin(theta)

  const particleCount = 100
  const particles = new THREE.BufferGeometry()
  const positions = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount; i++) {
    const angle = (i / particleCount) * Math.PI * 2
    const distance = Math.random() * 0.5
    positions[i * 3] = x + Math.cos(angle) * distance
    positions[i * 3 + 1] = y + Math.sin(angle) * distance
    positions[i * 3 + 2] = z + (Math.random() - 0.5) * 0.3
  }

  particles.setAttribute("position", new THREE.BufferAttribute(positions, 3))

  let flareColor
  if (type === "X") {
    flareColor = 0xff0000
  } else if (type === "M") {
    flareColor = 0xff6600
  } else {
    flareColor = 0xffff00
  }

  const particleMaterial = new THREE.PointsMaterial({
    color: flareColor,
    size: 0.08,
    transparent: true,
    opacity: intensity,
    blending: THREE.AdditiveBlending,
  })

  const flare = new THREE.Points(particles, particleMaterial)
  sunScene.add(flare)
  solarFlares.push(flare)

  animateFlare(flare, 3000)

  return flare
}

function animateFlare(flare, duration) {
  const startTime = Date.now()
  const startOpacity = flare.material.opacity

  function update() {
    const elapsed = Date.now() - startTime
    const progress = elapsed / duration

    if (progress < 1) {
      flare.material.opacity = startOpacity * (1 - progress)
      flare.scale.set(1 + progress * 3, 1 + progress * 3, 1 + progress * 3)
      requestAnimationFrame(update)
    } else {
      sunScene.remove(flare)
      const index = solarFlares.indexOf(flare)
      if (index > -1) solarFlares.splice(index, 1)
    }
  }

  update()
}

function clearSunspots() {
  sunSpots.forEach((spot) => sunScene.remove(spot))
  sunSpots = []
}

function clearSolarFlares() {
  solarFlares.forEach((flare) => sunScene.remove(flare))
  solarFlares = []
}

// Update Sun visualization with forecast data
let currentSunState = "normal" // Can be: normal, active, severe

function updateSunVisualization(forecastData) {
  console.log("[v0] Updating Sun visualization with forecast data:", forecastData)

  clearSunspots()
  clearSolarFlares()

  // Determine sun state based on flare probabilities
  const flares = forecastData.flare_probabilities || {}
  let newState = "normal"

  if (flares.x_class > 0.15 || flares.m_class > 0.4) {
    newState = "severe"
  } else if (flares.m_class > 0.2 || flares.c_class > 0.7) {
    newState = "active"
  }

  currentSunState = newState
  console.log("[v0] Sun state changed to:", currentSunState)

  // Update Sun appearance based on state
  if (currentSunState === "severe") {
    // Severe: Many large sunspots, intense glow
    sun.material.emissiveIntensity = 0.9
    const numSpots = Math.floor(Math.random() * 8) + 8 // 8-15 spots
    for (let i = 0; i < numSpots; i++) {
      addSunspot(
        Math.random() * 60 - 30,
        Math.random() * 360 - 180,
        Math.random() * 0.2 + 0.15, // Large spots
        Math.random() * 0.3 + 0.7, // High intensity
      )
    }
  } else if (currentSunState === "active") {
    // Active: Moderate number of medium sunspots
    sun.material.emissiveIntensity = 0.75
    const numSpots = Math.floor(Math.random() * 4) + 5 // 5-8 spots
    for (let i = 0; i < numSpots; i++) {
      addSunspot(
        Math.random() * 50 - 25,
        Math.random() * 360 - 180,
        Math.random() * 0.12 + 0.1, // Medium spots
        Math.random() * 0.3 + 0.5, // Medium intensity
      )
    }
  } else {
    // Normal: Few small sunspots
    sun.material.emissiveIntensity = 0.6
    addDefaultSunspots()
  }

  // Add sunspot regions from API if available
  if (forecastData.sunspot_regions && forecastData.sunspot_regions.length > 0) {
    forecastData.sunspot_regions.forEach((region) => {
      addSunspot(
        region.latitude || Math.random() * 60 - 30,
        region.longitude || Math.random() * 360 - 180,
        region.size || 0.2,
        region.intensity || 0.7,
      )
    })
  }

  // Trigger flares based on probabilities
  if (flares.x_class && flares.x_class > 0.05) {
    const numXFlares = Math.floor(flares.x_class * 3) + (Math.random() < flares.x_class % 1 ? 1 : 0)
    for (let i = 0; i < numXFlares; i++) {
      setTimeout(
        () => {
          addSolarFlare(Math.random() * 60 - 30, Math.random() * 360 - 180, 0.9, "X")
        },
        1000 + i * 1500,
      )
    }
  }

  if (flares.m_class && flares.m_class > 0.1) {
    const numMFlares = Math.floor(flares.m_class * 2) + (Math.random() < flares.m_class % 1 ? 1 : 0)
    for (let i = 0; i < numMFlares; i++) {
      setTimeout(
        () => {
          addSolarFlare(Math.random() * 60 - 30, Math.random() * 360 - 180, 0.7, "M")
        },
        2000 + i * 1200,
      )
    }
  }

  if (flares.c_class && flares.c_class > 0.3) {
    const numCFlares = Math.floor(flares.c_class * 1.5)
    for (let i = 0; i < numCFlares; i++) {
      setTimeout(
        () => {
          addSolarFlare(Math.random() * 60 - 30, Math.random() * 360 - 180, 0.5, "C")
        },
        3000 + i * 1000,
      )
    }
  }
}

function animateSun() {
  animationId = requestAnimationFrame(animateSun)

  if (sun) {
    sun.rotation.y += 0.002
  }

  sunSpots.forEach((spot) => {
    spot.rotation.y += 0.002
  })

  if (sunRenderer && sunScene && sunCamera) {
    sunRenderer.render(sunScene, sunCamera)
  }
}

function stopSunAnimation() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
}

// Add default sunspots for a normal, calm Sun
function addDefaultSunspots() {
  // Add 2-3 small sunspots for a normal, calm Sun
  const numSpots = 2
  for (let i = 0; i < numSpots; i++) {
    addSunspot(
      Math.random() * 40 - 20, // latitude (closer to equator)
      Math.random() * 360 - 180, // longitude
      0.08, // very small size
      0.4, // low intensity
    )
  }
  currentSunState = "normal"
}

// Export functions
window.initSun3D = initSun3D
window.updateSunVisualization = updateSunVisualization
window.clearSunspots = clearSunspots
window.addSolarFlare = addSolarFlare
