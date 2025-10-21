# Qwen2.5-VL Vision API

REST API for image analysis using Qwen2.5-VL vision-language model on GPU.

## Requirements

- **GPU**: NVIDIA L40S (48GB VRAM) or similar
- **OS**: Ubuntu 22.04+
- **Docker**: 20.10+
- **CUDA**: 12.4+

## Quick Start

### 1. Setup

```bash
git clone <repo>
cd qwen2.5-vl-poc/server

mkdir -p models logs
cp .env.example .env
```

### 2. Build & Run

```bash
docker-compose build --no-cache
docker-compose up -d

# Wait for model loading (2-3 minutes)
sleep 150

# Check health
curl http://localhost:8000/health | jq .

# View logs
docker-compose logs -f
```

### 3. Test

```bash
curl -X POST http://localhost:8000/analyze-image \
  -F "file=@image.jpg" \
  -F "prompt=Describe this image"

# Or with Python client
cd ../client
pip install -r requirements.txt
cp .env.example .env
python simple_client.py image.jpg "Your prompt"
```

## API Endpoints

### GET /health
Health check

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu_available": true,
  "vram_used_mb": 15000,
  "timestamp": "2025-01-21T10:30:00"
}
```

### GET /info
Model information

Response:
```json
{
  "model": "Qwen/Qwen2.5-VL-7B-Instruct",
  "device": "cuda",
  "cuda_available": true,
  "gpu_info": {...},
  "model_loaded": true
}
```

### POST /analyze-image
Analyze an image

Parameters:
- `file`: Image file (JPG, PNG, WebP, GIF, BMP)
- `prompt`: Optional custom prompt

Response:
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "analysis": "Image description...",
  "inference_time": 8.5,
  "model": "Qwen/Qwen2.5-VL-7B-Instruct",
  "timestamp": "2025-01-21T10:30:00"
}
```

## Configuration

Edit `server/.env`:

```env
MODEL_NAME=Qwen/Qwen2.5-VL-7B-Instruct
DEVICE_MAP=auto
TORCH_DTYPE=float16

API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

LOG_LEVEL=WARNING
HF_HOME=/app/models

MAX_NEW_TOKENS=1024
TEMPERATURE=0.7
TOP_P=0.8
TOP_K=20
```

## Performance

- First inference: 20-30s
- Subsequent: 5-15s per image
- VRAM: ~15-18GB (float16)
- Supported formats: JPG, PNG, WebP, GIF, BMP

## Clients

### Simple CLI
```bash
python client/simple_client.py image.jpg "Describe"
```

### Batch Processing
```bash
python client/advanced_client.py
# Processes images/ directory, exports JSON/CSV
```

## Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Shell access
docker-compose exec qwen-vl-api bash

# Rebuild
docker-compose build --no-cache
```

## Troubleshooting

### CUDA Out of Memory
- Reduce MAX_NEW_TOKENS in .env
- Or use TORCH_DTYPE=float32 instead of float16

### API Slow
- Check GPU: `nvidia-smi`
- Check network: `ping google.com`
- View logs: `docker-compose logs -f`

### Model Not Found
- Ensure internet connection
- Check HF_TOKEN if private model
- Redownload: `docker-compose build --no-cache`

## Production Deployment

For production, add:
- HTTPS/TLS with reverse proxy (nginx)
- Rate limiting
- Authentication (API keys)
- Monitoring (Prometheus/Grafana)
- Log aggregation

## License

Apache 2.0

## Documentation

- Model: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
- Transformers: https://huggingface.co/docs/transformers
- FastAPI: https://fastapi.tiangolo.com
