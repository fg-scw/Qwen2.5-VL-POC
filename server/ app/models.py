from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ImageAnalysisResponse(BaseModel):
    success: bool
    message: str
    analysis: Optional[str] = None
    inference_time: Optional[float] = None
    model: str
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    vram_used_mb: Optional[float] = None
    timestamp: datetime