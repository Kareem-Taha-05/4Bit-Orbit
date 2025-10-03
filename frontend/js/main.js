// Create animated stars
function createStars() {
  const container = document.getElementById("starsContainer")
  const numStars = 100

  for (let i = 0; i < numStars; i++) {
    const star = document.createElement("div")
    star.className = "star"

    const size = Math.random() * 3 + 1
    const x = Math.random() * 100
    const y = Math.random() * 100
    const delay = Math.random() * 3

    star.style.width = size + "px"
    star.style.height = size + "px"
    star.style.left = x + "%"
    star.style.top = y + "%"
    star.style.animationDelay = delay + "s"

    container.appendChild(star)
  }
}

// Navigation functionality
function showPage(pageId) {
  console.log("[v0] Navigating to page:", pageId)
  const pages = document.querySelectorAll(".page")
  pages.forEach((page) => page.classList.remove("active"))
  document.getElementById(pageId).classList.add("active")

  document.getElementById("navLinks").classList.remove("active")

  if (pageId === "prediction") {
    console.log("[v0] Prediction page activated, initializing Earth 3D...")
    setTimeout(() => {
      const earthContainer = document.getElementById("earth3D")

      if (earthContainer && !earthContainer.querySelector("canvas")) {
        console.log("[v0] Initializing Earth 3D from showPage...")
        if (typeof window.initEarth3D === "function") {
          window.initEarth3D()
        }
      }
    }, 200)
  }
}

// Smooth scroll to project summary
function scrollToSummary() {
  document.getElementById("project-summary").scrollIntoView({
    behavior: "smooth",
  })
}

// Game functionality
function startGame() {
  alert("Game integration ready! Connect your browser-based mini-game here.")
}

// Prediction tool slider
function updateSlider(event) {
  const slider = event.currentTarget
  const rect = slider.getBoundingClientRect()
  const x = event.clientX - rect.left
  const percentage = (x / rect.width) * 100

  const track = document.getElementById("sliderTrack")
  const currentLevel = document.getElementById("currentLevel")

  track.style.width = percentage + "%"

  // Update risk levels based on slider position
  if (percentage < 33) {
    currentLevel.textContent = "Calm Conditions"
    updateRiskLevels("low")
  } else if (percentage < 66) {
    currentLevel.textContent = "Moderate Activity"
    updateRiskLevels("moderate")
  } else {
    currentLevel.textContent = "Severe Storm"
    updateRiskLevels("high")
  }
}

function updateRiskLevels(level) {
  const gpsRisk = document.getElementById("gpsRisk")
  const powerRisk = document.getElementById("powerRisk")
  const commRisk = document.getElementById("commRisk")

  if (level === "low") {
    gpsRisk.textContent = "Low Risk"
    powerRisk.textContent = "Low Risk"
    commRisk.textContent = "Minimal Risk"
  } else if (level === "moderate") {
    gpsRisk.textContent = "Moderate Risk"
    powerRisk.textContent = "Moderate Risk"
    commRisk.textContent = "Low Risk"
  } else {
    gpsRisk.textContent = "High Risk"
    powerRisk.textContent = "Critical Risk"
    commRisk.textContent = "High Risk"
  }
}

// ML prediction functionality
function runPrediction() {
  // Get input values
  const solarWind = Number.parseFloat(document.getElementById("solarWind").value)
  const magneticField = Number.parseFloat(document.getElementById("magneticField").value)
  const sunspotNumber = Number.parseFloat(document.getElementById("sunspotNumber").value)
  const xrayFlux = Number.parseInt(document.getElementById("xrayFlux").value)
  const protonFlux = Number.parseFloat(document.getElementById("protonFlux").value)
  const kpIndex = Number.parseFloat(document.getElementById("kpIndex").value)

  // Show results section with animation
  const resultsSection = document.getElementById("predictionResults")
  resultsSection.style.display = "block"
  resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" })

  // Calculate storm probability using weighted formula
  let probability = 0

  // Solar wind contribution (0-30%)
  probability += Math.min(((solarWind - 300) / 700) * 30, 30)

  // Magnetic field contribution (0-25%)
  probability += Math.min((magneticField / 50) * 25, 25)

  // Sunspot contribution (0-15%)
  probability += Math.min((sunspotNumber / 300) * 15, 15)

  // X-ray flux contribution (0-20%)
  probability += ((xrayFlux - 1) / 4) * 20

  // Proton flux contribution (0-10%)
  probability += Math.min((protonFlux / 10000) * 10, 10)

  // Kp index contribution (0-10%)
  probability += (kpIndex / 9) * 10

  probability = Math.max(0, Math.min(100, probability))

  // Animate probability circle
  animateProbability(probability)

  // Determine storm category
  let category, categoryColor
  if (probability < 20) {
    category = "Quiet Conditions"
    categoryColor = "var(--aurora-green)"
  } else if (probability < 40) {
    category = "Minor Storm (G1)"
    categoryColor = "#90EE90"
  } else if (probability < 60) {
    category = "Moderate Storm (G2)"
    categoryColor = "#FFD700"
  } else if (probability < 80) {
    category = "Strong Storm (G3)"
    categoryColor = "#FFA500"
  } else {
    category = "Severe Storm (G4-G5)"
    categoryColor = "var(--aurora-pink)"
  }

  const categoryElement = document.getElementById("stormCategory")
  categoryElement.textContent = category
  categoryElement.style.color = categoryColor

  // Update timeline
  updateTimeline(probability, solarWind)

  // Update risk assessments
  updateRiskAssessments(probability, xrayFlux, kpIndex)

  // Generate recommendations
  generateRecommendations(probability, category)
}

function animateProbability(targetProbability) {
  const circle = document.getElementById("probabilityCircle")
  const valueDisplay = document.getElementById("probabilityValue")
  const circumference = 283

  let currentValue = 0
  const duration = 2000
  const startTime = Date.now()

  function animate() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    currentValue = targetProbability * progress
    const offset = circumference - (currentValue / 100) * circumference

    circle.style.strokeDashoffset = offset
    valueDisplay.textContent = Math.round(currentValue) + "%"

    // Change color based on probability
    if (currentValue < 40) {
      circle.style.stroke = "var(--aurora-green)"
    } else if (currentValue < 70) {
      circle.style.stroke = "#FFD700"
    } else {
      circle.style.stroke = "var(--aurora-pink)"
    }

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  animate()
}

function updateTimeline(probability, solarWind) {
  // Calculate impact progression based on solar wind speed
  const travelTime = 150000000 / solarWind // Approximate time for solar wind to reach Earth

  const impacts = [
    { id: "impactNow", value: probability * 0.3 },
    { id: "impact6h", value: probability * 0.5 },
    { id: "impact12h", value: probability * 0.8 },
    { id: "impact24h", value: probability },
    { id: "impact48h", value: probability * 0.6 },
  ]

  impacts.forEach((impact, index) => {
    setTimeout(() => {
      const bar = document.getElementById(impact.id)
      bar.style.width = impact.value + "%"

      if (impact.value < 30) {
        bar.style.background = "var(--aurora-green)"
      } else if (impact.value < 60) {
        bar.style.background = "linear-gradient(90deg, var(--aurora-green), #FFD700)"
      } else {
        bar.style.background = "linear-gradient(90deg, #FFD700, var(--aurora-pink))"
      }
    }, index * 200)
  })
}

function updateRiskAssessments(probability, xrayFlux, kpIndex) {
  // GPS risk (affected by ionospheric disturbances)
  const gpsRisk = Math.min(100, probability * 0.8 + xrayFlux * 5)
  updateRiskBar("gpsRiskBar", "gpsRisk", gpsRisk)

  // Power grid risk (affected by geomagnetic activity)
  const powerRisk = Math.min(100, probability * 0.9 + kpIndex * 8)
  updateRiskBar("powerRiskBar", "powerRisk", powerRisk)

  // Communications risk (affected by solar radiation)
  const commRisk = Math.min(100, probability * 0.7 + xrayFlux * 7)
  updateRiskBar("commRiskBar", "commRisk", commRisk)

  // Aviation risk (radiation exposure)
  const aviationRisk = Math.min(100, probability * 0.6 + xrayFlux * 6)
  updateRiskBar("aviationRiskBar", "aviationRisk", aviationRisk)
}

