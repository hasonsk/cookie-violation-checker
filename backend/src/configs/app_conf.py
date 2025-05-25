import os
from dotenv import load_dotenv, find_dotenv
from typing import Optional

# Load environment variables
load_dotenv(find_dotenv())

class AppConfig:
    """Cấu hình ứng dụng sử dụng environment variables"""

    def __init__(self):
        # Server settings
        self.host: str = os.environ.get("HOST", "0.0.0.0")
        self.port: int = int(os.environ.get("PORT", "8000"))
        self.debug: bool = os.environ.get("DEBUG", "True").lower() == "true"

        # API settings
        self.api_title: str = os.environ.get("API_TITLE", "Cookie Compliance Analyzer")
        self.api_description: str = os.environ.get("API_DESCRIPTION", "API for analyzing cookie policy compliance")
        self.api_version: str = os.environ.get("API_VERSION", "1.0.0")

        # Compliance settings
        self.default_main_domain: str = os.environ.get("DEFAULT_MAIN_DOMAIN", "example.com")
        self.compliance_threshold: int = int(os.environ.get("COMPLIANCE_THRESHOLD", "70"))

        # Database settings
        self.db_name: Optional[str] = os.environ.get("DB_NAME")
        self.collection_name: Optional[str] = os.environ.get("COLLECTION_NAME")
        self.mongodb_pwd: Optional[str] = os.environ.get("MONGODB_PWD")

        # External API settings
        self.hf_token: Optional[str] = os.environ.get("HF_TOKEN")
        self.ngrok_authtoken: Optional[str] = os.environ.get("NGROK_AUTHTOKEN")

    def get_database_url(self) -> Optional[str]:
        """Tạo database URL từ các env variables"""
        if self.mongodb_pwd and self.db_name:
            return f"mongodb+srv://username:{self.mongodb_pwd}@cluster.mongodb.net/{self.db_name}"
        return None

    def is_production(self) -> bool:
        """Kiểm tra có phải môi trường production không"""
        return not self.debug

    def validate_required_configs(self) -> bool:
        """Validate các config bắt buộc"""
        required_configs = [
            ('DB_NAME', self.db_name),
            ('COLLECTION_NAME', self.collection_name),
            ('MONGODB_PWD', self.mongodb_pwd),
        ]

        missing_configs = []
        for name, value in required_configs:
            if not value:
                missing_configs.append(name)

        if missing_configs:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_configs)}")

        return True

    def __repr__(self):
        return f"AppConfig(host={self.host}, port={self.port}, debug={self.debug})"

app_config = AppConfig()
