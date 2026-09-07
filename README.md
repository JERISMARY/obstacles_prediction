
## AI-Powered detection platform

> **Prototype**
> Public buses act as mobile urban sensing units. AI analyses bus camera footage to detect traffic congestion and road defects in real-time.

---

## 🎯 How This Solves

This problem statement asks for a mobile urban intelligence system that uses existing city infrastructure (buses) as sensing units to monitor road conditions and traffic without deploying fixed sensors everywhere.

**Our solution:**
- Every bus carries a camera (existing hardware)
- AI (YOLOv8) analyses the footage in real-time
- Detections are tagged with GPS + timestamp + bus ID and become structured events
- Events flow to a central backend → stored in MongoDB → visualised on a GIS dashboard
- City administrators get real-time awareness of:
  - Traffic congestion with severity levels
  - Potholes and road damage with GPS location
  - Waterlogging and sign damage
- The same infrastructure can be expanded (ANPR, accident detection, etc.)

This is **scalable** (more buses = more coverage), **cost-effective** (reuses existing fleet), and **actionable** (events directly trigger maintenance workflows).

---

## 🏗️ Architecture

```
Bus Camera
    ↓
Video Upload API (FastAPI)
    ↓
Frame Extraction (OpenCV)
    ↓
Vehicle Detection (YOLOv8n COCO)   ←→  Pothole Detection (Custom YOLO — plug-in)
    ↓                                           ↓
Traffic Analyzer                         Event Generator
(density score, level)                   (GPS + timestamp)
    ↓
Event Store (MongoDB)
    ↓
REST APIs (FastAPI)
    ↓
React Dashboard (Leaflet GIS Map + Recharts)
```

---

## ✨ Features

### Core (P0 — Fully Working)
- ✅ YOLOv8 vehicle detection (car, bus, truck, motorcycle, pedestrian)
- ✅ Traffic density scoring (Low / Moderate / High / Severe)
- ✅ Event generation with GPS, timestamp, bus ID, confidence
- ✅ GPS simulation for 5 Madurai bus routes
- ✅ MongoDB storage with full CRUD APIs
- ✅ React GIS dashboard with Leaflet + CartoDB dark tiles
- ✅ Incident map with clickable markers showing full details
- ✅ Bus fleet monitoring with real-time status
- ✅ Video upload and background processing pipeline
- ✅ Demo Mode with realistic sample data

### Dashboard (P1)
- ✅ Statistics cards (buses, incidents, road defects, traffic alerts)
- ✅ Severity breakdown pie chart
- ✅ Incident type bar chart
- ✅ Incident table with filtering (type, severity, status, bus)
- ✅ Status workflow: New → Verified → In Progress → Resolved
- ✅ Analytics page with traffic density trends
- ✅ Live monitoring with 5-second refresh and incident feed

### Optional (P2 — Stubs ready)
- 🔧 Pothole/road-damage model (plug-in interface ready)
- 🔧 Number plate detection (architecture documented)
- 🔧 Real GPS hardware (GPSProvider interface ready)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, React Router 6 |
| Map | Leaflet + CartoDB Dark tiles |
| Charts | Recharts |
| HTTP | Axios |
| Backend | Python, FastAPI |
| Database | MongoDB (Motor async driver) |
| AI | YOLOv8 (ultralytics), OpenCV |
| GPS | Custom simulator (real hardware interface ready) |

---

## 📁 Folder Structure

```
DEMO/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── buses.py         # Bus CRUD + GPS
│   │   │   ├── events.py        # Event CRUD + filters
│   │   │   ├── video.py         # Upload + processing
│   │   │   └── statistics.py    # Stats + heatmap
│   │   ├── ai/
│   │   │   ├── config.py        # AI thresholds
│   │   │   ├── detector.py      # Base detector interface
│   │   │   ├── vehicle_detector.py  # YOLOv8 vehicle detection
│   │   │   ├── pothole_detector.py  # Custom model stub
│   │   │   ├── traffic_analyzer.py  # Density calculation
│   │   │   └── event_generator.py   # Detection → Event
│   │   ├── database/
│   │   │   └── connection.py    # Motor MongoDB client
│   │   ├── models/
│   │   │   ├── bus.py           # Bus Pydantic models
│   │   │   ├── event.py         # Event Pydantic models
│   │   │   └── traffic.py       # Traffic + Job models
│   │   ├── services/
│   │   │   ├── gps_simulator.py # GPS simulation engine
│   │   │   ├── video_processor.py # Full processing pipeline
│   │   │   └── demo_data.py     # Demo seed data
│   │   ├── config.py            # App settings
│   │   └── main.py              # FastAPI app + lifespan
│   ├── uploads/                 # Video and evidence storage
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx      # Navigation sidebar
│   │   │   ├── TopHeader.jsx    # Page header + clock
│   │   │   ├── GISMap.jsx       # Leaflet map wrapper
│   │   │   ├── EventPopup.jsx   # Map marker popup
│   │   │   └── IncidentTable.jsx # Incident data table
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Main command centre
│   │   │   ├── LiveMonitoring.jsx # Real-time view
│   │   │   ├── Incidents.jsx    # Incident management
│   │   │   ├── Buses.jsx        # Fleet monitoring
│   │   │   ├── Analytics.jsx    # Charts and trends
│   │   │   ├── VideoAnalysis.jsx # Upload pipeline
│   │   │   └── Settings.jsx     # System config
│   │   ├── services/
│   │   │   └── api.js           # Axios API layer
│   │   ├── hooks/
│   │   │   └── useApi.js        # Data fetching hooks
│   │   ├── utils/
│   │   │   └── format.js        # Formatting utilities
│   │   ├── App.jsx              # Router + layout
│   │   ├── index.css            # Design system
│   │   └── main.jsx             # Entry point
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB 6+ (local or Atlas)

### 1. Clone / Open the project

```
cd DEMO
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env if needed (MongoDB URI, etc.)
```

### 3. MongoDB Setup

Start MongoDB locally:
```bash
# Windows (if installed as service)
net start MongoDB