function updateRiskBar(barId, labelId, riskValue) {
  const bar = document.getElementById(barId)
  const label = document.getElementById(labelId)

  setTimeout(() => {
    bar.style.width = riskValue + "%"

    let riskText, riskColor
    if (riskValue < 25) {
      riskText = "Low Risk - Normal Operations"
      riskColor = "var(--aurora-green)"
      bar.style.background = "var(--aurora-green)"
    } else if (riskValue < 50) {
      riskText = "Moderate Risk - Monitor Closely"
      riskColor = "#FFD700"
      bar.style.background = "linear-gradient(90deg, var(--aurora-green), #FFD700)"
    } else if (riskValue < 75) {
      riskText = "High Risk - Take Precautions"
      riskColor = "#FFA500"
      bar.style.background = "linear-gradient(90deg, #FFD700, #FFA500)"
    } else {
      riskText = "Critical Risk - Immediate Action Required"
      riskColor = "var(--aurora-pink)"
      bar.style.background = "linear-gradient(90deg, #FFA500, var(--aurora-pink))"
    }

    label.textContent = riskText
    label.style.color = riskColor
  }, 300)
}

function generateRecommendations(probability, category) {
  const recommendationsDiv = document.getElementById("recommendations")
  let recommendations = []

  if (probability < 20) {
    recommendations = [
      { icon: "check-circle", text: "All systems operating normally", color: "var(--aurora-green)" },
      { icon: "eye", text: "Continue routine space weather monitoring", color: "var(--aurora-green)" },
      {
        icon: "satellite",
        text: "No special precautions needed for satellite operations",
        color: "var(--aurora-green)",
      },
    ]
  } else if (probability < 40) {
    recommendations = [
      { icon: "exclamation-triangle", text: "Minor GPS accuracy degradation possible", color: "#FFD700" },
      { icon: "broadcast-tower", text: "HF radio communications may be affected at high latitudes", color: "#FFD700" },
      { icon: "eye", text: "Increased monitoring recommended", color: "#FFD700" },
      { icon: "star", text: "Aurora may be visible at high latitudes", color: "var(--aurora-green)" },
    ]
  } else if (probability < 60) {
    recommendations = [
      { icon: "satellite", text: "Satellite operators should review contingency plans", color: "#FFA500" },
      { icon: "bolt", text: "Power grid operators: monitor voltage irregularities", color: "#FFA500" },
      { icon: "plane", text: "Consider rerouting polar flights to lower latitudes", color: "#FFA500" },
      { icon: "broadcast-tower", text: "HF radio propagation disruptions likely", color: "#FFA500" },
      { icon: "star", text: "Aurora may be visible at mid-latitudes", color: "var(--aurora-green)" },
    ]
  } else if (probability < 80) {
    recommendations = [
      {
        icon: "exclamation-circle",
        text: "CRITICAL: Satellite orientation anomalies possible",
        color: "var(--aurora-pink)",
      },
      { icon: "bolt", text: "URGENT: Power grid operators activate storm protocols", color: "var(--aurora-pink)" },
      { icon: "plane", text: "Aviation: Avoid polar routes, monitor radiation levels", color: "var(--aurora-pink)" },
      { icon: "broadcast-tower", text: "Expect widespread HF radio blackouts", color: "var(--aurora-pink)" },
      { icon: "map-marked-alt", text: "GPS accuracy significantly degraded", color: "var(--aurora-pink)" },
      { icon: "star", text: "Aurora may be visible at lower latitudes", color: "var(--aurora-green)" },
    ]
  } else {
    recommendations = [
      { icon: "radiation", text: "SEVERE: Satellite damage and failures likely", color: "#FF0000" },
      { icon: "bolt", text: "EMERGENCY: Power grid blackouts possible", color: "#FF0000" },
      { icon: "plane", text: "CRITICAL: Ground all polar flights immediately", color: "#FF0000" },
      { icon: "broadcast-tower", text: "Complete HF radio blackout expected", color: "#FF0000" },
      { icon: "satellite", text: "GPS systems may be completely unavailable", color: "#FF0000" },
      { icon: "shield-alt", text: "Activate all emergency space weather protocols", color: "#FF0000" },
      { icon: "star", text: "Aurora may be visible at very low latitudes", color: "var(--aurora-green)" },
    ]
  }

  recommendationsDiv.innerHTML = recommendations
    .map(
      (rec) => `
    <div class="recommendation-item" style="border-left-color: ${rec.color};">
      <i class="fas fa-${rec.icon}" style="color: ${rec.color};"></i>
      <span>${rec.text}</span>
    </div>
  `,
    )
    .join("")
}

// Navbar scroll effect
window.addEventListener("scroll", () => {
  const navbar = document.querySelector(".navbar")
  if (window.scrollY > 50) {
    navbar.style.background = "rgba(10, 10, 35, 0.95)"
  } else {
    navbar.style.background = "rgba(10, 10, 35, 0.9)"
  }
})

