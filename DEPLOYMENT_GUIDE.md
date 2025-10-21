# Qwen2.5-VL API - Complete Deployment Guide

## Directory Structure

```
qwen2.5-vl-api/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   ├── models/          (auto-created)
│   └── logs/            (auto-created)
├── client/
│   ├── simple_client.py
│   ├── advanced_client.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
└── README.md
```

## Installation Steps

### 1. Clone Repository
```bash
git clone <repo-url>
cd qwen2.5-vl-api/server
mkdir -p models logs
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (optional)
```

### 3. Build Docker Image
```bash
docker-compose build --no-cache
```

### 4. Start Service
```bash
docker-compose up -d
```

### 5. Wait for Model Loading
```bash
sleep 150
docker-compose logs -f
# Wait until "Model loaded successfully" appears
```

## Verification

```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/info

# Test analysis
curl -X POST http://localhost:8000/analyze-image \
  -F "file=@test.jpg"
```

## Client Usage

### Setup Client
```bash
cd ../client
pip install -r requirements.txt
cp .env.example .env
```

### Simple Analysis
```bash
python simple_client.py image.jpg "Describe in French"
```

### Batch Processing
```bash
mkdir images
# Add JPG/PNG files to images/
python advanced_client.py
# Outputs: results.json, results.csv
```

## Management Commands

```bash
# View logs
docker-compose logs -f

# Restart service
docker-compose restart qwen-vl-api

# Stop service
docker-compose down

# Stop & remove volumes
docker-compose down -v

# Shell access
docker-compose exec qwen-vl-api bash

# Monitor GPU
nvidia-smi -l 1

# Full rebuild
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

## API Response Examples

### Success Response
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "analysis": "The image shows a detailed landscape with mountains...",
  "inference_time": 8.5,
  "model": "Qwen/Qwen2.5-VL-7B-Instruct",
  "timestamp": "2025-01-21T10:30:00.123456"
}
```

### Error Response
```json
{
  "error": "File too large (max 50MB)",
  "status_code": 413,
  "timestamp": "2025-01-21T10:30:00.123456"
}
```

## Configuration Reference

| Variable | Default | Options |
|----------|---------|---------|
| MODEL_NAME | Qwen/Qwen2.5-VL-7B-Instruct | Any Qwen model |
| DEVICE_MAP | auto | auto, cuda, cpu |
| TORCH_DTYPE | float16 | float16, float32, bfloat16 |
| LOG_LEVEL | WARNING | DEBUG, INFO, WARNING, ERROR |
| MAX_NEW_TOKENS | 1024 | 256-4096 |
| TEMPERATURE | 0.7 | 0.0-2.0 |
| TOP_P | 0.8 | 0.0-1.0 |
| TOP_K | 20 | 0-100 |

## Performance Metrics

| Metric | Value |
|--------|-------|
| Model Size | 7B parameters |
| VRAM Usage | 15-18 GB (float16) |
| Max Batch Size | 1 image |
| First Inference | 20-30 seconds |
| Subsequent Inference | 5-15 seconds |
| Supported Formats | JPG, PNG, WebP, GIF, BMP |
| Max Image Size | 50 MB |

## Troubleshooting Checklist

- [ ] Docker running: `docker ps`
- [ ] GPU available: `nvidia-smi`
- [ ] Port 8000 free: `lsof -i :8000`
- [ ] API responding: `curl http://localhost:8000/health`
- [ ] Model loaded: `docker-compose logs | grep "loaded"`
- [ ] Logs clean: `docker-compose logs | grep ERROR`

## Common Issues

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Reduce MAX_NEW_TOKENS |
| Model not found | Check internet, rebuild |
| Timeout | Increase TIMEOUT in .env |
| Port 8000 in use | Change port in docker-compose.yml |
| Slow inference | Check GPU: `nvidia-smi` |

## Production Checklist

- [ ] Use fixed image tags (not latest)
- [ ] Enable HTTPS with reverse proxy
- [ ] Add authentication (API keys)
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Enable log aggregation
- [ ] Configure auto-restart
- [ ] Test failover
- [ ] Document deployment
- [ ] Backup model cache

## Support Resources

- Model: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
- Docs: https://huggingface.co/docs/transformers
- FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/