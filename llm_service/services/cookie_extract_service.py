import os
from typing import Optional, Tuple, Any
import torch
from unsloth import FastLanguageModel
from peft import PeftConfig, PeftModel
from huggingface_hub import login

from configs.settings import settings
from utils.logging import get_logger
from utils.prompt_formatter import PromptFormatter
from schemas.generate import GenerateRequest

logger = get_logger(__name__)


class CookieExtractService:
    def __init__(self):
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.is_loaded: bool = False
        self.prompt_formatter = PromptFormatter()

    async def load_model(self) -> None:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")

            await self._authenticate_huggingface()

            await self._load_model_with_fallback()

            self._setup_tokenizer()
            self._log_gpu_memory()

            self.is_loaded = True
            logger.info("Model loading completed successfully")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_loaded = False
            raise e

    async def _authenticate_huggingface(self) -> None:
        hf_token = settings.huggingface_api_key
        if hf_token:
            login(hf_token)
            logger.info("Authenticated with Hugging Face")
        else:
            logger.warning("No Hugging Face token provided.")

    async def _load_model_with_fallback(self) -> None:
        model_path = settings.model_name

        try:
            # Primary: Load with Unsloth
            logger.info("Loading model with Unsloth...")
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=model_path,
                max_seq_length=settings.max_seq_length,
                dtype=None,
                load_in_4bit=settings.load_in_4bit,
            )
            logger.info("Model loaded successfully with Unsloth!")

        except Exception as e:
            logger.error(f"Error loading model with Unsloth: {e}")
            logger.info("Falling back to transformers...")

            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                # Fallback 1: PEFT model
                config = PeftConfig.from_pretrained(model_path)
                base_model = AutoModelForCausalLM.from_pretrained(
                    config.base_model_name_or_path,
                    device_map="auto",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                self.model = PeftModel.from_pretrained(base_model, model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                logger.info("Model loaded with PEFT fallback")

            except Exception as peft_error:
                logger.error(f"PEFT fallback failed: {peft_error}")

                # Fallback 2: Standard transformers
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    device_map="auto",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                logger.info("Model loaded with standard transformers fallback")

    def _setup_tokenizer(self) -> None:
        if self.tokenizer and self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.info("Added padding token")

    def _log_gpu_memory(self) -> None:
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            logger.info(f"GPU Memory: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")

    def get_gpu_memory_info(self) -> Optional[str]:
        if not torch.cuda.is_available():
            return None

        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        return f"{allocated:.2f}GB / {reserved:.2f}GB"

    async def generate_text(self, request: GenerateRequest) -> str:
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")

        try:
            logger.info(f"Generating text for prompt: {request.prompt[:50]}...")

            formatted_prompt = self.prompt_formatter.format_prompt(
                request.prompt,
                self.tokenizer
            )

            # Tokenize input
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=min(request.max_length, settings.max_input_length)
            )

            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_new_tokens=min(request.max_length, settings.max_new_tokens),
                    temperature=request.temperature,
                    top_p=request.top_p,
                    top_k=request.top_k,
                    do_sample=request.do_sample,
                    num_return_sequences=request.num_return_sequences,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=request.repetition_penalty,
                    use_cache=request.use_cache
                )

            # Decode and extract response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            result_text = self.prompt_formatter.extract_response(generated_text)

            logger.info("Text generation completed")
            return result_text

        except Exception as e:
            logger.error(f"Error during generation: {e}")
            raise RuntimeError(f"Generation failed: {e}")
