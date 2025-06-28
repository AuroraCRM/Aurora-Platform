import pytest
from aurora_platform.models.phi3_handler import Phi3Handler

# Mock settings for testing
class MockSettings:
    def get(self, key, default=None):
        if key == "PHI3_MODEL_NAME":
            return "mock/phi3-model"
        if key == "PHI3_TRUST_REMOTE_CODE":
            return False
        return default

# Mock the actual model and tokenizer loading
def mock_from_pretrained(*args, **kwargs):
    class MockObject:
        def __init__(self):
            self.device = "cpu"
        def generate(self, *args, **kwargs):
            return torch.tensor([[1, 2, 3, 4, 5]]) # Dummy output
    return MockObject()

def mock_apply_chat_template(*args, **kwargs):
    return torch.tensor([1, 2, 3]) # Dummy token_ids

def mock_decode(*args, **kwargs):
    return "Mocked response"

# Use monkeypatch to replace the actual imports during testing
def test_phi3_handler_initialization(monkeypatch):
    monkeypatch.setattr("aurora_platform.models.phi3_handler.AutoTokenizer.from_pretrained", mock_from_pretrained)
    monkeypatch.setattr("aurora_platform.models.phi3_handler.AutoModelForCausalLM.from_pretrained", mock_from_pretrained)
    monkeypatch.setattr("aurora_platform.models.phi3_handler.settings", MockSettings())

    handler = Phi3Handler()
    assert handler.model_name == "mock/phi3-model"
    assert handler.trust_remote_code == False

def test_phi3_handler_generate_response(monkeypatch):
    monkeypatch.setattr("aurora_platform.models.phi3_handler.AutoTokenizer.from_pretrained", mock_from_pretrained)
    monkeypatch.setattr("aurora_platform.models.phi3_handler.AutoModelForCausalLM.from_pretrained", mock_from_pretrained)
    monkeypatch.setattr("aurora_platform.models.phi3_handler.settings", MockSettings())

    # Mock the methods called within generate_response
    mock_tokenizer_instance = mock_from_pretrained()
    monkeypatch.setattr(mock_tokenizer_instance, "apply_chat_template", mock_apply_chat_template)
    monkeypatch.setattr(mock_tokenizer_instance, "decode", mock_decode)
    monkeypatch.setattr("aurora_platform.models.phi3_handler.AutoTokenizer.from_pretrained", lambda *args, **kwargs: mock_tokenizer_instance)

    handler = Phi3Handler()
    response = handler.generate_response("test prompt")
    assert response == "Mocked response"