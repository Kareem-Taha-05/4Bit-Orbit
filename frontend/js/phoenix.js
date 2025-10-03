// Aether Phoenix Chat Interface - Connected to Gemini API and ElevenLabs TTS

const API_BASE_URL = "http://localhost:3000"

const STORIES = {
  carrington: {
    title: "The Carrington Event (1859)",
    text: "Long ago, in the year 1859, I witnessed the most powerful solar storm ever recorded by humans. The sun unleashed a tremendous burst of energy that painted the skies with brilliant auroras visible even near the equator! Telegraph systems sparked and caught fire, and operators received electric shocks. This event, named after astronomer Richard Carrington, showed humanity the awesome power of our star. Even today, scientists study this event to prepare for future solar storms that could affect our modern technology.",
    audio: "assets/stories/carrington.mp3",
  },
  auroras: {
    title: "Auroras in the Night Sky",
    text: "Have you ever seen the magical dancing lights in the night sky? These beautiful curtains of green, pink, and purple are called auroras - or the Northern and Southern Lights. They happen when tiny particles from the sun collide with gases in Earth's atmosphere. I love flying through these shimmering veils of light! The colors tell a story: green comes from oxygen, red from high-altitude oxygen, and blue or purple from nitrogen. Indigenous peoples have many legends about these lights, and now you know the science behind the magic!",
    audio: "assets/stories/auroras.mp3",
  },
  satellites: {
    title: "When Satellites Shook",
    text: "Did you know that space weather can make your GPS lose its way? During strong solar storms, the ionosphere - a layer of Earth's atmosphere - becomes disturbed. GPS signals travel through this layer, and when it's disturbed, the signals can be delayed or scattered. Farmers using precision agriculture, airplanes navigating, and even your phone's map app can all be affected! In 2003, a Halloween solar storm caused GPS errors of up to 30 meters. That's why scientists monitor space weather - to keep our navigation systems working properly!",
    audio: "assets/stories/satellites.mp3",
  },
  phoenix: {
    title: "The Phoenix Flies Through Solar Storms",
    text: "Let me tell you about one of my greatest adventures! I was soaring through space when suddenly, a massive solar flare erupted from the sun. Waves of charged particles rushed toward me like a cosmic tsunami! My feathers glowed with brilliant colors as I flew through the storm. I watched as the particles raced toward Earth, where they would create spectacular auroras. Flying through solar storms has taught me to respect the sun's power and beauty. Every storm is different, and each one is a reminder of how dynamic and alive our solar system truly is!",
    audio: "assets/stories/phoenix.mp3",
  },
  gps: {
    title: "The Tale of Lost GPS Signals",
    text: "Did you know that space weather can make your GPS lose its way? During strong solar storms, the ionosphere - a layer of Earth's atmosphere - becomes disturbed. GPS signals travel through this layer, and when it's disturbed, the signals can be delayed or scattered. Farmers using precision agriculture, airplanes navigating, and even your phone's map app can all be affected! In 2003, a Halloween solar storm caused GPS errors of up to 30 meters. That's why scientists monitor space weather - to keep our navigation systems working properly!",
    audio: "assets/stories/gps.mp3",
  },
}

