const { spawn } = require("child_process")
const path = require("path")
const fs = require("fs")

const backendModules = path.join(__dirname, "backend", "node_modules")
const frontendModules = path.join(__dirname, "frontend", "node_modules")

if (!fs.existsSync(backendModules) || !fs.existsSync(frontendModules)) {
  console.error("\n❌ Error: Dependencies not installed!\n")
  console.log("Please run the following commands first:\n")
  console.log("  cd backend && npm install")
  console.log("  cd ../frontend && npm install")
  console.log("  cd ..\n")
  console.log("Or run this one-liner:\n")
  console.log("  cd backend && npm install && cd ../frontend && npm install && cd ..\n")
  process.exit(1)
}

console.log("[v0] Starting Aether Phoenix servers...\n")

// Start backend server
const backend = spawn("npm", ["start"], {
  cwd: path.join(__dirname, "backend"),
  shell: true,
  stdio: "inherit",
})

// Wait a bit for backend to start, then start frontend
setTimeout(() => {
  const frontend = spawn("npm", ["start"], {
    cwd: path.join(__dirname, "frontend"),
    shell: true,
    stdio: "inherit",
  })

  frontend.on("error", (err) => {
    console.error("[v0] Frontend error:", err)
  })
}, 2000)

backend.on("error", (err) => {
  console.error("[v0] Backend error:", err)
})

// Handle shutdown
process.on("SIGINT", () => {
  console.log("\n[v0] Shutting down servers...")
  backend.kill()
  process.exit()
})
