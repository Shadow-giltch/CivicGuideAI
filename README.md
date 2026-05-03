# 🗳️ CivicGuide AI — Your Election Education Assistant

> An interactive, AI-powered chatbot that helps anyone understand election processes, timelines, voting rights, and civic participation — for any country.

![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%20AI-blue) ![Cloud Run](https://img.shields.io/badge/Deployed%20on-Google%20Cloud%20Run-blue) ![Node.js](https://img.shields.io/badge/Node.js-20-green) ![Express](https://img.shields.io/badge/Express-4.18-lightgrey)

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 💬 **AI Chat** | Ask any election question in plain language |
| 📅 **Timeline Mode** | Get step-by-step election process breakdown |
| 🎯 **Quiz Mode** | Test your civic knowledge interactively |
| 🧠 **Session Memory** | Remembers your conversation context |
| 🌍 **Multi-Country** | Covers India, USA, UK, Australia, Canada & more |
| ⚡ **Mode Detection** | Automatically detects quiz, timeline, or chat mode |

---

## 🚀 Quick Start (Local)

### 1. Clone & Install

```bash
git clone https://github.com/Shadow-giltch/electbot.git
cd electbot
npm install
```

### 2. Set your Gemini API Key

```bash
set GEMINI_API_KEY=AIzaSy...your-key-here
```

### 3. Run

```bash
node server.js
```

Open [http://localhost:8080](http://localhost:8080)

---

## ☁️ Deploy to Google Cloud Run

### Prerequisites
- Google Cloud account with a project
- `gcloud` CLI installed and authenticated
- Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikey)

### Deployment Steps

```bash
# 1. Set your project
gcloud config set project YOUR_PROJECT_ID

# 2. Enable required APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# 3. Create artifact repository
gcloud artifacts repositories create electbot-repo --repository-format=docker --location=us-central1

# 4. Build Docker image
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/electbot-repo/electbot

# 5. Deploy to Cloud Run
gcloud run deploy electbot \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/electbot-repo/electbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=YOUR_GEMINI_KEY"
```

---

## 🏗️ Architecture

```
User Browser
     │
     ▼
Google Cloud Run (Express + Node.js)
     │
     ├── GET  /         → Serve interactive UI
     ├── GET  /health   → Health check endpoint
     └── POST /chat     → AI chat with mode detection
              │
              ▼
     Mode Detection (router.js)
     ├── "quiz"     → Quiz JSON generation
     ├── "timeline" → Step-by-step timeline
     └── "chat"     → General Q&A
              │
              ▼
     Google Gemini API (gemini-2.0-flash)
```

---

## 📁 Project Structure

```
electbot/
├── server.js           # Express server entry point
├── package.json        # Node.js dependencies
├── Dockerfile          # Container config for Cloud Run
├── .gitignore
├── .dockerignore
├── src/
│   ├── ai.js           # Gemini AI integration + session history
│   ├── chat.js         # Chat route handler
│   ├── router.js       # Auto mode detection
│   ├── sessionStore.js # In-memory conversation memory
│   ├── systemPrompt.js # AI personality and rules
│   └── quizPrompt.js   # Quiz generation prompt
└── public/
    └── index.html      # Frontend UI
```

---

## 🧠 How It Works

1. **Chat Mode** — Ask any election question and get a clear, structured answer powered by Gemini AI.

2. **Timeline Mode** — Type "timeline" to get a step-by-step breakdown of the election process for any country.

3. **Quiz Mode** — Type "quiz" to get an interactive multiple-choice quiz that tests your civic knowledge.

4. **Session Memory** — The app remembers the last 10 messages so conversations stay contextual.

---

## 🌍 Supported Countries

India · United States · United Kingdom · Australia · Canada · Germany · France · Japan · Brazil · and more

---

## 📦 Repository Size

All source files are well under the 10 MB limit.

---

## 📄 License

MIT — free for educational and civic use.
