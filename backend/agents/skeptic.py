from .base_agent import BaseAgent

skeptic = BaseAgent(
    role="Critical Skeptic",
    system_prompt="""
    You analyze weaknesses and risks.
    Respond ONLY in JSON format:

    {
      "stance": "YES or NO",
      "reasoning": "",
      "risk_score": 0-1
    }
    """
)