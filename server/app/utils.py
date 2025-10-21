import torch
import logging
from pathlib import Path
from PIL import Image
from io import BytesIO
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def check_cuda() -> bool:
    return torch.cuda.is_available()


def get_gpu_info() -> Dict[str, Any]:
    try:
        if not check_cuda():
            return {"available": False}
        
        gpu_count = torch.cuda.device_count()
        if gpu_count == 0:
            return {"available": False}
        
        device_name = torch.cuda.get_device_name(0)
        memory_allocated = torch.cuda.memory_allocated(0) / 1024 / 1024
        memory_reserved = torch.cuda.memory_reserved(0) / 1024 / 1024
        
        try:
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
        except:
            total_memory = None
        
        return {
            "available": True,
            "count": gpu_count,
            "name": device_name,
            "memory_allocated_mb": round(memory_allocated, 2),
            "memory_reserved_mb": round(memory_reserved, 2),
            "total_memory_mb": round(total_memory, 2) if total_memory else None,
        }
    except Exception as e:
        logger.error(f"GPU info error: {e}")
        return {"available": False}


def get_device() -> str:
    return "cuda" if check_cuda() else "cpu"


def load_image_from_bytes(file_bytes: bytes) -> Optional[Image.Image]:
    try:
        img = Image.open(BytesIO(file_bytes))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        return img
    except Exception as e:
        logger.error(f"Image load error: {e}")
        return None


def validate_image_format(filename: str, supported_formats: tuple) -> bool:
    ext = Path(filename).suffix.lower().lstrip(".")
    return ext in supported_formats