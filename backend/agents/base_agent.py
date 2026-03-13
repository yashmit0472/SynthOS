import requests

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

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]