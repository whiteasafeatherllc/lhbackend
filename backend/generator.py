# backend/generator.py
from transformers import pipeline
import torch

try:
    generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-small",
        max_length=250,
        torch_dtype=torch.float32
    )
except Exception as e:
    print(f"⚠️ Model load failed: {e}")
    generator = None

def generate_message(service: str, tone: str, location: str, context: str) -> str:
    prompt = (
        f"Write a {tone.lower()}-tone outreach message for a {service} business in {location}, "
        f"responding to this need: '{context[:150]}...'. "
        "Be helpful, not salesy. Keep under 120 words."
    )
    if generator:
        try:
            output = generator(prompt, max_length=250, num_return_sequences=1)
            return output[0]["generated_text"].strip()
        except Exception as e:
            print(f"Generation error: {e}")
    # Fallback
    return (
        f"Hi, I saw you were looking for {service} in {location}. "
        "I specialize in helping businesses like yours. "
        "Would you be open to a quick chat about how I can support you?"
    )