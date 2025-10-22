# Qwen2.5-VL Image Analysis Platform

Complete AI-powered image analysis solution with web interface, REST API, and CLI clients.

## Overview

This platform provides a production-ready image analysis service using Qwen2.5-VL (7B parameters) vision-language model on GPU. Users can upload images via web interface, REST API, or CLI tools for instant AI analysis.

**Key Features:**
- Web interface with drag & drop upload
- Single or batch image processing
- Custom analysis prompts
- REST API for integration
- CLI clients for automation
- Real-time result display
- Responsive mobile design
- GPU accelerated inference

## Project Structure

```
Qwen2.5-VL-POC/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── models.py            # Pydantic models
│   │   └── utils.py             # Utility functions
│   ├── Dockerfile               # API server container
│   ├── docker-compose.yml       # API only compose
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment template
│   ├── models/                  # Model cache (auto-created)
│   └── logs/                    # Application logs
├── web/
│   ├── index.html               # Web interface
│   ├── server.py                # Web proxy server
│   ├── Dockerfile               # Web server container
│   ├── requirements.txt         # Web dependencies
│   └── README.md                # Web guide
├── client/
│   ├── simple_client.py         # Basic CLI client
│   ├── advanced_client.py       # Batch processing
│   ├── requirements.txt         # Client dependencies
│   └── .env.example             # Client config
├── docker-compose.yml           # Complete stack (root)
└── README.md                    # This file
```

## Requirements

- Ubuntu 22.04+ or Linux with CUDA support
- NVIDIA GPU with 24GB+ VRAM (tested on L40S 48GB)
- Docker & Docker Compose
- CUDA 12.4+ compatible GPU drivers

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd Qwen2.5-VL-POC
mkdir -p server/models server/logs
```

### 2. Configure Environment

```bash
cp server/.env.example server/.env
# Edit server/.env if needed (optional)
```

### 3. Deploy Complete Stack

```bash
# Build all services
docker-compose build --no-cache

# Start services (waits for API to be healthy)
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### 4. Access Services

- **Web Interface:** http://localhost:8080
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Usage

### Web Interface

1. Open browser to `http://localhost:8080`
2. Drag & drop images or click "Select Images"
3. (Optional) Enter custom prompt
4. Click "Analyze"
5. View results with image preview

Supported formats: JPG, PNG, WebP, GIF, BMP (max 50MB each)

### API (Direct)

```bash
# Single image analysis
curl -X POST http://localhost:8000/analyze-image \
  -F "file=@image.jpg" \
  -F "prompt=Describe this image"

# Health check
curl http://localhost:8000/health | jq .

# Model info
curl http://localhost:8000/info | jq .
```

### CLI Client (Simple)

```bash
cd client
pip install -r requirements.txt
cp .env.example .env

# Analyze single image
python simple_client.py image.jpg "Your prompt"
```

### CLI Client (Batch)

```bash
cd client
python advanced_client.py
# Processes images/ directory
# Outputs: results.json, results.csv
```

## API Endpoints

### GET /health
Check service health

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
Model and environment information

### POST /analyze-image
Analyze an image

Parameters:
- `file` (multipart): Image file
- `prompt` (query, optional): Custom prompt

Response:
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "analysis": "Detailed image analysis...",
  "inference_time": 8.5,
  "model": "Qwen/Qwen2.5-VL-7B-Instruct",
  "timestamp": "2025-01-21T10:30:00"
}
```

## Docker Management

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f qwen-vl-api

# Web only
docker-compose logs -f qwen-vl-web
```

### Restart Services

```bash
docker-compose restart

# Specific service
docker-compose restart qwen-vl-api
```

### Full Rebuild

```bash
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

## Configuration

Edit `server/.env` to customize:

```env
# Model
MODEL_NAME=Qwen/Qwen2.5-VL-7B-Instruct
DEVICE_MAP=auto
TORCH_DTYPE=float16

# Server
API_PORT=8000
API_WORKERS=1

# Logging
LOG_LEVEL=WARNING
LOG_FILE=logs/qwen-vl.log

# Model Cache
HF_HOME=/app/models
HF_TOKEN=                          # Optional for private models

# Inference Parameters
MAX_NEW_TOKENS=1024
TEMPERATURE=0.7
TOP_P=0.8
TOP_K=20
```

## Performance

| Metric | Value |
|--------|-------|
| Model Size | 7B parameters |
| VRAM Usage | 15-18 GB (float16) |
| First Inference | 20-30 seconds |
| Subsequent | 5-15 seconds |
| Max Batch | Sequential processing |
| Max File Size | 50 MB per image |

## Troubleshooting

### Web Interface Hangs on "Processing"

1. Check console (F12) for errors
2. Verify API health: `curl http://localhost:8000/health`
3. Check logs: `docker-compose logs qwen-vl-api | grep -i error`
4. Restart: `docker-compose restart`

### CUDA Out of Memory

1. Reduce MAX_NEW_TOKENS in .env
2. Or use float32: `TORCH_DTYPE=float32`
3. Check GPU: `nvidia-smi`

### Model Download Timeout

1. Check internet connection
2. Increase timeout in server.py
3. Or pre-download: `huggingface-cli download Qwen/Qwen2.5-VL-7B-Instruct`

### Container Fails to Start

```bash
# Check logs
docker-compose logs qwen-vl-api

# Verify GPU
docker run --rm --gpus all nvidia/cuda:12.4.1-runtime-ubuntu22.04 nvidia-smi

# Rebuild
docker-compose build --no-cache qwen-vl-api
```

## Network Access

### Local Network

Access from other machines:
```
http://<server-ip>:8080    # Web interface
http://<server-ip>:8000    # API
```

### Internet Access

Use reverse proxy with HTTPS:

```bash
# Install Nginx
sudo apt-get install nginx

# Install Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx

# Configure SSL
sudo certbot --nginx -d your-domain.com
```

Nginx config template:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Production Deployment

### Security Recommendations

- Enable HTTPS with SSL/TLS
- Add authentication (API keys)
- Implement rate limiting
- Run behind reverse proxy
- Keep dependencies updated
- Monitor GPU usage
- Enable request logging

### Scaling

For multiple GPUs:

```bash
# Set in docker-compose.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0', '1']  # Multiple GPUs
          capabilities: [gpu]
```


- Application: 1.0.0
- Model: Qwen2.5-VL-7B-Instruct
- Last Updated: 2025-09-22
