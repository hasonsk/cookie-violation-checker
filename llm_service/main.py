from unsloth import FastLanguageModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import uvicorn
import asyncio
from typing import Optional, List
import logging
import gc
import os
from huggingface_hub import login
import ast
import json
import pandas as pd
import numpy as np
from datasets import Dataset, load_dataset
from tqdm import tqdm
from typing import List, Dict, Any
from peft import PeftModel, PeftConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Llama-3.1-8B Custom Fine-tuned API Server",
    description="LLM API server using custom fine-tuned Llama-3.1-8B with Unsloth and 4-bit quantization",
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
    top_k: Optional[int] = 50
    do_sample: Optional[bool] = True
    num_return_sequences: Optional[int] = 1
    repetition_penalty: Optional[float] = 1.1
    use_cache: Optional[bool] = True

class GenerateResponse(BaseModel):
    generated_text: str
    prompt: str
    model_info: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    gpu_memory_used: Optional[str] = None
    model_name: str

@app.on_event("startup")
async def load_model():
    """Load the model on startup"""
    global model, tokenizer

    try:
        logger.info("Starting custom model loading...")

        # Check GPU availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # Hugging Face authentication
        logger.info("Setting up Hugging Face authentication...")
        os.environ["HUGGINGFACE_API_KEY"] = "hf_"  # Replace with your actual token
        hf_token = os.environ["HUGGINGFACE_API_KEY"]

        if hf_token and hf_token != "hf_":
            login(hf_token)
            logger.info("Successfully authenticated with Hugging Face")
        else:
            logger.warning("No Hugging Face token provided. Some models may not be accessible.")

        # Model configuration
        new_model_name = "sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6"
        max_seq_length = 4096
        dtype = torch.float16
        load_in_4bit = True

        logger.info(f"Loading model: {new_model_name}")
        logger.info(f"Max sequence length: {max_seq_length}")
        logger.info(f"Data type: {dtype}")
        logger.info(f"4-bit quantization: {load_in_4bit}")

        # Load model and tokenizer using Unsloth
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=new_model_name,
            max_seq_length=max_seq_length,
            dtype=dtype,
            load_in_4bit=load_in_4bit,
        )

        # Prepare model for inference
        FastLanguageModel.for_inference(model)

        logger.info("Model loaded successfully!")

        # Print model info
        logger.info(f"Model type: {type(model)}")
        logger.info(f"Tokenizer type: {type(tokenizer)}")

        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            logger.info("Added padding token")

        # Print GPU usage if available
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")

    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise e

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "message": "Custom Fine-tuned Llama-3.1-8B API Server",
        "version": "1.0.0",
        "model": "sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6",
        "framework": "Unsloth + FastAPI",
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
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        gpu_memory = f"{allocated:.2f}GB / {reserved:.2f}GB"

    return HealthResponse(
        status="healthy" if model is not None else "model_not_loaded",
        model_loaded=model is not None,
        gpu_available=torch.cuda.is_available(),
        gpu_memory_used=gpu_memory,
        model_name="sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6"
    )

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using the loaded fine-tuned model"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        logger.info(f"Generating text for prompt: {request.prompt[:50]}...")

        # Prepare the prompt - you might want to adjust this based on your fine-tuning format
        formatted_prompt = request.prompt

        # Tokenize input
        inputs = tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=min(request.max_length, 4096)
        )

        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=min(request.max_length, 2048),  # Limit max new tokens
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=request.repetition_penalty,
                use_cache=request.use_cache
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
            model_info="sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6 (Unsloth fine-tuned)"
        )

    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/generate-chat", response_model=GenerateResponse)
async def generate_chat(request: GenerateRequest):
    """Generate text using chat format (if your model was fine-tuned with chat format)"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        logger.info(f"Generating chat response for: {request.prompt[:50]}...")

        # Format as chat if your model expects it
        # Adjust this format based on how your model was fine-tuned
        chat_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{request.prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        # Tokenize input
        inputs = tokenizer(
            chat_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096
        )

        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=min(request.max_length, 2048),
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=request.repetition_penalty,
                use_cache=request.use_cache
            )

        # Decode generated text
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant's response
        if "<|start_header_id|>assistant<|end_header_id|>" in full_response:
            generated_text = full_response.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
            # Remove any trailing tokens
            if "<|eot_id|>" in generated_text:
                generated_text = generated_text.split("<|eot_id|>")[0].strip()
        else:
            # Fallback: remove the original prompt
            if full_response.startswith(chat_prompt):
                generated_text = full_response[len(chat_prompt):].strip()
            else:
                generated_text = full_response.strip()

        logger.info("Chat generation completed")

        return GenerateResponse(
            generated_text=generated_text,
            prompt=request.prompt,
            model_info="sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6 (Chat format)"
        )

    except Exception as e:
        logger.error(f"Error during chat generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")

@app.post("/clear-cache")
async def clear_cache():
    """Clear GPU cache"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        return {
            "message": "Cache cleared successfully",
            "gpu_memory_after": f"{allocated:.2f}GB allocated, {reserved:.2f}GB reserved"
        }
    return {"message": "No GPU cache to clear"}

@app.get("/model-info")
async def get_model_info():
    """Get detailed model information"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    info = {
        "model_name": "sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6",
        "model_type": str(type(model)),
        "tokenizer_type": str(type(tokenizer)),
        "vocab_size": tokenizer.vocab_size if hasattr(tokenizer, 'vocab_size') else "Unknown",
        "max_sequence_length": 4096,
        "quantization": "4-bit",
        "framework": "Unsloth",
        "device": "cuda" if torch.cuda.is_available() and next(model.parameters()).is_cuda else "cpu"
    }

    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        info["gpu_memory"] = f"{allocated:.2f}GB allocated, {reserved:.2f}GB reserved"

    return info

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
