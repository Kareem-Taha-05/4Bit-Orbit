let earthSpaceScene, earthSpaceCamera, earthSpaceRenderer, earthSpace, earthSpaceMarker
let earthSpaceAnimationId = null
let isEarthSpaceInitialized = false
let magnetosphere = null
let currentEarthState = "normal" // Can be: calm, minor, moderate, severe
let stormParticles = [] // Track storm particles for cleanup
const THREE = window.THREE

// Initialize 3D Earth for space weather section
function initEarthSpace3D() {
  console.log("[v0] initEarthSpace3D called")

  if (typeof THREE === "undefined") {
    console.error("[v0] THREE.js not loaded yet for Earth Space, retrying...")
    setTimeout(initEarthSpace3D, 100)
    return
  }

  const container = document.getElementById("earth3DSpace")
  if (!container) {
    console.log("[v0] Earth Space container not found")
    return
  }

  if (isEarthSpaceInitialized && container.querySelector("canvas")) {
    console.log("[v0] Earth Space 3D already initialized")
    return
  }

  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.log("[v0] Earth Space container has no dimensions yet, retrying...")
    setTimeout(initEarthSpace3D, 200)
    return
  }

  console.log("[v0] Initializing Earth Space 3D model...")
  container.innerHTML = ""

  // Scene setup
  earthSpaceScene = new THREE.Scene()
  earthSpaceScene.background = null

  // Camera setup
  earthSpaceCamera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000)
  earthSpaceCamera.position.z = 4

  // Renderer setup
  earthSpaceRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  earthSpaceRenderer.setSize(container.clientWidth, container.clientHeight)
  earthSpaceRenderer.setClearColor(0x000000, 0)
  container.appendChild(earthSpaceRenderer.domElement)

  // Create Earth sphere
  const geometry = new THREE.SphereGeometry(1.2, 64, 64)
  const textureLoader = new THREE.TextureLoader()
  const earthTexture = textureLoader.load(
    "https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg",
    () => console.log("[v0] Earth Space texture loaded"),
    undefined,
    (error) => {
      console.error("[v0] Error loading Earth Space texture:", error)
      earthSpace.material.color.setHex(0x4169e1)
    },
  )

  const material = new THREE.MeshBasicMaterial({
    map: earthTexture,
  })

  earthSpace = new THREE.Mesh(geometry, material)
  earthSpaceScene.add(earthSpace)

  // Add atmosphere glow
  const atmosphereGeometry = new THREE.SphereGeometry(1.3, 64, 64)
  const atmosphereMaterial = new THREE.MeshBasicMaterial({
    color: 0x4169e1,
    transparent: true,
    opacity: 0.15,
    side: THREE.BackSide,
  })
  const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial)
  earthSpaceScene.add(atmosphere)

  // Add magnetosphere (invisible by default, shown during storms)
  const magnetosphereGeometry = new THREE.SphereGeometry(1.6, 32, 32)
  const magnetosphereMaterial = new THREE.MeshBasicMaterial({
    color: 0x64ffda,
    transparent: true,
    opacity: 0, // Start invisible, will show during storms
    side: THREE.BackSide,
    wireframe: true,
  })
  magnetosphere = new THREE.Mesh(magnetosphereGeometry, magnetosphereMaterial)
  earthSpaceScene.add(magnetosphere)

  window.addEventListener("resize", onEarthSpaceWindowResize)

  isEarthSpaceInitialized = true
  console.log("[v0] Earth Space 3D initialization complete!")

  animateEarthSpace()
}

function onEarthSpaceWindowResize() {
  const container = document.getElementById("earth3DSpace")
  if (!container || !earthSpaceCamera || !earthSpaceRenderer) return

  earthSpaceCamera.aspect = container.clientWidth / container.clientHeight
  earthSpaceCamera.updateProjectionMatrix()
  earthSpaceRenderer.setSize(container.clientWidth, container.clientHeight)
}

function updateEarthSpaceVisualization(stormLevel) {
  if (!magnetosphere) return

  console.log("[v0] Updating Earth visualization with storm level:", stormLevel)

  currentEarthState = stormLevel

  // Clear existing storm particles
  stormParticles.forEach((particle) => earthSpaceScene.remove(particle))
  stormParticles = []

  // Update magnetosphere based on storm intensity
  if (stormLevel === "severe") {
    // Severe storm: Bright red magnetosphere, compressed
    magnetosphere.material.opacity = 0.5
    magnetosphere.material.color.setHex(0xff4081) // Bright pink/red
    magnetosphere.scale.set(0.85, 0.85, 1.2) // Compressed by solar wind

    // Add intense storm particles
    addStormParticles(150, 0xff0000, 0.7)
  } else if (stormLevel === "moderate") {
    // Moderate storm: Yellow/orange magnetosphere
    magnetosphere.material.opacity = 0.35
    magnetosphere.material.color.setHex(0xffd700) // Gold
    magnetosphere.scale.set(0.9, 0.9, 1.1)

    // Add moderate storm particles
    addStormParticles(80, 0xffa500, 0.5)
  } else if (stormLevel === "minor") {
    // Minor storm: Green magnetosphere
    magnetosphere.material.opacity = 0.25
    magnetosphere.material.color.setHex(0x64ffda) // Cyan/green
    magnetosphere.scale.set(0.95, 0.95, 1.05)

    // Add light storm particles
    addStormParticles(40, 0x64ffda, 0.3)
  } else {
    // Calm: No visible magnetosphere, normal shape
    magnetosphere.material.opacity = 0
    magnetosphere.scale.set(1, 1, 1)
  }
}

