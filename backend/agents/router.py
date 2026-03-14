from .base_agent import BaseAgent

router = BaseAgent(
    role="Intent Router",
    system_prompt="""
    Classify the user's input into ONE of the following types:

    - DECISION → if the user is asking whether they should do something
    - ANALYSIS → if the user is asking for explanation, philosophy, exploration, or general reasoning
    - FILE_SEARCH → if the user is asking to find notes, documents, or files they have written
    - SYSTEM_INSIGHT → if the user wants to know about computer performance, battery, RAM, CPU, or files recently edited

    Respond ONLY in JSON:

    {
      "query_type": "DECISION or ANALYSIS or FILE_SEARCH or SYSTEM_INSIGHT"
    }
    """
)