# Or start manually
mongod --dbpath C:\data\db
```

Or use MongoDB Atlas — update `MONGODB_URI` in `.env`.

The app will **automatically** seed demo data on first startup.

### 4. Frontend Setup

```bash
cd frontend
npm install
```

---

## 🏃 Running the Application

### Start Backend

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `urban_intel` | Database name |
| `DEMO_MODE` | `true` | Enable demo data seeding |
| `YOLO_MODEL` | `yolov8n.pt` | YOLO model path |
| `UPLOAD_DIR` | `uploads` | Video upload directory |
| `MAX_UPLOAD_SIZE_MB` | `500` | Max video file size |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

---

## 🤖 AI Model Setup

### Vehicle Detection (Working out of the box)
Uses YOLOv8n pretrained on COCO dataset.
- Automatically downloaded by ultralytics on first run (~6 MB)
- Detects: car, bus, truck, motorcycle, bicycle, person

### Pothole / Road Defect Detection (Plug-in)
Requires a custom-trained model. To add:

1. Train YOLOv8 on a road defect dataset:
   - [RDD2022 Dataset](https://github.com/sekilab/RoadDamageDetector)
   - [Roboflow Pothole Dataset](https://roboflow.com/search?q=pothole)

2. Save weights: `backend/models/pothole_yolov8.pt`

3. Update `backend/app/ai/config.py`:
   ```python
   POTHOLE_MODEL_PATH = "models/pothole_yolov8.pt"
   ```

Classes your model should detect:
- `0: pothole`
- `1: road_damage`
- `2: waterlogging`
- `3: traffic_sign_damage`

---

## 🎭 Demo Mode

When `DEMO_MODE=true` (default), the system pre-populates:

- **5 buses** on realistic Madurai city routes
- **10 incidents** (potholes, congestion, waterlogging, etc.)
- **5 traffic records** with vehicle type breakdowns

All demo data is clearly labelled with `is_demo: true` and displayed with **⚡ DEMO DATA** in the UI.

To disable demo mode and use only real data:
```
DEMO_MODE=false
```

---

## 📡 API Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health check |
| `/api/buses` | GET | List all buses |
| `/api/buses/{id}` | GET | Bus details |
| `/api/buses/{id}/events` | GET | Bus-specific events |
| `/api/buses/{id}/location` | GET | Current GPS location |
| `/api/events` | GET | List events (with filters) |
| `/api/events/{id}` | GET | Event details |
| `/api/events` | POST | Create event |
| `/api/events/{id}` | PATCH | Update event status |
| `/api/statistics` | GET | Dashboard statistics |
| `/api/traffic` | GET | Traffic records |
| `/api/heatmap` | GET | Heatmap data points |
| `/api/video/upload` | POST | Upload video file |
| `/api/video/process` | POST | Start AI processing |
| `/api/video/status/{id}` | GET | Job status polling |
| `/api/video/jobs` | GET | List processing jobs |

Full interactive docs at `http://localhost:8000/docs`

---

## 🗺️ GPS Simulation

5 bus routes simulated in Madurai city (real coordinates):

| Bus | Route | Start | End |
|-----|-------|-------|-----|
| BUS-101 | Route 1 | Madurai Central | Anna Nagar |
| BUS-102 | Route 2 | Meenakshi Temple | Kochadai |
| BUS-103 | Route 3 | Mattuthavani | Goripalayam |
| BUS-104 | Route 4 | Madurai Junction | Vilangudi |
| BUS-105 | Route 5 | Bypass Road | Bypass Road |

Real GPS hardware can replace the simulator by implementing the `GPSProvider` interface in `services/gps_simulator.py`.

---

## 🔮 Future Improvements

1. **Real-time WebSocket streaming** — push events to dashboard without polling
2. **Custom pothole model** — train on RDD2022 dataset
3. **ANPR module** — vehicle number plate recognition for hit-and-run detection
4. **Mobile app** — driver-side app for manual incident reporting
5. **Maintenance workflow** — integration with municipal work order systems
6. **Historical analytics** — trend analysis, hotspot mapping
7. **Alert system** — SMS/email notifications for critical incidents
8. **Multi-city deployment** — configurable city/region support
9. **Edge deployment** — run inference on Raspberry Pi / Jetson on the bus
10. **Real GPS integration** — NMEA serial or REST tracker API

---


*All demo data is simulated and clearly labelled. Not real-world measurements.*
