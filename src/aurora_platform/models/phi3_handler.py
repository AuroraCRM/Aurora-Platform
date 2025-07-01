from transformers import AutoModelForCausalLM, AutoTokenizer
from aurora_platform.config import settings
import torch
from typing import Dict, Any, cast

class Phi3Handler:
    def __init__(self):
        self.model_name = str(cast(Dict[str, Any], settings).get("PHI3_MODEL_NAME", "microsoft/Phi-3-mini-4k-instruct"))
        self.trust_remote_code = bool(cast(Dict[str, Any], settings).get("PHI3_TRUST_REMOTE_CODE", False))
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=self.trust_remote_code)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, trust_remote_code=self.trust_remote_code, torch_dtype=torch.bfloat16, device_map="auto")

    def generate_response(self, prompt: str, max_new_tokens: int = 500) -> str:
        messages = [
            {"role": "user", "content": prompt},
        ]
        token_ids = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
        output = self.model.generate(token_ids.to(self.model.device), max_new_tokens=max_new_tokens)
        response = self.tokenizer.decode(output[0][token_ids.shape[0]:], skip_special_tokens=True)
        return response