/**
 * Space Weather Dashboard - Live Kp Index Monitor
 * Fetches real-time Kp index from NOAA SWPC and displays risk level
 */

class SpaceWeatherDashboard {
  constructor() {
    this.apiUrl = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    this.refreshInterval = 60000 // 60 seconds
    this.kpValue = null
    this.lastUpdate = null
    this.intervalId = null

    this.init()
  }

  init() {
    console.log("[v0] Space Weather Dashboard initializing...")
    this.fetchKpData()
    this.startAutoRefresh()
  }

  async fetchKpData() {
    try {
      const response = await fetch(this.apiUrl)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Data format: [["time_tag", "kp", "a_running", "station_count"], ...]
      // Skip header row and get the most recent entry
      if (data.length > 1) {
        const latestEntry = data[data.length - 1]
        const timeTag = latestEntry[0]
        const kpValue = Number.parseFloat(latestEntry[1])

        this.kpValue = kpValue
        this.lastUpdate = new Date(timeTag)

        this.updateUI()
        this.dispatchKpEvent()

        console.log("[v0] Kp data fetched:", { kp: kpValue, time: timeTag })
      }
    } catch (error) {
      console.error("[v0] Error fetching Kp data:", error)
      this.showError()
    }
  }

  updateUI() {
    const kpElement = document.getElementById("kpValue")
    const levelElement = document.getElementById("kpLevel")
    const indicatorElement = document.getElementById("kpIndicator")
    const timestampElement = document.getElementById("kpTimestamp")

    if (!kpElement || !levelElement || !indicatorElement || !timestampElement) {
      console.error("[v0] Dashboard elements not found")
      return
    }

    // Update Kp value
    kpElement.textContent = this.kpValue.toFixed(1)

    // Determine risk level and color
    const riskData = this.getRiskLevel(this.kpValue)
    levelElement.textContent = riskData.level
    levelElement.className = `kp-level ${riskData.class}`

    // Update indicator
    indicatorElement.className = `kp-indicator ${riskData.class}`

    // Update timestamp
    const timeString = this.lastUpdate.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
    timestampElement.textContent = `Last updated: ${timeString}`
  }

  getRiskLevel(kp) {
    if (kp <= 3) {
      return { level: "LOW", class: "low" }
    } else if (kp === 4) {
      return { level: "MODERATE", class: "moderate" }
    } else {
      return { level: "HIGH", class: "high" }
    }
  }

  showError() {
    const kpElement = document.getElementById("kpValue")
    const levelElement = document.getElementById("kpLevel")
    const indicatorElement = document.getElementById("kpIndicator")
    const timestampElement = document.getElementById("kpTimestamp")

    if (kpElement) kpElement.textContent = "--"
    if (levelElement) {
      levelElement.textContent = "UNAVAILABLE"
      levelElement.className = "kp-level error"
    }
    if (indicatorElement) {
      indicatorElement.className = "kp-indicator error"
    }
    if (timestampElement) {
      timestampElement.textContent = "Data unavailable"
    }
  }

  dispatchKpEvent() {
    const riskData = this.getRiskLevel(this.kpValue)
    const event = new CustomEvent("kpUpdated", {
      detail: {
        kp: this.kpValue,
        level: riskData.level,
        time: this.lastUpdate.toISOString(),
      },
    })
    window.dispatchEvent(event)
    console.log("[v0] kpUpdated event dispatched:", event.detail)
  }

  startAutoRefresh() {
    this.intervalId = setInterval(() => {
      console.log("[v0] Auto-refreshing Kp data...")
      this.fetchKpData()
    }, this.refreshInterval)
  }

  stopAutoRefresh() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }
}

// Initialize dashboard when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.spaceWeatherDashboard = new SpaceWeatherDashboard()
  })
} else {
  window.spaceWeatherDashboard = new SpaceWeatherDashboard()
}

// Optional: Listen to kpUpdated events (example for Games tab integration)
window.addEventListener("kpUpdated", (event) => {
  console.log("[v0] Kp update received:", event.detail)
  // Games or other tabs can hook into this event
})
