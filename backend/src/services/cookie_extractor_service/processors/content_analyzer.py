import logging
import re
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Functional Cohesion - Chỉ làm một việc: phân tích và chuẩn bị content"""

    @staticmethod
    def prepare_content_for_analysis(
        original_content: Optional[str] = None,
        table_content: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Prepare content for analysis
        Returns: (content_to_analyze, content_type)
        """
        if table_content and table_content.strip():
            logger.info("Using table content for analysis")
            return table_content.strip(), "table"
        elif original_content and original_content.strip():
            logger.info("Using original content for analysis")
            return original_content.strip(), "original"
        else:
            logger.warning("No valid content provided for analysis")
            return "", "empty"
