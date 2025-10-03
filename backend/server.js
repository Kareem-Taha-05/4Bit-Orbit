const express = require("express")
const cors = require("cors")
const { spawn } = require("child_process")
const path = require("path")
require("dotenv").config()

const app = express()
const PORT = process.env.PORT || 3000



// Middleware
app.use(cors())
app.use(express.json())

// Route to handle .exe downloads explicitly
app.get("/game/:file", (req, res) => {
  const file = req.params.file
  const filePath = path.join(__dirname, "..", "game", file)

  res.download(filePath, file, (err) => {
    if (err) {
      console.error("[v0] Error sending game file:", err)
      res.status(404).send("File not found")
    }
  })
})

// Serve frontend normally
app.use(express.static(path.join(__dirname, "..", "frontend")))


app.use((req, res, next) => {
  console.log(`[v0] ${req.method} ${req.url}`)
  console.log(`[v0] Headers:`, req.headers)
  next()
})

app.get("/api/health", (req, res) => {
  res.json({ status: "ok", message: "Server is running" })
})

app.post("/api/predict/aurora", async (req, res) => {
  try {
    const { latitude, longitude } = req.body

    console.log("[v0] Aurora prediction request:", { latitude, longitude })

    if (latitude === undefined || longitude === undefined) {
      return res.status(400).json({ error: "Latitude and longitude are required" })
    }

    // Validate coordinates
    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      return res.status(400).json({ error: "Invalid coordinates" })
    }

    // Call Python script
    const pythonScript = path.join(__dirname, "..", "scripts", "aurora_prediction.py")
    const pythonProcess = spawn("python3", [pythonScript, latitude.toString(), longitude.toString()])

    let dataString = ""
    let errorString = ""

    pythonProcess.stdout.on("data", (data) => {
      dataString += data.toString()
    })

    pythonProcess.stderr.on("data", (data) => {
      errorString += data.toString()
      console.error("[v0] Python error:", data.toString())
    })

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        console.error("[v0] Python script failed:", errorString)
        return res.status(500).json({ error: "Prediction failed", details: errorString })
      }

      try {
        const result = JSON.parse(dataString)
        console.log("[v0] Aurora prediction result:", result)
        res.json(result)
      } catch (parseError) {
        console.error("[v0] Failed to parse Python output:", dataString)
        res.status(500).json({ error: "Failed to parse prediction result" })
      }
    })
  } catch (error) {
    console.error("[v0] Error in aurora prediction:", error)
    res.status(500).json({ error: "Internal server error", details: error.message })
  }
})

// Gemini API endpoint
app.post("/api/gemini", async (req, res) => {
  console.log("[v0] ===== CODE VERSION: 2025-10-01-FIXED =====")

  try {
    const { prompt } = req.body

    console.log("[v0] Received prompt:", prompt)

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" })
    }

    if (!process.env.GEMINI_API_KEY) {
      console.error("[v0] GEMINI_API_KEY not configured")
      return res.status(500).json({ error: "Gemini API key not configured" })
    }

    console.log("[v0] API Key length:", process.env.GEMINI_API_KEY.length)
    console.log("[v0] API Key starts with:", process.env.GEMINI_API_KEY.substring(0, 10) + "...")

    const systemPrompt =
      "You are Aether the Phoenix, a thousand-year-old mystical bird who has flown through solar storms and auroras. Speak in a warm, wise, storybook tone appropriate for children. Keep replies short (1–3 paragraphs). You also have a story library with tales such as 'The Carrington Event (1859)', 'Auroras in the Night Sky', 'When Satellites Shook', 'The Phoenix Flies Through Solar Storms', and 'The Tale of Lost GPS Signals'. If a child asks for one of these stories or wants to hear a tale, encourage them to click on the story cards below the chat window to hear them in your voice."

    const fullPrompt = systemPrompt + "\n\nUser: " + prompt

    console.log("[v0] Calling Gemini API...")

    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`
    console.log("[v0] API URL (without key):", apiUrl.split("?key=")[0])

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            role: "user",
            parts: [{ text: fullPrompt }],
          },
        ],
      }),
    })

    console.log("[v0] Gemini API response status:", response.status)
    console.log("[v0] Gemini API response headers:", Object.fromEntries(response.headers.entries()))

    const data = await response.json()
    console.log("[v0] Gemini API response data:", JSON.stringify(data, null, 2))

    if (!response.ok) {
      console.error("[v0] Gemini API error:", data)
      return res.status(response.status).json({ error: "Failed to generate response", details: data })
    }

    if (
      !data.candidates ||
      !data.candidates[0] ||
      !data.candidates[0].content ||
      !data.candidates[0].content.parts ||
      !data.candidates[0].content.parts[0]
    ) {
      console.error("[v0] Unexpected Gemini API response structure:", data)
      return res.status(500).json({ error: "Unexpected response structure from Gemini", details: data })
    }

    const generatedText = data.candidates[0].content.parts[0].text
    console.log("[v0] Generated response:", generatedText.substring(0, 50) + "...")
    res.json({ text: generatedText })
  } catch (error) {
    console.error("[v0] Error calling Gemini API:", error)
    console.error("[v0] Error stack:", error.stack)
    res.status(500).json({ error: "Internal server error", details: error.message, stack: error.stack })
  }
})

// ElevenLabs TTS endpoint
app.post("/api/tts", async (req, res) => {
  try {
    const { text } = req.body

    console.log("[v0] Received TTS request for text length:", text?.length)

    if (!text) {
      return res.status(400).json({ error: "Text is required" })
    }

    if (!process.env.ELEVEN_API_KEY || !process.env.ELEVEN_VOICE_ID) {
      console.error("[v0] ElevenLabs API key or Voice ID not configured")
      return res.status(500).json({ error: "ElevenLabs API not configured" })
    }

    console.log("[v0] Calling ElevenLabs API...")

    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${process.env.ELEVEN_VOICE_ID}`, {
      method: "POST",
      headers: {
        "xi-api-key": process.env.ELEVEN_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        voice_settings: {
          stability: 0.6,
          similarity_boost: 0.7,
        },
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("[v0] ElevenLabs API error:", response.status, errorText)
      return res.status(response.status).json({ error: "Failed to generate audio", details: errorText })
    }

    console.log("[v0] TTS audio generated successfully")

    // Stream the audio back to the client
    res.setHeader("Content-Type", "audio/mpeg")
    const audioBuffer = await response.arrayBuffer()
    res.send(Buffer.from(audioBuffer))
  } catch (error) {
    console.error("[v0] Error calling ElevenLabs API:", error)
    res.status(500).json({ error: "Internal server error", details: error.message })
  }
})

app.listen(PORT, () => {
  console.log(`[v0] Server running on http://localhost:${PORT}`)
  console.log(`[v0] GEMINI_API_KEY configured: ${!!process.env.GEMINI_API_KEY}`)
  console.log(`[v0] ELEVEN_API_KEY configured: ${!!process.env.ELEVEN_API_KEY}`)
  console.log(`[v0] ELEVEN_VOICE_ID configured: ${!!process.env.ELEVEN_VOICE_ID}`)
  console.log(`[v0] Registered routes:`)
  app._router.stack.forEach((r) => {
    if (r.route && r.route.path) {
      console.log(`[v0]   ${Object.keys(r.route.methods).join(", ").toUpperCase()} ${r.route.path}`)
    }
  })
})