// Initialize page
document.addEventListener("DOMContentLoaded", () => {
  createStars()

  // Add click handlers for nav links
  document.querySelectorAll(".nav-links a").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault()
    })
  })

  // Add floating animation to cards
  const cards = document.querySelectorAll(".card")
  cards.forEach((card, index) => {
    card.style.animationDelay = index * 0.1 + "s"
  })

  // Simulate real-time data updates (placeholder)
  setInterval(() => {
    // This would connect to NOAA API for real data
    console.log("Real-time data update placeholder")
  }, 30000)

  const kpSlider = document.getElementById("kpIndex")
  if (kpSlider) {
    kpSlider.addEventListener("input", (e) => {
      const value = e.target.value
      const kpValue = document.getElementById("kpValue")
      const labels = [
        "Quiet",
        "Quiet",
        "Unsettled",
        "Unsettled",
        "Active",
        "Minor Storm",
        "Moderate Storm",
        "Strong Storm",
        "Severe Storm",
        "Extreme Storm",
      ]
      kpValue.textContent = `${value} (${labels[value]})`
    })
  }

  // Add event listener for aurora prediction
  const auroraButton = document.getElementById("predictAuroraButton")
  if (auroraButton) {
    auroraButton.addEventListener("click", predictAurora)
  }

  // Add event listeners for story modals
  document.querySelectorAll(".story-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault()
      const storyId = link.getAttribute("data-story")
      openStoryModal(storyId)
    })
  })

  const closeButtons = document.querySelectorAll(".story-modal-close")
  closeButtons.forEach((button) => {
    button.addEventListener("click", closeStoryModal)
  })
})

// Aurora prediction function based on ML model
async function predictAurora() {
  const location = window.getSelectedLocation()

  if (!location || location.latitude === null || location.longitude === null) {
    alert("Please select a location on the Earth first!")
    return
  }

  const lat = location.latitude
  const lon = location.longitude

  // Show results
  const resultsDiv = document.getElementById("auroraResults")
  resultsDiv.style.display = "block"
  resultsDiv.scrollIntoView({ behavior: "smooth", block: "nearest" })

  const skyImageContainer = document.getElementById("skyImageContainer")
  skyImageContainer.innerHTML = `
    <div class="loading-spinner">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Generating your aurora sky...</p>
    </div>
  `

  try {
    const backendPort = window.location.hostname === "localhost" ? "3000" : "3000"
    const response = await fetch(`http://localhost:${backendPort}/api/predict/aurora`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        latitude: lat,
        longitude: lon,
      }),
    })

    if (!response.ok) {
      throw new Error("Failed to get aurora prediction")
    }

    const data = await response.json()
    console.log("[v0] Aurora prediction received:", data)

    if (data.success && data.prediction) {
      updateAuroraStatsFromAPI(data.prediction, lat, lon)

      // Use canvas visualization
      skyImageContainer.innerHTML = `
        <canvas id="auroraCanvas" width="600" height="400"></canvas>
      `
      drawAuroraMap(lat, lon, data.prediction.intensity / 100)
    } else {
      throw new Error(data.error || "Prediction failed")
    }
  } catch (error) {
    console.error("[v0] Error predicting aurora:", error)

    // Fallback to simulation
    const auroraIntensity = simulateAuroraIntensity(lat)

    skyImageContainer.innerHTML = `
      <canvas id="auroraCanvas" width="600" height="400"></canvas>
    `
    drawAuroraMap(lat, lon, auroraIntensity)
    updateAuroraStats(auroraIntensity, lat)
  }
}

function simulateAuroraIntensity(lat) {
  const latFactor = Math.abs(lat)
  let auroraIntensity = 0

  if (latFactor > 60) {
    auroraIntensity = 0.6 + Math.random() * 0.4
  } else if (latFactor > 50) {
    auroraIntensity = 0.3 + Math.random() * 0.3
  } else if (latFactor > 40) {
    auroraIntensity = 0.1 + Math.random() * 0.2
  } else {
    auroraIntensity = Math.random() * 0.1
  }

  return auroraIntensity
}

