# Project Aether 🌌

An innovative educational platform that spreads awareness about space weather through immersive storytelling, interactive experiences, and AI-powered learning.

## 🌟 Overview

Project Aether combines cutting-edge technology with engaging narratives to educate users about space weather phenomena. Meet Aether, a 1000-year-old cosmic Phoenix who has witnessed countless space weather events and is here to share his wisdom through interactive conversations, curated stories, games, and scientific predictions.

## ✨ Features

### 1. **Home Dashboard**
Live space weather data visualization from NASA sources with real-time updates and project introduction.

### 2. **Aether's Tales**
- **AI Chatbot**: Interact with Aether, an ancient Phoenix powered by Gemini API with ElevenLabs voice synthesis
- **Aether's Library**: Curated collection of real space weather event stories narrated in Aether's mystical voice, available as interactive cards with audio playback

### 3. **Interactive Game**
An educational adventure game where you play as an astronaut exploring space events:
- Learn about various space weather phenomena
- Battle enemies while discovering cosmic mysteries
- Complete a quiz to test your knowledge
- Guided by Aether throughout your journey

### 4. **Aurora Prediction Model**
- Interactive 3D Earth visualization
- Click any location to predict Aurora intensity
- Powered by Random Forest machine learning models
- Real-time predictions based on longitude and latitude

### 5. **User Survey**
Collect data on public knowledge about space weather to measure educational impact.

## 📁 Project Structure

```
Project-Aether/
├── ML/
│   ├── Aurora_model_training.ipynb    # Model training notebook
│   ├── aurora_model_temp.pkl          # Random Forest model (pickle)
│   └── Aurora_model.onxx              # ONNX model for web deployment
│
├── backend/
│   ├── .env                           # API keys (Gemini, ElevenLabs)
│   ├── server.js                      # Backend server
│   ├── package.json
│   ├── package-lock.json
│   └── .gitignore
│
├── frontend/
│   ├── assets/
│   │   ├── comic/                     # Comic panels
│   │   ├── stories/                   # MP3 audio files for stories
│   │   └── *.png                      # Aether character images
│   ├── css/
│   │   ├── dashboard.css
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── earth3d-space.js
│   │   ├── earth3d.js
│   │   ├── main.js
│   │   ├── phoenix.js
│   │   └── sun3d.js
│   ├── index.html
│   ├── server.js
│   ├── package.json
│   ├── package-lock.json
│   └── .gitignore
│
├── game/
│   └── Aether.exe                     # Educational space game
│
├── README.md
├── requirements.txt
└── start-all.js                       # Unified startup script
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v14 or higher)
- **npm** (comes with Node.js)
- **Python dependencies** for ML model:
  - `numpy>=1.21.0`
  - `scikit-learn>=1.0.0`

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Project-Aether
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   npm install
   cd ..
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the `backend/` directory with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_VOICE_ID=your_voice_id
   ```

5. **Start the application**
   ```bash
   node start-all.js
   ```

6. **Access the application**
   
   Open your browser and navigate to:
   ```
   http://localhost:8080/
   ```

## 🤖 Machine Learning Model

The Aurora prediction model uses Random Forest algorithm trained on geospatial data to predict Aurora intensity based on:
- **Longitude**: Geographic longitude position
- **Latitude**: Geographic latitude position

Two model formats are provided:
- **PKL format**: Standard scikit-learn pickle format
- **ONNX format**: Optimized for web deployment with better performance

## 🎮 Game Installation

The Aether game executable is located in the `game/` folder. Download and run `Aether.exe` to begin your educational space adventure.

## 🛠️ Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript, Three.js (3D visualizations)
- **Backend**: Node.js, Express.js
- **AI/ML**: 
  - Gemini API (conversational AI)
  - ElevenLabs (voice synthesis)
  - scikit-learn (Aurora prediction)
  - ONNX Runtime (model deployment)
- **Game Development**: Unity/Custom game engine

## 📚 Educational Impact

Project Aether aims to:
- Increase public awareness of space weather phenomena
- Make complex scientific concepts accessible through storytelling
- Provide interactive learning experiences
- Collect data on space weather knowledge gaps

## 👥 Authors

- [Kareem Taha](https://github.com/Kareem-Taha-05)  
- [Bassel Shaheen](https://github.com/BasselShaheen06)  
- [Karim Hassan](https://github.com/karimhassan-808)  
- [Hakeem Taha](https://github.com/Hakeem-Taha-06)  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).


## 🙏 Acknowledgments

- NASA for space weather data APIs
- Gemini API for conversational AI capabilities
- ElevenLabs for voice synthesis technology

---

**Experience the cosmos through Aether's eyes. Learn, explore, and understand the weather of space.** 🌠
