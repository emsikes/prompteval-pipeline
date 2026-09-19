import os
from dotenv import load_dotenv

import litellm


load_dotenv(override=True)

litellm.api_key = os.getenv("ANTHROPIC_API_KEY")


def chat(messages, model, system=None, temperature=1.0, stop_sequences=None, max_tokens=1000):
    """Send messages to the LLM and return the response text."""

    params = {
        "model": model,
        "max_tokens": 1000, 
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    response = litellm.completion(**params)
    return response.choices[0].message.content


def add_user_message(messages, text):
    """Append a user turn to the messages list"""
    messages.append({"role": "user", "content": text})


def add_assistant_message(messages, text):
    """Append and assistant prefill turn to the messages list"""
    messages.append({"role": "assistant", "content": text})