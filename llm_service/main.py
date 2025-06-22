from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import uvicorn
import asyncio
from typing import Optional, List
import logging
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Llama-3.1-8B API Server",
    description="LLM API server using Llama-3.1-8B with 4-bit quantization",
    version="1.0.0"
)

# Global variables for model and tokenizer
model = None
tokenizer = None

# Pydantic models for request/response
class GenerateRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 512
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    do_sample: Optional[bool] = True
    num_return_sequences: Optional[int] = 1

class GenerateResponse(BaseModel):
    generated_text: str
    prompt: str
    model_info: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    gpu_memory_used: Optional[str] = None

@app.on_event("startup")
async def load_model():
    """Load the model on startup"""
    global model, tokenizer

    try:
        logger.info("Starting model loading...")

        # Check GPU availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # Configure 4-bit quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

        model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"

        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        logger.info("Loading model with 4-bit quantization...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )

        logger.info("Model loaded successfully!")

        # Print GPU usage if available
        if torch.cuda.is_available():
            logger.info(f"GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f}GB allocated")

    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise e

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Llama-3.1-8B API Server",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    gpu_memory = None
    if torch.cuda.is_available():
        gpu_memory = f"{torch.cuda.memory_allocated()/1024**3:.2f}GB / {torch.cuda.memory_reserved()/1024**3:.2f}GB"

    return HealthResponse(
        status="healthy" if model is not None else "model_not_loaded",
        model_loaded=model is not None,
        gpu_available=torch.cuda.is_available(),
        gpu_memory_used=gpu_memory
    )

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using the loaded model"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        logger.info(f"Generating text for prompt: {request.prompt[:50]}...")

        # Tokenize input
        inputs = tokenizer.encode(request.prompt, return_tensors="pt")

        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = inputs.cuda()

        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=min(request.max_length, 2048),  # Limit max length
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )

        # Decode generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove the original prompt from generated text
        if generated_text.startswith(request.prompt):
            generated_text = generated_text[len(request.prompt):].strip()

        logger.info("Text generation completed")

        return GenerateResponse(
            generated_text=generated_text,
            prompt=request.prompt,
            model_info="meta-llama/Meta-Llama-3.1-8B-Instruct (4-bit quantized)"
        )

    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/clear-cache")
async def clear_cache():
    """Clear GPU cache"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        return {"message": "Cache cleared successfully"}
    return {"message": "No GPU cache to clear"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