function updateAuroraStatsFromAPI(prediction, lat, lon) {
  const intensityEl = document.getElementById("auroraIntensity")
  const colorsEl = document.getElementById("auroraColors")
  const visibilityEl = document.getElementById("auroraVisibility")
  const locationEl = document.getElementById("auroraLocation")

  const intensity = prediction.intensity / 100 // Convert to 0-1 scale

  // Intensity
  let intensityText, intensityColor
  if (intensity > 0.6) {
    intensityText = "Very Strong! 🌟"
    intensityColor = "#ff4081"
  } else if (intensity > 0.3) {
    intensityText = "Strong ⚡"
    intensityColor = "#FFD700"
  } else if (intensity > 0.1) {
    intensityText = "Moderate 💫"
    intensityColor = "#64ffda"
  } else {
    intensityText = "Weak ✨"
    intensityColor = "#7b68ee"
  }
  intensityEl.textContent = intensityText
  intensityEl.style.color = intensityColor

  // Colors from API
  colorsEl.textContent = prediction.color
  colorsEl.style.color = "#64ffda"

  // Visibility
  visibilityEl.textContent = prediction.description
  visibilityEl.style.color = "#ffffff"

  // Location
  const latDir = lat >= 0 ? "N" : "S"
  const lonDir = lon >= 0 ? "E" : "W"
  locationEl.textContent = `${Math.abs(lat).toFixed(1)}° ${latDir}, ${Math.abs(lon).toFixed(1)}° ${lonDir}`
  locationEl.style.color = "#64ffda"
}

function drawAuroraMap(lat, lon, intensity) {
  const canvas = document.getElementById("auroraCanvas")
  if (!canvas) return

  const ctx = canvas.getContext("2d")
  const width = canvas.width
  const height = canvas.height

  // Clear canvas
  ctx.fillStyle = "#0a0a23"
  ctx.fillRect(0, 0, width, height)

  // Draw Earth outline
  ctx.strokeStyle = "#64ffda"
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.arc(width / 2, height / 2, 150, 0, Math.PI * 2)
  ctx.stroke()

  // Draw latitude lines
  ctx.strokeStyle = "rgba(100, 255, 218, 0.3)"
  ctx.lineWidth = 1
  for (let i = -60; i <= 60; i += 30) {
    const y = height / 2 - (i / 90) * 150
    ctx.beginPath()
    ctx.moveTo(width / 2 - 150, y)
    ctx.lineTo(width / 2 + 150, y)
    ctx.stroke()
  }

  // Draw aurora oval (simplified)
  const auroraLat = lat > 0 ? 65 : -65 // Northern or Southern hemisphere
  const auroraY = height / 2 - (auroraLat / 90) * 150

  // Create gradient for aurora
  const gradient = ctx.createRadialGradient(width / 2, auroraY, 0, width / 2, auroraY, 100)
  gradient.addColorStop(0, `rgba(100, 255, 218, ${intensity})`)
  gradient.addColorStop(0.5, `rgba(255, 64, 129, ${intensity * 0.7})`)
  gradient.addColorStop(1, "rgba(123, 104, 238, 0)")

  ctx.fillStyle = gradient
  ctx.beginPath()
  ctx.ellipse(width / 2, auroraY, 120, 40, 0, 0, Math.PI * 2)
  ctx.fill()

  // Draw user location
  const userY = height / 2 - (lat / 90) * 150
  const userX = width / 2 + (lon / 180) * 150

  ctx.fillStyle = "#ff4081"
  ctx.beginPath()
  ctx.arc(userX, userY, 8, 0, Math.PI * 2)
  ctx.fill()

  ctx.strokeStyle = "#ffffff"
  ctx.lineWidth = 2
  ctx.stroke()

  // Add label
  ctx.fillStyle = "#ffffff"
  ctx.font = "14px Poppins"
  ctx.fillText("You are here!", userX + 15, userY + 5)

  // Add aurora animation
  animateAurora(ctx, width, height, auroraY, intensity)
}

function animateAurora(ctx, width, height, auroraY, intensity) {
  let frame = 0
  const animate = () => {
    if (frame < 60) {
      // Redraw base
      ctx.fillStyle = "#0a0a23"
      ctx.fillRect(0, 0, width, height)

      // Redraw Earth
      ctx.strokeStyle = "#64ffda"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(width / 2, height / 2, 150, 0, Math.PI * 2)
      ctx.stroke()

      // Animated aurora
      const wave = Math.sin(frame * 0.1) * 10
      const gradient = ctx.createRadialGradient(width / 2, auroraY + wave, 0, width / 2, auroraY + wave, 100)
      gradient.addColorStop(0, `rgba(100, 255, 218, ${intensity * (0.8 + Math.sin(frame * 0.15) * 0.2)})`)
      gradient.addColorStop(0.5, `rgba(255, 64, 129, ${intensity * 0.7})`)
      gradient.addColorStop(1, "rgba(123, 104, 238, 0)")

      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.ellipse(width / 2, auroraY + wave, 120, 40, 0, 0, Math.PI * 2)
      ctx.fill()

      frame++
      requestAnimationFrame(animate)
    }
  }
  animate()
}

function updateAuroraStats(intensity, lat) {
  const intensityEl = document.getElementById("auroraIntensity")
  const colorsEl = document.getElementById("auroraColors")
  const visibilityEl = document.getElementById("auroraVisibility")

  // Intensity
  let intensityText, intensityColor
  if (intensity > 0.7) {
    intensityText = "Very Strong! 🌟"
    intensityColor = "#ff4081"
  } else if (intensity > 0.4) {
    intensityText = "Strong ⚡"
    intensityColor = "#FFD700"
  } else if (intensity > 0.2) {
    intensityText = "Moderate 💫"
    intensityColor = "#64ffda"
  } else {
    intensityText = "Weak ✨"
    intensityColor = "#7b68ee"
  }
  intensityEl.textContent = intensityText
  intensityEl.style.color = intensityColor

  // Colors
  let colors
  if (intensity > 0.6) {
    colors = "Green, Pink, Purple, and Red!"
  } else if (intensity > 0.3) {
    colors = "Green and Pink"
  } else {
    colors = "Pale Green"
  }
  colorsEl.textContent = colors
  colorsEl.style.color = "#64ffda"

  // Visibility
  const absLat = Math.abs(lat)
  let visibility
  if (absLat > 60 && intensity > 0.5) {
    visibility = "Excellent! Go outside and look up! 👀"
  } else if (absLat > 50 && intensity > 0.3) {
    visibility = "Good chance tonight! 🌙"
  } else if (absLat > 40 && intensity > 0.5) {
    visibility = "Maybe visible on the horizon 🔭"
  } else {
    visibility = "Unlikely from your location 😔"
  }
  visibilityEl.textContent = visibility
  visibilityEl.style.color = "#ffffff"
}

// Add some interactive effects
document.addEventListener("mousemove", (e) => {
  const stars = document.querySelectorAll(".star")
  const mouseX = e.clientX / window.innerWidth
  const mouseY = e.clientY / window.innerHeight

  stars.forEach((star, index) => {
    if (index % 10 === 0) {
      // Only affect every 10th star for performance
      const speed = ((index % 3) + 1) * 0.5
      const x = mouseX * speed
      const y = mouseY * speed
      star.style.transform = `translate(${x}px, ${y}px)`
    }
  })
})

// Intersection Observer for fade-in animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1"
      entry.target.style.transform = "translateY(0)"
    }
  })
}, observerOptions)

// Observe all cards for animation
setTimeout(() => {
  document.querySelectorAll(".card").forEach((card) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(20px)"
    card.style.transition = "all 0.6s ease"
    observer.observe(card)
  })
}, 100)

