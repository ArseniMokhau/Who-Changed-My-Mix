# 🎵 Audio-VIPS: Who changed my mix?
**Blockchain + AI for auditing song versions**

![Next.js](https://img.shields.io/badge/Next.js-black?style=flat&logo=next.js)
![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=flat&logo=nestjs&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Solidity](https://img.shields.io/badge/Solidity-363636?style=flat&logo=solidity&logoColor=white)

A dual-module distributed system designed to verify the authenticity of audio files and protect intellectual property in the music industry. The system detects unauthorized manipulations (such as time-stretching, pitch-shifting, and AI voice cloning) using Deep Learning, while securing the original cryptographic fingerprints of songs on the Blockchain.

Developed as a Team Research Project at the Gdańsk University of Technology.

---

## 🧠 Core Architecture

The system operates on a fully asynchronous, event-driven architecture to handle heavy audio processing without blocking the main server thread.

1. **The Fast Path (Blockchain Verification):** The API generates a lightweight cryptographic Hash of the uploaded audio file and queries the smart contract to verify its original registration.
2. **The Heavy Path (AI Analysis):** The API drops the audio job into a Redis Queue. An isolated Python worker picks up the job, converts the audio into a Mel Spectrogram, and passes it through a Convolutional Neural Network (CNN) to detect visual artifacts left by unauthorized editing. 

Results are combined and sent back to the Next.js frontend via an automated polling mechanism.

---

## 🛠 Tech Stack

* **Frontend:** Next.js (React), TypeScript, Tailwind CSS
* **Backend API:** Node.js, NestJS, TypeScript, TypeORM
* **AI Worker:** Python, FastAPI, PyTorch, Torchaudio
* **Database & Queues:** PostgreSQL, Redis (BullMQ)
* **Blockchain:** Solidity, Hardhat

---

## 📂 Project Structure

```text
/
├── frontend/          # Next.js web application
├── main-api/          # NestJS central hub (HTTP handling, Database, Webhooks)
├── ai-worker/         # Python/FastAPI service for PyTorch audio analysis
└── contracts/         # Hardhat environment for Solidity smart contracts

🚀 Local Development Setup
Because this project spans multiple environments, you will need several dependencies installed globally on your machine before running the system.

Prerequisites
Node.js (v18+)

Python (v3.10+)

PostgreSQL (Running locally or via Docker)

Redis (Running locally or via Docker)

FFmpeg (CRITICAL: Must be installed and added to your system PATH for Torchaudio to decode audio files).

1. Database & Queue
Ensure your local PostgreSQL and Redis instances are running. Create a new database in PostgreSQL named audio_vips (or update your .env to match your DB name).

2. Main API (NestJS)
Bash
cd main-api
npm install
# Configure your .env file with DB and Redis credentials
npm run start:dev
The API will run on http://localhost:3000

3. AI Worker (Python)
Bash
cd ai-worker
python -m venv .venv

# Activate the virtual environment
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
The Worker will run on http://localhost:8000 and immediately start listening to the Redis queue.

4. Frontend (Next.js)
Bash
cd frontend
npm install
npm run dev
The Dashboard will run on http://localhost:3001

🧪 How it Works
Open the frontend and upload an audio file (.wav or .mp3).

The UI will switch to a polling state: AI is Analyzing....

Check your Python terminal—you will see the AI Worker pick up the file, generate the Mel Spectrogram, and calculate the manipulation score.

The Python worker fires a Webhook back to NestJS.

NestJS updates PostgreSQL.

The frontend loop detects the completed status and displays the final validation report.

👥 Team
Arseni Mokhau * Kateryna Dryzhakova * (Add remaining team members here)

Gdańsk University of Technology, 2026



cd API && docker-compose up -d
cd API/main-api && npm run start:dev
cd frontend/frontend && npm run dev
cd ai/ai-worker && .venv\Scripts\activate && uvicorn main:app --reload