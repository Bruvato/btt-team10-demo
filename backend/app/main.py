from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import uvicorn

app = FastAPI(title="Orientation Data Receiver")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for orientation data
class OrientationData(BaseModel):
    timestamp: float
    azimuth: float
    pitch: float
    roll: float

# Store recent data in memory (last 1000 points)
orientation_buffer: List[OrientationData] = []
MAX_BUFFER_SIZE = 1000

@app.get("/")
async def root():
    return {
        "message": "Orientation Data Server Running",
        "endpoints": {
            "POST /orientation": "Submit orientation data",
            "GET /orientation": "Retrieve stored orientation data",
            "GET /orientation/latest": "Get the latest orientation reading"
        }
    }

@app.post("/orientation")
async def receive_orientation(data: OrientationData):
    """Receive and store orientation data from MATLAB"""
    orientation_buffer.append(data)
    
    # Keep buffer size manageable
    if len(orientation_buffer) > MAX_BUFFER_SIZE:
        orientation_buffer.pop(0)
    
    return {
        "status": "success",
        "received_at": datetime.now().isoformat(),
        "data": data
    }

@app.get("/orientation")
async def get_all_orientation():
    """Retrieve all stored orientation data"""
    return {
        "count": len(orientation_buffer),
        "data": orientation_buffer
    }

@app.get("/orientation/latest")
async def get_latest_orientation():
    """Get the most recent orientation reading"""
    if orientation_buffer:
        return {
            "status": "success",
            "data": orientation_buffer[-1]
        }
    return {
        "status": "no_data",
        "message": "No orientation data available yet"
    }

@app.delete("/orientation")
async def clear_orientation():
    """Clear all stored orientation data"""
    orientation_buffer.clear()
    return {"status": "success", "message": "Buffer cleared"}