function addStormParticles(count, color, intensity) {
  const particleGeometry = new THREE.BufferGeometry()
  const positions = new Float32Array(count * 3)

  for (let i = 0; i < count; i++) {
    // Create particles in a shell around Earth
    const theta = Math.random() * Math.PI * 2
    const phi = Math.random() * Math.PI
    const radius = 1.8 + Math.random() * 0.5

    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
    positions[i * 3 + 2] = radius * Math.cos(phi)
  }

  particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3))

  const particleMaterial = new THREE.PointsMaterial({
    color: color,
    size: 0.05,
    transparent: true,
    opacity: intensity,
    blending: THREE.AdditiveBlending,
  })

  const particles = new THREE.Points(particleGeometry, particleMaterial)
  earthSpaceScene.add(particles)
  stormParticles.push(particles)

  // Animate particles
  animateStormParticles(particles, intensity)
}

function animateStormParticles(particles, baseIntensity) {
  let frame = 0
  const maxFrames = 200

  function animate() {
    if (frame < maxFrames && earthSpaceScene.children.includes(particles)) {
      frame++
      particles.rotation.y += 0.005

      // Pulse effect
      const pulse = Math.sin(frame * 0.1) * 0.3
      particles.material.opacity = baseIntensity + pulse * 0.2

      requestAnimationFrame(animate)
    }
  }

  animate()
}

function addAuroraEffect(intensity) {
  console.log("[v0] Adding aurora effect with intensity:", intensity)

  // Create multiple aurora rings for more dramatic effect
  const numRings = intensity > 0.6 ? 3 : intensity > 0.3 ? 2 : 1

  for (let ring = 0; ring < numRings; ring++) {
    const ringRadius = 0.5 + ring * 0.15
    const ringThickness = 0.08 + ring * 0.02

    const auroraGeometry = new THREE.TorusGeometry(ringRadius, ringThickness, 16, 100)

    // Color based on intensity
    let auroraColor
    if (intensity > 0.6) {
      auroraColor = 0xff4081 // Pink for intense
    } else if (intensity > 0.3) {
      auroraColor = 0x64ffda // Cyan for moderate
    } else {
      auroraColor = 0x7b68ee // Purple for weak
    }

    const auroraMaterial = new THREE.MeshBasicMaterial({
      color: auroraColor,
      transparent: true,
      opacity: intensity * (1 - ring * 0.2),
      side: THREE.DoubleSide,
    })

    // North pole aurora
    const northAurora = new THREE.Mesh(auroraGeometry, auroraMaterial)
    northAurora.rotation.x = Math.PI / 2
    northAurora.position.y = 0.9 + ring * 0.1
    earthSpaceScene.add(northAurora)

    // South pole aurora
    const southAurora = new THREE.Mesh(auroraGeometry, auroraMaterial.clone())
    southAurora.rotation.x = Math.PI / 2
    southAurora.position.y = -(0.9 + ring * 0.1)
    earthSpaceScene.add(southAurora)

    // Animate auroras
    animateAurora(northAurora, southAurora, intensity, ring * 500)
  }
}

function animateAurora(northAurora, southAurora, intensity, delay) {
  setTimeout(() => {
    let frame = 0
    const duration = 5000

    function animate() {
      if (frame < duration / 16 && earthSpaceScene.children.includes(northAurora)) {
        frame++

        // Rotate
        northAurora.rotation.z += 0.01
        southAurora.rotation.z -= 0.01

        // Pulse
        const pulse = Math.sin(frame * 0.1) * 0.2
        northAurora.material.opacity = Math.max(0, intensity + pulse)
        southAurora.material.opacity = Math.max(0, intensity + pulse)

        requestAnimationFrame(animate)
      } else {
        earthSpaceScene.remove(northAurora)
        earthSpaceScene.remove(southAurora)
      }
    }

    animate()
  }, delay)
}

function animateEarthSpace() {
  earthSpaceAnimationId = requestAnimationFrame(animateEarthSpace)

  if (earthSpace) {
    earthSpace.rotation.y += 0.001
  }

  if (magnetosphere && magnetosphere.material.opacity > 0) {
    magnetosphere.rotation.y += 0.002

    const pulseSpeed = currentEarthState === "severe" ? 0.004 : currentEarthState === "moderate" ? 0.003 : 0.002
    const pulse = Math.sin(Date.now() * pulseSpeed) * 0.05

    // Keep opacity within bounds based on storm level
    const baseOpacity =
      currentEarthState === "severe"
        ? 0.5
        : currentEarthState === "moderate"
          ? 0.35
          : currentEarthState === "minor"
            ? 0.25
            : 0

    magnetosphere.material.opacity = Math.max(0, baseOpacity + pulse)
  }

  stormParticles.forEach((particles) => {
    if (particles.rotation) {
      particles.rotation.y += 0.003
    }
  })

  if (earthSpaceRenderer && earthSpaceScene && earthSpaceCamera) {
    earthSpaceRenderer.render(earthSpaceScene, earthSpaceCamera)
  }
}

function stopEarthSpaceAnimation() {
  if (earthSpaceAnimationId) {
    cancelAnimationFrame(earthSpaceAnimationId)
    earthSpaceAnimationId = null
  }
}

// Export functions
window.initEarthSpace3D = initEarthSpace3D
window.updateEarthSpaceVisualization = updateEarthSpaceVisualization
window.addAuroraEffect = addAuroraEffect
