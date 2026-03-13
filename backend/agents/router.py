from .base_agent import BaseAgent

router = BaseAgent(
    role="Intent Router",
    system_prompt="""
    Classify the user's input into ONE of the following types:

    - DECISION → if the user is asking whether they should do something
    - ANALYSIS → if the user is asking for explanation, philosophy, exploration, or general reasoning

    Respond ONLY in JSON:

    {
      "query_type": "DECISION or ANALYSIS"
    }
    """
)