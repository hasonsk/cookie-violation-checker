import os
from typing import Optional
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    # API Configuration
    title: str = "Llama-3.1-8B Custom Fine-tuned API Server"
    description: str = "LLM API server using custom fine-tuned Llama-3.1-8B with Unsloth and 4-bit quantization"
    version: str = "1.0.0"

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    model_name: str = "sonhask/meta-Llama-3.1-8B-Instruct-bnb-4bit-DATN"
    max_seq_length: int = 4096
    max_new_tokens: int = 2048
    max_input_length: int = 4096
    load_in_4bit: bool = True

    # Hugging Face Configuration
    huggingface_api_key: Optional[str] = os.environ.get("HUGGINGFACE_API_KEY")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Global settings instance
settings = Settings()