// Story modal functions and story data
const stories = {
  story1: {
    title: "The Sun's Mighty Cry",
    audio: "assets/stories/aether_story_1.mp3",
    text: "I have watched the Sun whisper and roar across countless ages… yet on the twenty-seventh day of May, in the year you call 2025, her voice rang louder than I have heard in many lifetimes.\n\nShe drew in a breath, and with a mighty cry released an X1.1-class flare, a blaze more fierce than a billion bombs, a flash that raced ahead to strike Earth in but minutes. The sky's hidden veil, the ionosphere, quivered under her song. Pilots heard only silence where voices should be. Signals bent and faltered, leaving the tools of farmers astray, and the guardians in orbit, your satellites, shuddered as fiery currents coursed through their veins.\n\nI lingered between Sun and Earth, a witness as humanity braced against the storm. Scientists followed her heartbeat, engineers shielded their creations, and people were reminded of the star that gives them life… and tests their strength.\n\nWhen the Sun speaks, the Earth must listen. Each flare is not only fury, but a lesson, a call to prepare, to endure, and to remember.",
  },
  story2: {
    title: "When the Sun Exhales",
    audio: "assets/stories/aether_story_2.mp3",
    text: "I have seen the Sun exhale with a force that shakes worlds. On the twenty-eighth day of October, in the year 2003, she loosed one of her greatest breaths, a coronal mass ejection so fierce it crossed the vast gulf to Earth in less than a single day.\n\nThe skies ignited with auroras, glowing even above Texas and the Mediterranean. Yet beauty carried a cost: power grids in Sweden fell dark, satellites faltered in silence, and astronauts sought refuge from the storm's invisible fire.\n\nAgain, on March 13, 2023, her corona swelled and burst, hurling billions of tons of plasma into the solar sea. NASA's vigilant SOHO caught the eruption, a burning ring of flame, with Mercury a quiet witness to the Sun's wrath.\n\nTo humankind, such storms seem sudden. But I, who have watched her for ages, know them as the rhythm of her heart, reminders that when the Sun exhales, the Earth must hold its breath.",
  },
  story3: {
    title: "Arrows Swifter Than Light",
    audio: "assets/stories/aether_story_3.mp3",
    text: "I remember the day the Sun loosed her arrows swifter than light itself. On the twenty-third of January, in the year 2012, a violent eruption cast forth a storm of energetic particles, racing across the void.\n\nIn less than an hour, they pierced Earth's magnetic shield and rode the hidden lines into the polar skies. Pilots flying near the crown of the world heard their radios fade into silence. Satellites groaned as their circuits strained. Even NASA's vigilant SOHO beheld the storm, its vision clouded by a blizzard of white static, snowfall in the emptiness of space.\n\nFor the astronauts, it was a warning written not in words, but in radiation: space is alive, and the Sun's breath can nurture or endanger. These storms are her invisible arrows, swift, silent, and relentless.",
  },
  story4: {
    title: "The Trembling Shield",
    audio: "assets/stories/aether_story_4.mp3",
    text: "I have often watched Earth's hidden shield tremble when the Sun speaks too sharply. On the sixth day of September, in the year 2017, I felt such a tremor, an X9.3 flare, fiercest in more than a decade, struck the ionosphere within minutes.\n\nHigh above, the thin sea of charged particles rippled with fury. The daylight side of Earth fell silent as pilots and ships lost their voices, radios cut short mid-sentence. GPS signals bent and scattered, drifting like leaves caught in a storm.\n\nYet below, the Sun still shone, calm and golden, while in the fragile veil above, chaos reigned. The atmosphere rang like a bell, struck by fire.\n\nI hovered between star and world, watching the disruption race across continents. It was a solemn reminder: our lives rest upon a sky unseen… and with but a single breath, the Sun can twist that sky into silence.",
  },
  story5: {
    title: "Threads of Confusion",
    audio: "assets/stories/aether_story_5.mp3",
    text: "I have seen Earth's travelers place their faith in unseen threads, signals stitched through the upper sky to guide their ships, their planes, their machines. Yet on November 20, 2003, those threads twisted under the Sun's breath.\n\nThat day, the ionosphere swelled with restless charge, its fabric shifting like a tide turned by an unseen moon. The measure of its strength, the Total Electron Content, wavered wildly. GPS signals, once sharp and sure, bent and scattered as though lost in a canyon of mirrors.\n\nPilots felt their paths drift, farmers saw their machines circle like hunters chasing ghosts, and soldiers and scientists alike discovered their instruments deceived them.\n\nThe Sun had not struck with flame, nor blinded the skies with storm, but with confusion, turning the heavens into a shifting puzzle of tangled threads. And so I whisper this truth: even without fire, the Sun may unravel the quiet order of Earth's sky.",
  },
}

function openStoryModal(storyId) {
  const story = stories[storyId]
  if (!story) return

  const modal = document.getElementById("storyModal")
  const title = document.getElementById("storyTitle")
  const text = document.getElementById("storyText")
  const audioSource = document.getElementById("storyAudioSource")
  const audio = document.getElementById("storyAudio")

  title.textContent = story.title
  text.textContent = story.text
  audioSource.src = story.audio
  audio.load()

  modal.classList.add("active")
  document.body.style.overflow = "hidden"
}

function closeStoryModal(event) {
  if (event && event.target !== event.currentTarget && !event.target.classList.contains("story-modal-close")) {
    return
  }

  const modal = document.getElementById("storyModal")
  const audio = document.getElementById("storyAudio")

  audio.pause()
  audio.currentTime = 0

  modal.classList.remove("active")
  document.body.style.overflow = "auto"
}

// Close modal with Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeStoryModal()
  }
})
