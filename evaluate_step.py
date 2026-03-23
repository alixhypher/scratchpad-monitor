# evaluate_step.py
import json
import os
from typing import Any, Dict, List, Optional

import requests


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Good starter choices:
# - "openrouter/free" for cheapest experimentation
# - a specific model later once your pipeline works
DEFAULT_MODEL = "openrouter/free"

def test_openrouter_connection(model: str = DEFAULT_MODEL) -> dict:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a pirate."},
            {"role": "user", "content": "Say hello in five words."}
        ],
    }

    resp = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    print("STATUS:", resp.status_code)
    print("RAW RESPONSE:")
    print(resp.text)

    resp.raise_for_status()
    return resp.json()

def send_openrouter_messages(
    messages: list[dict[str, Any]],
    model: str = DEFAULT_MODEL,
    timeout: int = 60,
) -> dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    resp = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=timeout,
    )

    #print("STATUS:", resp.status_code)
    #print("RAW RESPONSE:")
    #print(resp.text)

    resp.raise_for_status()
    return resp.json()

def get_message_text(response: dict[str, Any]) -> str:
    return response["choices"][0]["message"]["content"]

def get_reasoning_snippet(response: dict[str, Any]) -> str:
    return response["choices"][0]["message"]["reasoning"]

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a pirate."},
        {"role": "user", "content": "Say hello in five words."},
    ]

    data = send_openrouter_messages(messages)

    print("\nMODEL SAID:")
    print(get_message_text(data))
