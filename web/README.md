# Web Interface for Qwen2.5-VL API

Simple web interface for uploading and analyzing images.

## Files

- `index.html` - Web interface (HTML + CSS + JavaScript)
- `server.py` - Proxy server
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration

## Setup

### Option 1: Docker Compose (Recommended)

```bash
cd web
docker-compose build --no-cache
docker-compose up -d

# Access at http://localhost:8080
```

### Option 2: Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
export API_URL=http://localhost:8000
python server.py
```

3. Access at http://localhost:8080

## Usage

1. Click "Select Images" or drag images onto the drop zone
2. (Optional) Enter a custom analysis prompt
3. Click "Analyze" button
4. Wait for results to appear
5. Click images to view full size

## Supported Formats

- JPG, JPEG
- PNG
- WebP
- GIF
- BMP

Maximum file size: 50MB per image

## Features

- Single or batch image upload
- Drag and drop support
- Real-time progress tracking
- Custom analysis prompts
- Image preview on click
- Responsive design
- Error handling and status messages

## Configuration

Environment variables:

```bash
API_URL=http://localhost:8000    # Backend API URL
WEB_PORT=8080                     # Web server port
```

## Deployment

### Docker Compose from root:

```bash
cd web
docker-compose -f docker-compose.yml up -d
```

### Production HTTPS with Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API Endpoints

### GET /
Serves the web interface

### POST /api/analyze-image
Proxy to backend API

Parameters:
- `file`: Image file (multipart)
- `prompt`: Optional custom prompt

### GET /api/health
Check backend API status

## Troubleshooting

### Cannot connect to API
- Ensure API is running: `curl http://localhost:8000/health`
- Check API_URL environment variable
- Verify network connectivity

### Timeout errors
- Model may be loading, wait 2-3 minutes
- Check API logs: `docker-compose logs qwen-vl-api`
- Increase timeout if needed

### Files not uploading
- Check file size (max 50MB)
- Verify file format (JPG, PNG, WebP, GIF, BMP)
- Check browser console for errors

## Performance

- First request: 20-30 seconds (model warming up)
- Subsequent requests: 5-15 seconds per image
- Batch processing: Sequential, one image at a time

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

Requires JavaScript enabled.