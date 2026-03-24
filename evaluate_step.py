# evaluate_step.py
import json
import os
from typing import Any, Dict, List, Optional
import sys
import random
import requests
import time
import logging
import argparse

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Good starter choices:
# - "openrouter/free" for cheapest experimentation
# - a specific model later once your pipeline works
DEFAULT_MODEL = "openrouter/free"
#DEFAULT_MODEL = "gpt-4o-mini"

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s [%(threadName)s - %(name)s] %(message)s")


def send_openrouter_messages(  
    messages: list[dict[str, Any]],
    model: str = DEFAULT_MODEL,
    timeout: int = 60,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> dict[str, Any]:
    logger.debug("Sending messages to OpenRouter: %s", json.dumps(messages, indent=2))
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
    delay = base_delay
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.debug("Attempt %d failed with error: %s", attempt + 1, e)
            if attempt == max_retries - 1:
                raise
            sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
    raise RuntimeError("send_openrouter_messages failed unexpectedly")

def get_message_text(response: dict[str, Any]) -> str:
    text = response["choices"][0]["message"]["content"]
    logger.debug("Model response text: %s", text)
    return text

def get_model(response: dict[str, Any]) -> str:
    model = response["model"]
    logger.debug("Model used: %s", model)
    return model

def get_reasoning_snippet(response: dict[str, Any]) -> str:
    reasoning = response["choices"][0]["message"]["reasoning"]
    logger.debug("Model reasoning snippet: %s", reasoning)
    return reasoning

def key_info():
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.get(
        "https://openrouter.ai/api/v1/key",headers=headers,timeout=30)
    print("STATUS:", resp.status_code)
    print("RAW RESPONSE:",json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command",nargs="?", choices=["test", "key-info"], default="test")
    parser.add_argument("log_level", nargs="?", choices=["debug", "info", "warning", "error"], default="info")
    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper(), None))
    if args.command == "key-info":
        key_info()

    if args.command == "test":
        messages = [
            {"role": "system", "content": "You are a pirate."},
            {"role": "user", "content": "Say hello in five words."},
        ]

        data = send_openrouter_messages(messages)
        print("Model:", get_model(data))
        print("\nMODEL SAID:")
        print(get_message_text(data))
        logger.debug(json.dumps(data, indent=2))
