import logging
from datetime import datetime
from typing import Optional
import time

import torch
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

from app.config import settings, logger
from app.models import ImageAnalysisResponse, HealthResponse
from app.utils import (
    load_image_from_bytes,
    validate_image_format,
    get_gpu_info,
    check_cuda,
    get_device
)

model = None
processor = None
device = None

app = FastAPI(
    title="Qwen2.5-VL Vision API",
    description="Vision-language model API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    global model, processor, device

    try:
        device = get_device()
        logger.info(f"Device: {device}")

        if device == "cuda":
            gpu_info = get_gpu_info()
            logger.info(f"GPU: {gpu_info.get('name')} - {gpu_info.get('total_memory_mb')} MB VRAM")

        logger.info(f"Loading model: {settings.model_name}")

        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            settings.model_name,
            torch_dtype=torch.float16 if settings.torch_dtype == "float16" else torch.bfloat16,
            device_map=settings.device_map,
            trust_remote_code=True,
            attn_implementation="sdpa"
        )

        processor = AutoProcessor.from_pretrained(
            settings.model_name,
            trust_remote_code=True
        )

        logger.info("Model loaded successfully")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    global model, processor
    if model:
        del model
    if processor:
        del processor
    if check_cuda():
        torch.cuda.empty_cache()


@app.get("/")
async def root():
    return {
        "name": "Qwen2.5-VL Vision API",
        "version": "1.0.0",
        "status": "running",
        "model": settings.model_name
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    try:
        gpu_info = get_gpu_info()
        return HealthResponse(
            status="healthy" if model is not None else "initializing",
            model_loaded=model is not None,
            gpu_available=gpu_info.get("available", False),
            vram_used_mb=gpu_info.get("memory_allocated_mb"),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="error",
            model_loaded=False,
            gpu_available=False,
            timestamp=datetime.now()
        )


@app.get("/info")
async def info():
    gpu_info = get_gpu_info()
    return {
        "model": settings.model_name,
        "device": device,
        "cuda_available": check_cuda(),
        "gpu_info": gpu_info,
        "model_loaded": model is not None,
        "max_image_size_mb": settings.max_image_size / 1024 / 1024,
        "supported_formats": settings.supported_formats,
    }


@app.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    prompt: Optional[str] = Query(None)
):
    """
    Analyze image with optional custom prompt.
    
    Supports any language and any type of customization.
    The user prompt is passed directly to the model without modification.
    """
    if model is None or processor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        if not validate_image_format(file.filename, settings.supported_formats):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Accepted: {', '.join(settings.supported_formats)}"
            )

        file_bytes = await file.read()

        if len(file_bytes) > settings.max_image_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {settings.max_image_size / 1024 / 1024:.0f}MB)"
            )

        image = load_image_from_bytes(file_bytes)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image")

        # Use user prompt or default
        analysis_prompt = prompt if prompt else "Describe this image in detail."

        logger.info(f"Analyzing image: {file.filename}")
        logger.info(f"Prompt: {analysis_prompt}")

        # Build messages - user has full control via their prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": analysis_prompt}
                ]
            }
        ]

        start_time = time.time()

        # Apply chat template
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        )

        if device == "cuda":
            inputs = {
                k: v.to(device) if hasattr(v, "to") else v
                for k, v in inputs.items()
            }

        # Generate response
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=settings.max_new_tokens,
                temperature=settings.temperature,
                top_p=settings.top_p,
                top_k=settings.top_k
            )

        # Trim input tokens from output
        generated_ids_trimmed = [
            out_ids[len(in_ids):]
            for in_ids, out_ids in zip(inputs["input_ids"], generated_ids)
        ]

        # Decode output
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        inference_time = time.time() - start_time

        logger.info(f"Analysis completed in {inference_time:.2f}s")

        return ImageAnalysisResponse(
            success=True,
            message="Analysis completed successfully",
            analysis=output_text,
            inference_time=inference_time,
            model=settings.model_name,
            timestamp=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )