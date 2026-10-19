# Road Accident Severity & Hotspot Explorer — Web Application

A full-screen, Google Maps-inspired interactive road safety application for exploring 106,000+ personal-injury road collisions, 293 acute spatial hotspot clusters, driving directions, and machine learning severity prediction across Great Britain.

## Architecture
- **Frontend**: React, TypeScript, Vite, MapLibre GL JS, Lucide Icons.
- **Backend**: FastAPI, Pydantic, Scikit-learn, Uvicorn, Pandas, PyArrow.
- **Services**: CARTO Basemaps, Photon Geocoding, OSRM Driving Directions.

## Quickstart
1. **Backend**:
   ```powershell
   .venv\Scripts\Activate.ps1
   python -m uvicorn webapp.backend.main:app --port 8000 --reload
   ```
2. **Frontend**:
   ```powershell
   cd webapp\frontend
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.
