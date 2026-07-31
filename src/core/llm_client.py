class OllamaClient:
    def __init__(self) -> None:
        self.host = "http://192.168.0.164:11434"

    def generate(
        self,
        user_prompt: str,
        system_prompt: str = None,
        model: str = "qwen2.5:7b",
        temperature: float = 0.2,
        top_p: float = 0.9,
        top_k: int = 40,
        json_mode: bool = False,
    ) -> str:
        """
        Temperature guide:
        - 0.0: Always same output (deterministic)
        - 0.2: Very consistent (good for tasks)
        - 0.5: Balanced
        - 1.0: Very creative/random

        For summarization: use 0.1-0.3
        For entity extraction: use 0.1
        For classification: use 0.1
        """

        import requests

        payload = {
            "model": model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": 1000,
            },
        }
        if json_mode:
            payload["format"] = "json"

        response = requests.post(f"{self.host}/api/generate", json=payload)
        response.raise_for_status()

        return response.json()
