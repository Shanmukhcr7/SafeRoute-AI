from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from ml.predictor import RiskPredictorAPI
from context.context_engine import ContextEngine
from context.dynamic_risk_engine import DynamicRiskEngine

app = FastAPI(
    title="Road Risk AI API",
    description="Intelligent Transportation System & Context Awareness Engine REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize engines
try:
    predictor = RiskPredictorAPI()
    context_engine = ContextEngine()
    risk_engine = DynamicRiskEngine()
except Exception as e:
    print(f"Warning: Engines could not initialize natively. {e}")
    predictor = None

# --- Schemas ---
class PredictionRequest(BaseModel):
    rain: bool
    fog: bool
    snow: bool
    is_curve: bool
    hour: int
    speed: float
    lat: float
    lon: float

class SimulateRequest(BaseModel):
    scenario_id: str

# --- Endpoints ---

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "model_loaded": predictor is not None,
        "api_version": "1.0.0"
    }

@app.get("/api/zones")
def get_zones():
    return {"message": "Endpoint to return H3 zone statuses (Safe/Critical)."}

@app.get("/api/telemetry")
def get_telemetry():
    return {"message": "Endpoint to stream live digital twin telemetry."}

@app.get("/api/alerts")
def get_alerts():
    return {"message": "Endpoint returning active ADAS alerts."}

@app.post("/api/predict")
def predict_severity(req: PredictionRequest):
    """Generates an AI severity prediction based on raw weather and GPS data."""
    if not predictor:
        raise HTTPException(status_code=503, detail="Model not loaded")
        
    raw_data = req.dict()
    # Mock some standard conversions
    raw_data['is_rain'] = 1 if req.rain else 0
    raw_data['is_fog'] = 1 if req.fog else 0
    raw_data['is_snow'] = 1 if req.snow else 0
    raw_data['is_night'] = 1 if req.hour >= 20 or req.hour <= 5 else 0
    
    result = predictor.predict(raw_data)
    return result

@app.post("/api/context")
def build_context(req: PredictionRequest):
    """Processes raw data into the full Context Object (Modifiers & Explanations)."""
    raw_data = req.dict()
    raw_data['road_type'] = "Highway"
    ctx = context_engine.build_context(raw_data)
    return ctx

@app.post("/api/simulate")
def run_simulation(req: SimulateRequest):
    """Triggers the backend Simulation Manager for a given scenario (e.g., 'Heavy Rain')."""
    return {"status": "started", "scenario": req.scenario_id, "message": "Simulation running in background."}
