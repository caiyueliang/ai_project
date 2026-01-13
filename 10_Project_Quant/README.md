# Fund Quantitative Backtesting Platform

## Project Structure
- `api/`: Backend (Python + FastAPI)
- `src/`: Frontend (React + TypeScript)
- `docker-compose.yml`: Docker deployment configuration

## Prerequisites
- Docker & Docker Compose
- Node.js (for local frontend dev)
- Python 3.11 (for local backend dev)

## Quick Start (Docker)
1. Build and start services:
   ```bash
   docker-compose up --build
   ```
2. Access Frontend: http://localhost:5173
3. Access Backend API Docs: http://localhost:8000/docs

## Local Development

### Backend
1. Enter `api` directory:
   ```bash
   cd api
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run dev server:
   ```bash
   npm run dev
   ```

## Default Accounts
- Admin: admin / 123456 (Mocked in login for now)
