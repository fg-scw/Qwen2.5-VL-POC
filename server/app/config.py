from pydantic_settings import BaseSettings
from pathlib import Path
import logging
import os


class Settings(BaseSettings):
    model_name: str = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-VL-7B-Instruct")
    device_map: str = os.getenv("DEVICE_MAP", "auto")
    torch_dtype: str = os.getenv("TORCH_DTYPE", "float16")
    
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "1"))
    
    log_level: str = os.getenv("LOG_LEVEL", "WARNING")
    log_file: str = os.getenv("LOG_FILE", "logs/qwen-vl.log")
    
    hf_home: str = os.getenv("HF_HOME", "/app/models")
    hf_token: str = os.getenv("HF_TOKEN", "")
    
    max_new_tokens: int = int(os.getenv("MAX_NEW_TOKENS", "1024"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    top_p: float = float(os.getenv("TOP_P", "0.8"))
    top_k: int = int(os.getenv("TOP_K", "20"))
    
    max_image_size: int = 50 * 1024 * 1024
    supported_formats: tuple = ("jpg", "jpeg", "png", "webp", "gif", "bmp")
    
    class Config:
        case_sensitive = False


settings = Settings()

log_path = Path(settings.log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)