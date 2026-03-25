
from evaluate_step import send_openrouter_messages, get_message_text, get_reasoning_snippet, get_model
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import argparse
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s [%(threadName)s - %(name)s] %(message)s")

def extract_score(text):
    match = re.search(r"<score>\s*(\d+(?:\.\d+)?)\s*</score>", text, re.IGNORECASE)
    if not match:
        raise ValueError("Score not found in the text.")
    score = float(match.group(1))
    logger.debug("Extracted score: %s", score)
    return int(score) if score.is_integer() else score

def extract_scratchpad(text):
    match = re.search(
    r"<scratchpad>\s*(.*?)\s*</scratchpad>",
    text,
    re.IGNORECASE | re.DOTALL,)
    return match.group(1).strip() if match else ""

def extract_reasoning(text):
    match = re.search(
    r"<reasoning>\s*(.*?)\s*</reasoning>",
    text,
    re.IGNORECASE | re.DOTALL,)
    return match.group(1).strip() if match else ""

def load_prompt(prompt_name):
    path = Path("prompts") / prompt_name
    return path.read_text(encoding="utf-8")
    
def render_prompt(template, **kwargs):
    prompt = template.format(**kwargs)
    logger.debug("Rendered prompt: %s", prompt)
    return prompt

class Monitor:
    def __init__(self, task_description,prompt_name="default_monitor.txt"):
        self.task_description = task_description
        self.actions = []
        self.last_score = 0
        self.max_score = 0
        self.reasoning = ""
        self.template = load_prompt(prompt_name)
    def observe(self,actions):
        self.actions.append(actions)
    def get_message(self):
        return [{"role":"system","content": render_prompt(self.template, **self.get_prompt_kwargs())}]
    def handle_response_text(self,text):
        Error = None
        try:
            score = extract_score(text)
        except ValueError as e: 
            Error = f"Error extracting score: {e}"           
            score = -1
        self.last_score = score
        self.max_score = max(self.max_score, score)
        self.reasoning = extract_reasoning(text)
        return Error
    def get_prompt_kwargs(self):
        return {"task_description": self.task_description, "actions": self.actions}
    
    def evaluate_step(self):
        messages = self.get_message()
        data = send_openrouter_messages(messages)
        Error = self.handle_response_text(get_message_text(data))
        if Error:
            logger.error("Error handling response text: %s", Error)
            logger.info("Message sent to model: %s", json.dumps(messages, indent=2))
            logger.info("Model used: %s", get_model(data))
            logger.info("Response text: %s", get_message_text(data))
            logger.debug("Full response data: %s", json.dumps(data, indent=2))
        return self.last_score

class Scratchpad(Monitor):
    def __init__(self,task_description,prompt_name="scratchpad_monitor.txt"):
        super().__init__(task_description, prompt_name=prompt_name)
        self.scratchpad = ""
    def handle_response_text(self, text):
        super().handle_response_text(text)
        new_scratchpad = extract_scratchpad(text)
        logger.info("Scratchpad contents: %s", new_scratchpad)
        self.scratchpad = new_scratchpad
    def get_prompt_kwargs(self):
        kwargs = super().get_prompt_kwargs()
        kwargs["scratchpad"] = self.scratchpad
        return kwargs




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command",nargs="?", choices=["test", "run"], default="run")
    parser.add_argument("log_level", nargs="?", choices=["debug", "info", "warning", "error"], default="info")
    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper(), None))
    if args.command == "test":
        print("Test")
    elif args.command == "run":
        print("run")
            
