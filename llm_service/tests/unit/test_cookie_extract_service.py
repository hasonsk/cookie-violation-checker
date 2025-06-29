import pytest
from unittest.mock import MagicMock, patch
import json
import sys

# Create a mock for the unsloth module
mock_unsloth = MagicMock()
mock_unsloth.FastLanguageModel = MagicMock()
mock_unsloth.FastLanguageModel.from_pretrained.return_value = (MagicMock(), MagicMock())

# Add the mock to sys.modules before importing the service
sys.modules['unsloth'] = mock_unsloth
sys.modules['unsloth.FastLanguageModel'] = mock_unsloth.FastLanguageModel

# Mock torch.cuda.is_available
with patch('torch.cuda.is_available', return_value=False):
    from llm_service.services.cookie_extract_service import LlamaCookieExtractionService, alpaca_prompt, SYSTEM_PROMPT

@pytest.fixture
def mock_llama_service():
    """Fixture to provide a mocked LlamaCookieExtractionService instance."""
    # Reset mocks for each test to ensure isolation
    mock_unsloth.FastLanguageModel.from_pretrained.reset_mock()
    mock_unsloth.FastLanguageModel.from_pretrained.return_value = (MagicMock(), MagicMock())

    with patch('torch.cuda.is_available', return_value=False):
        service = LlamaCookieExtractionService(model_path="mock/path")
        service.model = mock_unsloth.FastLanguageModel.from_pretrained.return_value[0]
        service.tokenizer = mock_unsloth.FastLanguageModel.from_pretrained.return_value[1]
        return service

def test_llama_service_initialization(mock_llama_service):
    """Test that the service initializes correctly without loading the actual model."""
    assert mock_llama_service.device == "cpu"
    mock_llama_service.model.eval.assert_called_once()
    # Ensure from_pretrained was called on the global mock
    mock_unsloth.FastLanguageModel.from_pretrained.assert_called_once_with(
        model_name="mock/path",
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )

def test_build_prompt(mock_llama_service):
    """Test the build_prompt method."""
    instruction = "Extract cookies"
    content = "This is a cookie policy."
    expected_prompt = alpaca_prompt.format(instruction, content)
    assert mock_llama_service.build_prompt(instruction, content) == expected_prompt

def test_generate_response_valid_json(mock_llama_service):
    """Test generate_response with valid JSON output."""
    mock_output_text = "### Response:\n```json\n{\"is_specific\": 1, \"cookies\": [{\"cookie_name\": \"_ga\"}]}\n```"
    mock_llama_service.tokenizer.decode.return_value = mock_output_text
    mock_llama_service.model.generate.return_value = [MagicMock()] # Mock the output of generate

    result = mock_llama_service.generate_response("Some content")
    expected_json = "{\"is_specific\": 1, \"cookies\": [{\"cookie_name\": \"_ga\"}]}"
    assert result == expected_json
    assert json.loads(result) == {"is_specific": 1, "cookies": [{"cookie_name": "_ga"}]}

def test_generate_response_invalid_json(mock_llama_service):
    """Test generate_response with invalid JSON output."""
    mock_output_text = "### Response:\nThis is not a valid JSON string."
    mock_llama_service.tokenizer.decode.return_value = mock_output_text
    mock_llama_service.model.generate.return_value = [MagicMock()]

    result = mock_llama_service.generate_response("Some content")
    assert result == "This is not a valid JSON string."

def test_generate_response_no_cookies(mock_llama_service):
    """Test generate_response when no cookies are found (is_specific=0)."""
    mock_output_text = "### Response:\n{\"is_specific\": 0, \"cookies\": []}"
    mock_llama_service.tokenizer.decode.return_value = mock_output_text
    mock_llama_service.model.generate.return_value = [MagicMock()]

    result = mock_llama_service.generate_response("Some content")
    expected_json = "{\"is_specific\": 0, \"cookies\": []}"
    assert result == expected_json
    assert json.loads(result) == {"is_specific": 0, "cookies": []}

def test_generate_response_multiple_cookies(mock_llama_service):
    """Test generate_response with multiple cookies."""
    mock_output_text = """### Response:
{
  "is_specific": 1,
  "cookies": [
    {
      "cookie_name": "_ga",
      "declared_purpose": "Analytical",
      "declared_retention": "2 years",
      "declared_third_parties": ["Google"],
      "declared_description": "Used by Google Analytics to distinguish users."
    },
    {
      "cookie_name": "_gid",
      "declared_purpose": "Analytical",
      "declared_retention": "24 hours",
      "declared_third_parties": ["Google"],
      "declared_description": "Used by Google Analytics to distinguish users."
    }
  ]
}"""
    mock_llama_service.tokenizer.decode.return_value = mock_output_text
    mock_llama_service.model.generate.return_value = [MagicMock()]

    result = mock_llama_service.generate_response("Some content")
    expected_json_dict = {
      "is_specific": 1,
      "cookies": [
        {
          "cookie_name": "_ga",
          "declared_purpose": "Analytical",
          "declared_retention": "2 years",
          "declared_third_parties": ["Google"],
          "declared_description": "Used by Google Analytics to distinguish users."
        },
        {
          "cookie_name": "_gid",
          "declared_purpose": "Analytical",
          "declared_retention": "24 hours",
          "declared_third_parties": ["Google"],
          "declared_description": "Used by Google Analytics to distinguish users."
        }
      ]
    }
    assert json.loads(result) == expected_json_dict

def test_generate_response_json_with_code_block(mock_llama_service):
    """Test generate_response when JSON is wrapped in a code block."""
    mock_output_text = "### Response:\n```json\n{\"is_specific\": 1, \"cookies\": [{\"cookie_name\": \"test_cookie\"}]}\n```"
    mock_llama_service.tokenizer.decode.return_value = mock_output_text
    mock_llama_service.model.generate.return_value = [MagicMock()]

    result = mock_llama_service.generate_response("Some content")
    expected_json = "{\"is_specific\": 1, \"cookies\": [{\"cookie_name\": \"test_cookie\"}]}"
    assert result == expected_json
    assert json.loads(result) == {"is_specific": 1, "cookies": [{"cookie_name": "test_cookie"}]}
