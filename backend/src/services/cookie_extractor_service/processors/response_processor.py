import json
import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMResponseProcessor:
    """
    LLM Response Processor - Functional Cohesion
    Single responsibility: Process and clean responses from LLM providers
    """

    @staticmethod
    def clean_json_response(raw_response: str) -> str:
        """
        Clean JSON response from LLM by removing markdown formatting

        Args:
            raw_response: Raw response string from LLM

        Returns:
            Cleaned JSON string
        """
        if not raw_response or not isinstance(raw_response, str):
            logger.warning("Empty or invalid raw response provided")
            return '{"is_specific": 0, "cookies": []}'

        response = raw_response.strip()

        # Remove leading ```json if present
        if response.startswith("```json"):
            response = response[7:].strip()
        elif response.startswith("```"):
            response = response[3:].strip()

        # Remove trailing ``` if present
        if response.endswith("```"):
            response = response[:-3].strip()

        # Remove any leading/trailing whitespace or newlines
        response = response.strip()

        # If response is still empty, return default
        if not response:
            logger.warning("Response is empty after cleaning")
            return '{"is_specific": 0, "cookies": []}'

        return response

    @staticmethod
    def parse_json_response(json_str: str) -> Dict[str, Any]:
        """
        Parse JSON string to dictionary with error handling

        Args:
            json_str: JSON string to parse

        Returns:
            Parsed dictionary or default structure on error
        """
        if not json_str or not isinstance(json_str, str):
            logger.warning("Empty or invalid JSON string provided")
            return {"is_specific": 0, "cookies": []}

        try:
            parsed_data = json.loads(json_str)
            logger.debug("Successfully parsed JSON response")
            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}. Response: {json_str[:200]}...")
            return {"is_specific": 0, "cookies": []}
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            return {"is_specific": 0, "cookies": []}

    @staticmethod
    def extract_json_from_text(text: str) -> Optional[str]:
        """
        Extract JSON content from mixed text response

        Args:
            text: Text that may contain JSON

        Returns:
            Extracted JSON string or None if not found
        """
        if not text:
            return None

        # Try to find JSON objects in the text
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested JSON
            r'\{.*?\}',  # Basic JSON object
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    # Test if it's valid JSON
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

        return None

    @staticmethod
    def validate_response_structure(data: Dict[str, Any], required_fields: list = None) -> bool:
        """
        Validate that response has expected structure

        Args:
            data: Dictionary to validate
            required_fields: List of required field names

        Returns:
            True if structure is valid, False otherwise
        """
        if not isinstance(data, dict):
            logger.warning("Response data is not a dictionary")
            return False

        if required_fields is None:
            required_fields = ["is_specific", "cookies"]

        for field in required_fields:
            if field not in data:
                logger.warning(f"Required field '{field}' missing from response")
                return False

        return True

    @staticmethod
    def sanitize_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize response data by ensuring proper types and defaults

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary
        """
        sanitized = {}

        # Ensure is_specific is integer
        sanitized["is_specific"] = int(data.get("is_specific", 0))

        # Ensure cookies is a list
        cookies = data.get("cookies", [])
        if not isinstance(cookies, list):
            logger.warning("Cookies field is not a list, converting to empty list")
            cookies = []

        sanitized["cookies"] = cookies

        # Preserve other fields
        for key, value in data.items():
            if key not in ["is_specific", "cookies"]:
                sanitized[key] = value

        return sanitized

    def process_llm_response(
        self,
        raw_response: str,
        required_fields: list = None,
        extract_json: bool = True
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for LLM response

        Args:
            raw_response: Raw response from LLM
            required_fields: List of required fields to validate
            extract_json: Whether to attempt JSON extraction from mixed content

        Returns:
            Processed and validated response dictionary
        """
        # Step 1: Clean the response
        cleaned_response = self.clean_json_response(raw_response)

        # Step 2: Try to extract JSON if it's mixed content
        if extract_json and not cleaned_response.strip().startswith('{'):
            extracted_json = self.extract_json_from_text(raw_response)
            if extracted_json:
                cleaned_response = extracted_json

        # Step 3: Parse JSON
        parsed_data = self.parse_json_response(cleaned_response)

        # Step 4: Validate structure
        is_valid = self.validate_response_structure(parsed_data, required_fields)
        if not is_valid:
            logger.warning("Response structure validation failed, using defaults")
            parsed_data = {"is_specific": 0, "cookies": []}

        # Step 5: Sanitize data
        sanitized_data = self.sanitize_response_data(parsed_data)

        return sanitized_data
