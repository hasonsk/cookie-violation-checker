from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from configs.settings import settings
from services.cookie_extract_service import CookieExtractService
from routes import generate
from utils.logging import setup_logging, get_logger

# Setup logging
setup_logging(level=settings.log_level.upper())
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    try:
        cookie_extract_service = CookieExtractService()
        await cookie_extract_service.load_model()
        logger.info("Model loaded successfully during startup")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {e}")

    yield

    logger.info("Shutting down the application...")

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan
)

app.include_router(generate.router, tags=["Generation"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level
    )
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from unsloth import FastLanguageModel
# from peft import PeftConfig, PeftModel
# import torch
# import uvicorn
# import logging
# import os
# from huggingface_hub import login
# from typing import Optional

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Environment variable for Hugging Face API key
# os.environ["HUGGINGFACE_API_KEY"] = "xxx"
# MODEL_NAME = "sonhask/meta-Llama-3.1-8B-Instruct-bnb-4bit-DATN"

# # FastAPI app initialization
# app = FastAPI(
#     title="Llama-3.1-8B Custom Fine-tuned API Server",
#     description="LLM API server using custom fine-tuned Llama-3.1-8B with Unsloth and 4-bit quantization",
#     version="1.0.0"
# )

# # Global variables for model and tokenizer
# model = None
# tokenizer = None

# # Pydantic models for request/response
# class GenerateRequest(BaseModel):
#     prompt: str
#     max_length: Optional[int] = 512
#     temperature: Optional[float] = 0.7
#     top_p: Optional[float] = 0.9
#     top_k: Optional[int] = 50
#     do_sample: Optional[bool] = True
#     num_return_sequences: Optional[int] = 1
#     repetition_penalty: Optional[float] = 1.1
#     use_cache: Optional[bool] = True

# class GenerateResponse(BaseModel):
#     generated_text: str
#     model_info: str

# class HealthResponse(BaseModel):
#     status: str
#     model_loaded: bool
#     gpu_available: bool
#     gpu_memory_used: Optional[str] = None
#     model_name: str

# alpaca_prompt = """You are an expert AI assistant specialized in analyzing website cookie policies. Your task is to read the provided cookie policy text and extract detailed, structured information about each cookie mentioned, adhering strictly to the guidelines and format specified below.
# RESPONSE Format: JSON following structure:

# {{
#   "is_specific": 0,
#   "cookies": [
#      {{
#       "cookie_name": "cookie_name",
#       "declared_purpose": "declared_purpose",
#       "declared_retention": "declared_retention",
#       "declared_third_parties": ["declared_third_parties"],
#       "declared_description": "declared_description"
#     }}, ...
#   ]
# }}
# If no cookies are specifically described, only response {{"is_specific": 0, "cookies": []}}

# ### Instruction:
# {}

# ### Input:
# {}

# ### Response:
# """

# SYSTEM_PROMPT = """
# Extraction guidelines:
# For "is_specific": Determines if the website provides detailed descriptions of individual cookies:
# - Set to 0 if cookies are only described generically (e.g., "performance cookies," "necessary cookies," "Google cookies") without specific explanations
# - Set to 1 if cookies are described with specific names, purposes, retention periods, and third parties. Example: "The '_ga' cookie is used by Google Analytics to distinguish users and is stored for 2 years" would result in is_specific = 1

# For the "cookies" list containing objects, each object has
# - "cookie_name": Extract the exact technical name as mentioned. One object just has only one cookie name, ìf more one, create multiple objects. For example: ga, _gid, _gat --> 3 object cookies
# - "declared_purpose": cookie's purpose. With the following options:
#   * Strictly Necessary: Essential for basic website functionality
#   * Functionality: Personalizes user experience
#   * Analytical: Collects usage data
#   * Targeting/Advertising/Marketing: For personalized ads
#   * Performance: Improves technical performance
#   * Social Sharing: Enables social media integration
#   * Null: When no specific purpose information is provided
# - "declared_retention": Record the exact storage duration as mentioned
# - "declared_third_parties": An list of third parties involved in the use of this cookie for website-owned cookies
# - "declared_description": exact wording from the policy without modification or embellishment

# EXTRACT detailed information about each cookie mentioned in that policy"""


# def formatting_prompts_func(content):
#     EOS_TOKEN = tokenizer.eos_token

#     instruction = SYSTEM_PROMPT
#     input       = content

#     text = alpaca_prompt.format(instruction, input) + EOS_TOKEN
#     return text

# @app.on_event("startup")
# async def load_model():
#     """Load the model on startup."""
#     global model, tokenizer

#     try:
#         device = "cuda" if torch.cuda.is_available() else "cpu"
#         logger.info(f"Using device: {device}")

#         hf_token = os.environ.get("HUGGINGFACE_API_KEY")
#         if hf_token:
#             login(hf_token)
#             logger.info("Authenticated with Hugging Face")
#         else:
#             logger.warning("No Hugging Face token provided.")

#         model_path = MODEL_NAME

#         try:
#             logger.info("Loading model with Unsloth...")
#             model, tokenizer = FastLanguageModel.from_pretrained(
#                 model_name=model_path,
#                 max_seq_length=2048,
#                 dtype=None,
#                 load_in_4bit=True,
#             )
#             logger.info("Model loaded successfully with Unsloth!")
#         except Exception as e:
#             logger.error(f"Error loading model with Unsloth: {e}")
#             logger.info("Falling back to transformers...")

#             try:
#                 config = PeftConfig.from_pretrained(model_path)
#                 base_model = AutoModelForCausalLM.from_pretrained(
#                     config.base_model_name_or_path,
#                     device_map="auto",
#                     torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
#                 )
#                 model = PeftModel.from_pretrained(base_model, model_path)
#                 tokenizer = AutoTokenizer.from_pretrained(model_path)
#             except Exception:
#                 model = AutoModelForCausalLM.from_pretrained(
#                     model_path,
#                     device_map="auto",
#                     torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
#                 )
#                 tokenizer = AutoTokenizer.from_pretrained(model_path)

#         if tokenizer.pad_token is None:
#             tokenizer.pad_token = tokenizer.eos_token
#             logger.info("Added padding token")

#         if torch.cuda.is_available():
#             allocated = torch.cuda.memory_allocated() / 1024**3
#             reserved = torch.cuda.memory_reserved() / 1024**3
#             logger.info(f"GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")

#     except Exception as e:
#         logger.error(f"Error loading model: {e}")
#         raise e

# @app.get("/", response_model=dict)
# async def root():
#     """Root endpoint."""
#     return {
#         "message": "Custom Fine-tuned Llama-3.1-8B API Server",
#         "version": "1.0.0",
#         "model": "sonhask/meta-Llama-3.1-8B-Instruct-bnb-4bit-DATN",
#         "framework": "Unsloth + FastAPI",
#         "endpoints": {
#             "generate": "/generate",
#             "health": "/health",
#             "docs": "/docs"
#         }
#     }

# @app.get("/health", response_model=HealthResponse)
# async def health_check():
#     """Health check endpoint."""
#     gpu_memory = None
#     if torch.cuda.is_available():
#         allocated = torch.cuda.memory_allocated() / 1024**3
#         reserved = torch.cuda.memory_reserved() / 1024**3
#         gpu_memory = f"{allocated:.2f}GB / {reserved:.2f}GB"

#     return HealthResponse(
#         status="healthy" if model else "model_not_loaded",
#         model_loaded=model is not None,
#         gpu_available=torch.cuda.is_available(),
#         gpu_memory_used=gpu_memory,
#         model_name="sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6"
#     )

# @app.post("/generate", response_model=GenerateResponse)
# async def generate_text(request: GenerateRequest):
#     """Generate text using the loaded fine-tuned model."""
#     if model is None or tokenizer is None:
#         raise HTTPException(status_code=503, detail="Model not loaded")

#     try:
#         logger.info(f"Generating text for prompt: {request.prompt[:50]}...")
#         content = formatting_prompts_func(request.prompt)
#         inputs = tokenizer(
#             content,
#             return_tensors="pt",
#             truncation=True,
#             max_length=min(request.max_length, 4096)
#         )

#         if torch.cuda.is_available():
#             inputs = {k: v.cuda() for k, v in inputs.items()}

#         with torch.no_grad():
#             outputs = model.generate(
#                 input_ids=inputs["input_ids"],
#                 attention_mask=inputs["attention_mask"],
#                 max_new_tokens=min(request.max_length, 2048),
#                 temperature=request.temperature,
#                 top_p=request.top_p,
#                 top_k=request.top_k,
#                 do_sample=request.do_sample,
#                 num_return_sequences=request.num_return_sequences,
#                 pad_token_id=tokenizer.pad_token_id,
#                 eos_token_id=tokenizer.eos_token_id,
#                 repetition_penalty=request.repetition_penalty,
#                 use_cache=request.use_cache
#             )

#         generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         result_text = generated_text.split("assistant")[-1].strip()

#         logger.info("Text generation completed")
#         return GenerateResponse(
#             generated_text=result_text,
#             model_info="sonhask/Meta-Llama-3.1-8B-Instruct-bnb-4bit_v6 (Unsloth fine-tuned)"
#         )
#     except Exception as e:
#         logger.error(f"Error during generation: {e}")
#         raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=False,
#         log_level="info"
#     )
