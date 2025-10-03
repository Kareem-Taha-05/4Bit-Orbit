const express = require("express")
const path = require("path")

const app = express()
const PORT = process.env.FRONTEND_PORT || 8000

// Serve static files from the frontend directory
app.use(express.static(__dirname))

// Fallback to index.html for any route
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"))
})

app.listen(PORT, () => {
  console.log(`[v0] Frontend server running at http://localhost:${PORT}`)
  console.log(`[v0] Open http://localhost:${PORT} in your browser`)
})
