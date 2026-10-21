# Google Maps-Inspired Web Application Guide

## 1. Architecture Overview
This application upgrades the project into a modern, full-screen interactive mapping application built with **React**, **Vite**, **TypeScript**, and **MapLibre GL JS**, powered by a high-performance **FastAPI** backend that serves historical collision data, precomputed spatial hotspots, and real-time machine learning severity predictions.

```
DSE PRO/
├── app/
│   └── dashboard.py                         # Untouched original Streamlit application
├── webapp/
│   ├── backend/                             # FastAPI backend service
│   │   ├── main.py                          # API router & CORS middleware
│   │   ├── schemas.py                       # Pydantic request/response validation
│   │   ├── services.py                      # Data access, ML inference, Geocoding & Routing
│   │   ├── requirements.txt                 # Backend dependency manifest
│   │   └── tests/
│   │       └── test_api.py                  # API unit & integration tests (7 passing)
│   └── frontend/                            # React + Vite + TypeScript application
│       ├── src/
│       │   ├── components/
│       │   │   ├── MapLibreMap.tsx          # Fullscreen MapLibre GL map & layers
│       │   │   ├── SearchBar.tsx            # Floating search & driving direction bar
│       │   │   ├── LayerFilterBar.tsx       # Severity, speed, hotspot & style toggles
│       │   │   ├── CollisionDetailCard.tsx  # Floating card for clicked collisions
│       │   │   ├── HotspotDetailCard.tsx    # Floating card for clicked DBSCAN clusters
│       │   │   ├── LocationCard.tsx         # Floating card for searched locations
│       │   │   ├── DirectionsCard.tsx       # Route distance, duration & summary
│       │   │   └── PredictionModal.tsx      # ML severity prediction form & probabilities
│       │   ├── App.tsx                      # Root state & responsive layout
│       │   ├── api.ts                       # API client
│       │   └── types.ts                     # TypeScript definitions
│       ├── package.json
│       └── vite.config.ts                   # Vite dev server & /api proxy configuration
```

---

## 2. Technology Stack & Zero-Cost Providers

| Capability | Technology / Provider | Cost | Auth / API Key | Attribution & Terms |
|---|---|---|---|---|
| **Frontend Framework** | React 19 + TypeScript + Vite | ₹0 | None | MIT License |
| **Map Rendering** | MapLibre GL JS | ₹0 | None | BSD-3-Clause |
| **Map Basemap Tiles** | CARTO Positron, Voyager, Dark Matter | ₹0 | None | © [CARTO](https://carto.com/), © [OpenStreetMap](https://www.openstreetmap.org/copyright) |
| **Backend API** | FastAPI + Uvicorn + Pydantic | ₹0 | None | MIT License |
| **ML Inference** | Scikit-learn (Balanced Random Forest) | ₹0 | None | BSD-3-Clause (reuses existing model) |
| **Location Search** | Photon by Komoot (OSM Search) | ₹0 | None | Permissive OpenStreetMap geocoding |
| **Driving Directions** | OSRM (Open Source Routing Machine) | ₹0 | None | Public demo routing server |

---

## 3. Local Development & Launch Instructions

### Prerequisites
- Python 3.10.11 (with project `.venv` activated)
- Node.js (v18.0.0 or later, tested with v24.16.0)

### Terminal 1: Launch FastAPI Backend (Port 8000)
```powershell
cd "C:\Users\JOYCE GRACY\OneDrive\Documents\DSE PRO"
.venv\Scripts\Activate.ps1
python -m uvicorn webapp.backend.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Swagger Documentation will be accessible at `http://localhost:8000/docs`.*

### Terminal 2: Launch React Frontend (Port 5173)
```powershell
cd "C:\Users\JOYCE GRACY\OneDrive\Documents\DSE PRO\webapp\frontend"
npm run dev
```
*Web application will be accessible at `http://localhost:5173`.*

### Terminal 3 (Optional): Launch Original Streamlit Dashboard (Port 8501)
```powershell
cd "C:\Users\JOYCE GRACY\OneDrive\Documents\DSE PRO"
.venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

---

## 4. Running Automated Tests

### Root Tests (Original 15 Tests):
```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

### Backend API Tests (7 Tests):
```powershell
.venv\Scripts\python.exe -m pytest webapp/backend/tests/ -v
```

### Run All Tests Together:
```powershell
.venv\Scripts\python.exe -m pytest -v
```

### Build Frontend for Production:
```powershell
cd webapp/frontend
npm run build
```

---

## 5. Important Data and Boundary Caveats
- **Geographic Coverage**: The collision and hotspot datasets cover Great Britain in 2022. Collisions will only render within Great Britain bounds.
- **Exposure Caveat**: High collision counts at specific junctions or urban centers reflect concentrated exposure rather than validated risk rates.
- **Conditional Prediction**: The ML model predicts collision severity *conditional on a collision having occurred*; it does not predict occurrence probability.


---

## 6. Production Deployment & Live URLs

### 6.1 Backend Web Service (Render)
- **Status**: Deployed & Verified
- **Public URL**: `https://road-accident-api.onrender.com`
- **Health Endpoint**: `https://road-accident-api.onrender.com/api/health`
- **API Docs (Swagger)**: `https://road-accident-api.onrender.com/docs`
- **Configuration**:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn webapp.backend.main:app --host 0.0.0.0 --port $PORT`
  - Python Version: `3.10.11`

### 6.2 Free Frontend Static Hosting Options

#### Option A: GitHub Pages (Recommended — 100% Free, Automated CI/CD)
The repository includes an automated GitHub Actions deployment workflow at [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml).
- **Public Website URL**: `https://joycegracy72-sys.github.io/road-accident-severity-analysis/`
- **Cost**: Free (No credit card or billing details required)
- **Deployment Activation**:
  1. In the GitHub repository, navigate to **Settings** -> **Pages**.
  2. Under **Build and deployment** -> **Source**, select **GitHub Actions**.
  3. Every push to `main` automatically runs frontend tests, compiles the production bundle with `VITE_API_BASE_URL=https://road-accident-api.onrender.com/api`, and publishes to GitHub Pages.

#### Option B: Render Static Site (100% Free Tier, Same Platform as API)
The repository includes a [`render.yaml`](../render.yaml) blueprint declaring both the backend and frontend services.
- **Public Website URL**: `https://road-accident-explorer.onrender.com` (or chosen name)
- **Cost**: Free (Render provides 100 GB/month free static bandwidth, no billing required)
- **Deployment Settings**:
  - Service Type: **Static Site**
  - Name: `road-accident-explorer`
  - Root Directory: `webapp/frontend`
  - Build Command: `npm run build`
  - Publish Directory: `dist`
  - Environment Variable: `VITE_API_BASE_URL` = `https://road-accident-api.onrender.com/api`

#### Option C: Vercel or Netlify (Free Hobby Tier)
- **Framework Preset**: Vite
- **Root Directory**: `webapp/frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variable**: `VITE_API_BASE_URL` = `https://road-accident-api.onrender.com/api`
