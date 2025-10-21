.PHONY: build up down logs restart test clean shell

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "Waiting for model loading..."
	sleep 150
	@curl http://localhost:8000/health | jq .

down:
	docker-compose down

logs:
	docker-compose logs -f qwen-vl-api

restart:
	docker-compose restart qwen-vl-api

test:
	@curl -X POST http://localhost:8000/analyze-image \
		-F "file=@demo.jpeg" 2>/dev/null | jq .

clean:
	docker-compose down -v
	docker system prune -f
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

shell:
	docker-compose exec qwen-vl-api bash

health:
	@curl http://localhost:8000/health | jq .

info:
	@curl http://localhost:8000/info | jq .