document.addEventListener("DOMContentLoaded", () => {
  const phoenixForm = document.getElementById("phoenixForm")
  const userInput = document.getElementById("userInput")
  const chatWindow = document.getElementById("chatWindow")
  const phoenixClosed = document.getElementById("phoenixClosed")
  const phoenixOpen = document.getElementById("phoenixOpen")

  checkServerHealth()

  // Add welcome message
  addMessage(
    "aether",
    "Greetings! I am Aether the Phoenix. Ask me anything about space weather, or click on a story card below to hear one of my tales!",
  )

  async function checkServerHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`)
      if (response.ok) {
        console.log("[v0] Backend server is running")
      } else {
        console.error("[v0] Backend server returned error:", response.status)
        addMessage("aether", "⚠️ Warning: Backend server is not responding properly. Please check if it's running.")
      }
    } catch (error) {
      console.error("[v0] Cannot connect to backend server:", error)
      addMessage(
        "aether",
        "⚠️ Warning: Cannot connect to backend server. Please make sure the server is running at http://localhost:3000",
      )
    }
  }

  phoenixForm.addEventListener("submit", async (e) => {
    e.preventDefault()

    const userMessage = userInput.value.trim()
    if (!userMessage) return

    console.log("[v0] User message:", userMessage)

    // Add user message to chat
    addMessage("user", userMessage)
    userInput.value = ""

    // Show thinking message
    const thinkingMsg = addMessage("aether", "Thinking...")

    try {
      console.log("[v0] Calling Gemini API...")
      const geminiResponse = await fetch(`${API_BASE_URL}/api/gemini`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: userMessage }),
      })

      console.log("[v0] Gemini response status:", geminiResponse.status)

      if (!geminiResponse.ok) {
        const errorData = await geminiResponse.json()
        console.error("[v0] Gemini API error:", errorData)
        throw new Error(errorData.error || "Failed to get response from Aether")
      }

      const { text } = await geminiResponse.json()
      console.log("[v0] Received response:", text.substring(0, 50) + "...")

      // Replace thinking message with actual response
      thinkingMsg.textContent = text

      await playAetherVoice(text)
    } catch (error) {
      console.error("[v0] Error:", error)
      thinkingMsg.textContent = `I apologize, but I'm having trouble connecting right now. Error: ${error.message}. Please check the console for details.`
    }
  })

  function addMessage(sender, text) {
    const messageDiv = document.createElement("div")
    messageDiv.className = `message ${sender}`
    messageDiv.textContent = text
    chatWindow.appendChild(messageDiv)
    chatWindow.scrollTop = chatWindow.scrollHeight
    return messageDiv
  }

  async function playAetherVoice(text) {
    try {
      console.log("[v0] Calling TTS API...")
      const ttsResponse = await fetch(`${API_BASE_URL}/api/tts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      })

      console.log("[v0] TTS response status:", ttsResponse.status)

      if (!ttsResponse.ok) {
        console.error("[v0] TTS failed, skipping audio")
        return
      }

      const audioBlob = await ttsResponse.blob()
      console.log("[v0] Audio blob size:", audioBlob.size)
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)

      // Start animation when audio starts
      audio.addEventListener("play", () => {
        console.log("[v0] Audio playing, starting animation")
        startPhoenixAnimation()
      })

      // Stop animation when audio ends
      audio.addEventListener("ended", () => {
        console.log("[v0] Audio ended, stopping animation")
        stopPhoenixAnimation()
        URL.revokeObjectURL(audioUrl)
      })

      await audio.play()
    } catch (error) {
      console.error("[v0] Error playing audio:", error)
    }
  }

  let animationInterval = null

  function startPhoenixAnimation() {
    let isOpen = false
    animationInterval = setInterval(() => {
      if (isOpen) {
        phoenixClosed.style.display = "block"
        phoenixOpen.style.display = "none"
      } else {
        phoenixClosed.style.display = "none"
        phoenixOpen.style.display = "block"
      }
      isOpen = !isOpen
    }, 300) // Toggle every 300ms for talking effect
  }

  function stopPhoenixAnimation() {
    if (animationInterval) {
      clearInterval(animationInterval)
      animationInterval = null
    }
    // Return to closed state
    phoenixClosed.style.display = "block"
    phoenixOpen.style.display = "none"
  }

  window.playStory = (storyId, storyTitle, audioFile) => {
    console.log("[v0] Playing story:", storyId)

    const story = STORIES[storyId]
    if (!story) {
      console.error("[v0] Story not found:", storyId)
      return
    }

    // Add user message showing which story was clicked
    addMessage("user", `Clicked story: ${story.title}`)

    // Add Aether's story text
    addMessage("aether", story.text)

    // Play the pre-recorded audio file
    playStoryAudio(story.audio)
  }

  function playStoryAudio(audioPath) {
    try {
      console.log("[v0] Playing story audio:", audioPath)
      const audio = new Audio(audioPath)

      // Start animation when audio starts
      audio.addEventListener("play", () => {
        console.log("[v0] Story audio playing, starting animation")
        startPhoenixAnimation()
      })

      // Stop animation when audio ends
      audio.addEventListener("ended", () => {
        console.log("[v0] Story audio ended, stopping animation")
        stopPhoenixAnimation()
      })

      // Handle audio errors (file not found, etc.)
      audio.addEventListener("error", (e) => {
        console.error("[v0] Error playing story audio:", e)
        addMessage(
          "aether",
          "⚠️ The audio file for this story hasn't been recorded yet, but you can still read the text above!",
        )
        stopPhoenixAnimation()
      })

      audio.play()
    } catch (error) {
      console.error("[v0] Error playing story audio:", error)
      addMessage(
        "aether",
        "⚠️ The audio file for this story hasn't been recorded yet, but you can still read the text above!",
      )
    }
  }
})
