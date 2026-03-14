import requests
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

class BaseAgent:
    def __init__(self, role, system_prompt):
        self.role = role
        self.system_prompt = system_prompt

    def run(self, user_input, context=""):
        prompt = f"""
        You are a {self.role}.
        {self.system_prompt}

        Context:
        {context}

        User Input:
        {user_input}

        Respond ONLY in JSON.
        """

        logger.info(f"[{self.role}] Sending request to Ollama...")
        start_time = time.time()
        
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120 # Add a timeout so it doesn't hang forever
            )
            response.raise_for_status()
            logger.info(f"[{self.role}] Received response from Ollama in {time.time() - start_time:.2f}s")
            return response.json()["response"]
        except Exception as e:
            logger.error(f"[{self.role}] Error calling Ollama: {str(e)}")
            return '{"error": "Failed to generate response"}'