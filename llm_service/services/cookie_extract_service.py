from typing import Optional, Any
import torch
from unsloth import FastLanguageModel
from peft import PeftConfig, PeftModel
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer

from configs.settings import settings
from utils.prompt_formatter import PromptFormatter
from schemas.generate import GenerateRequest

class CookieExtractService:
    def __init__(self):
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.is_loaded: bool = False
        self.prompt_formatter = PromptFormatter()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    async def load_model(self) -> None:
        try:
            print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
            if settings.huggingface_api_key:
                login(settings.huggingface_api_key)

            await self._load_model()
            self._setup_tokenizer()

            self.is_loaded = True
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.is_loaded = False
            raise

    async def _load_model(self) -> None:
        try:
            print("Loading model with Unsloth...")
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=settings.model_name,
                max_seq_length=settings.max_seq_length,
                dtype=None,
                load_in_4bit=settings.load_in_4bit,
            )
        except Exception as e:
            print(f"Unsloth failed: {e}\nFalling back...")
            await self._fallback_load()

    async def _fallback_load(self) -> None:
        model_path = settings.model_name
        try:
            config = PeftConfig.from_pretrained(model_path)
            base = AutoModelForCausalLM.from_pretrained(
                config.base_model_name_or_path,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            self.model = PeftModel.from_pretrained(base, model_path)
        except:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

    def _setup_tokenizer(self) -> None:
        if self.tokenizer and self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    async def generate_text(self, request: GenerateRequest) -> str:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        try:
            prompt = self.prompt_formatter.format_prompt(request.prompt, self.tokenizer)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=settings.max_input_length).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=settings.max_new_tokens,
                    do_sample=settings.temperature > 0,
                    temperature=settings.temperature,
                    top_p=settings.top_p,
                    pad_token_id=self.tokenizer.pad_token_id
                )

            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self.prompt_formatter.extract_response(generated)

        except Exception as e:
            print(f"Generation failed: {e}")
            raise RuntimeError(f"Generation failed: {e}")

cookie_extract_service = CookieExtractService()
