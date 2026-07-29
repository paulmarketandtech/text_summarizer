from pathlib import Path
import yaml
from ollama import Client  # pyright: ignore

client = Client(host="http://192.168.0.164:11434")
models = {"llama": "llama3.2:3b", "qwen3": "qwen3.5:9b", "qwen2": "qwen2.5:7b"}


class PromptManager:
    def __init__(self, prompts_file: str = "./prompts.yaml"):
        self.prompts_file = Path(prompts_file)
        self.prompts = self._load_prompts()
        self.cache = {}

    def _load_prompts(self) -> dict:
        """Load prompts from YAML file"""
        with open(self.prompts_file, "r") as f:
            prompts = yaml.safe_load(f)
        # logger.info(f"Loaded prompts from {self.prompts_file}")
        return prompts

    def get_prompt(self, category: str) -> dict:
        # Fallback to 'stock_analysis' if category doesn't exist
        category_prompts = self.prompts.get(
            category, self.prompts.get("stock_analysis", {})
        )
        system_prompt = category_prompts["instruction"]
        task_prompt = category_prompts["task"]

        return {"system": system_prompt, "task": task_prompt}


manager = PromptManager("./prompts.yaml")

# You can easily swap 'executive_brief' to 'dense_synthesis' to experiment
prompt = manager.get_prompt(category="stock_analysis", transcript=chunk_text)
