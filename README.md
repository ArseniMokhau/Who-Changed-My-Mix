# Who Changed My Mix

cd API && docker-compose up -d
cd API/main-api && npm run start:dev
cd frontend/frontend && npm run dev
cd ai/ai-worker && .venv\Scripts\activate && uvicorn main:app --reload