# src/aurora_platform/models/phi3_handler.py

"""
Handles the loading of the Phi-3 model and provides a function for text generation.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
# Try to use GPU if available, otherwise CPU.
# MPS (Apple Silicon) can have issues with some Hugging Face models or operations,
# so we'll prefer CUDA, then CPU, and explicitly avoid MPS for now to ensure broader compatibility.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Global variables to hold the model and tokenizer
# This is a simple way to cache them in memory.
# For a production system, consider a more robust caching or model management strategy.
model = None
tokenizer = None
pipe = None

def load_model():
    """
    Loads the Phi-3 model and tokenizer.
    This function will be called once when the application starts
    or when the first request is made.
    """
    global model, tokenizer, pipe

    if model is None or tokenizer is None:
        print(f"Loading model {MODEL_ID} on device {DEVICE}...")
        # Trust remote code if you are sure about the source, Phi-3 requires it.
        model_kwargs = {"trust_remote_code": True}
        if DEVICE == "cuda": # Specific optimizations for CUDA
            model_kwargs["torch_dtype"] = "auto" # Or torch.bfloat16 for mixed precision if supported
            # model_kwargs["flash_attn"] = True # If flash attention is available and desired
            # model_kwargs["flash_rotary"] = True # If flash rotary is available and desired

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            **model_kwargs
        ).to(DEVICE)

        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

        # Set pad_token_id to eos_token_id if it's not set
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=DEVICE,
        )
        print(f"Model {MODEL_ID} loaded successfully on {DEVICE}.")

def generate_text(prompt: str, max_new_tokens: int = 250) -> str:
    """
    Generates text using the loaded Phi-3 model.

    Args:
        prompt (str): The input prompt for the model.
        max_new_tokens (int): The maximum number of new tokens to generate.

    Returns:
        str: The generated text.
    """
    if pipe is None:
        load_model() # Ensure model is loaded

    # Construct the input messages for the chat template
    messages = [
        {"role": "user", "content": prompt},
    ]

    # Apply the chat template
    # Note: Phi-3's recommended template might require specific handling.
    # For simplicity, we'll use the tokenizer's default apply_chat_template
    # if it's available and configured for instruction-following.
    # If not, a more manual construction of the prompt string might be needed.
    # For Phi-3 instruct models, the prompt format is usually:
    # <|user|>
    # {prompt}<|end|>
    # <|assistant|>
    # The pipeline should ideally handle this.

    generation_args = {
        "max_new_tokens": max_new_tokens,
        "return_full_text": False, # Return only the generated text
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
    }

    try:
        print(f"Generating text for prompt: '{prompt[:100]}...'")
        # The pipeline for text-generation typically expects a string or list of strings.
        # If using `apply_chat_template` directly, the output should be passed to `model.generate`.
        # Here, we pass the messages array directly to the pipeline, which should handle it.
        output = pipe(messages, **generation_args)

        generated_text = output[0]['generated_text']

        # Some models might include the prompt in the output or add special tokens.
        # This step might need adjustment based on observed model output.
        # If `return_full_text=False` works as expected, this cleanup might not be needed.
        # If the model's output is a list of dicts with 'generated_text', extract it.
        # Example: [{'generated_text': '...response...'}]

        # The Phi-3 instruct template typically ends with <|assistant|>
        # The response follows that. If special tokens like <|end|> appear, they might need to be stripped.
        # For now, we assume the pipeline handles this well.
        if isinstance(generated_text, str) and "<|end|>" in generated_text:
            generated_text = generated_text.split("<|end|>")[0].strip()

        print(f"Generated text: '{generated_text[:100]}...'")
        return generated_text
    except Exception as e:
        print(f"Error during text generation: {e}")
        # Fallback for older transformers versions or if messages format is not directly supported by pipe
        try:
            print("Retrying with formatted prompt string...")
            # Manual prompt formatting based on typical Phi-3 instruct style
            formatted_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>"
            output = pipe(formatted_prompt, **generation_args)
            generated_text = output[0]['generated_text']
            if isinstance(generated_text, str) and "<|end|>" in generated_text:
                 generated_text = generated_text.split("<|end|>")[0].strip()
            print(f"Generated text (fallback): '{generated_text[:100]}...'")
            return generated_text
        except Exception as e_fallback:
            print(f"Error during text generation (fallback attempt): {e_fallback}")
            raise e_fallback

# Example usage (optional, for testing this module directly)
if __name__ == "__main__":
    print("Performing a test run of phi3_handler...")
    load_model() # Explicitly load
    test_prompt = "Explique o que é um Large Language Model em português."
    print(f"\nTest prompt: {test_prompt}")
    response = generate_text(test_prompt)
    print(f"\nModel response:\n{response}")

    test_prompt_2 = "Write a short story about a robot learning to paint."
    print(f"\nTest prompt 2: {test_prompt_2}")
    response_2 = generate_text(test_prompt_2, max_new_tokens=100)
    print(f"\nModel response 2:\n{response_2}")

    # Test with a slightly different type of prompt
    messages_test = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What are the main challenges in training SLMs?"}
    ]
    # The current generate_text expects a single string prompt.
    # To use the messages format directly with the pipeline:
    if pipe:
        print(f"\nTest prompt 3 (messages format): {messages_test}")
        output = pipe(messages_test, max_new_tokens=150, return_full_text=False, do_sample=True, temperature=0.7, top_p=0.9)
        print(f"\nModel response 3:\n{output[0]['generated_text']}")
    else:
        print("Pipeline not initialized, skipping messages format test.")

    print("\nPhi3_handler test run completed.")
