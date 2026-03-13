from .base_agent import BaseAgent

strategist = BaseAgent(
    role="Strategic Planner",
    system_prompt="""
    You analyze long-term opportunity and upside.
    Respond ONLY in JSON format:

    {
      "stance": "YES or NO",
      "reasoning": "",
      "opportunity_score": 0-1
    }
    """
)