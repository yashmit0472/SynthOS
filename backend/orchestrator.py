from agents.strategist import strategist
from agents.skeptic import skeptic
from agents.risk_analyst import risk_analyst
from agents.synthesizer import synthesizer
from agents.router import router
import json


def handle_query(user_input, context=""):
    # Step 1: Route intent
    route_raw = router.run(user_input)
    route = json.loads(route_raw)

    query_type = route.get("query_type", "ANALYSIS")

    if query_type == "DECISION":
        return run_decision_engine(user_input, context)
    else:
        return run_analysis_engine(user_input, context)


def run_decision_engine(user_input, context=""):
    agents = [strategist, skeptic, risk_analyst]
    outputs = []

    for agent in agents:
        raw = agent.run(user_input, context)
        parsed = json.loads(raw)
        outputs.append(parsed)

    yes_votes = sum(1 for o in outputs if o.get("stance") == "YES")
    decision = "YES" if yes_votes >= 2 else "NO"

    decision_strength = []

    for o in outputs:
        if decision == "YES":
            if "opportunity_score" in o:
                decision_strength.append(o["opportunity_score"])
            elif "risk_score" in o:
                decision_strength.append(1 - o["risk_score"])
            else:
                decision_strength.append(0.5)
        else:
            if "risk_score" in o:
                decision_strength.append(o["risk_score"])
            elif "opportunity_score" in o:
                decision_strength.append(1 - o["opportunity_score"])
            else:
                decision_strength.append(0.5)

    confidence = round(sum(decision_strength) / len(decision_strength), 2)

    # 🔥 Synthesis Step
    combined_reasoning = "\n".join([o.get("reasoning", "") for o in outputs])

    synth_prompt = f"""
    User Question: {user_input}

    Agent Insights:
    {combined_reasoning}

    Final Decision: {decision}
    """

    synth_raw = synthesizer.run(synth_prompt)
    synth_parsed = json.loads(synth_raw)

    return {
        "mode": "DECISION",
        "final_answer": synth_parsed["final_answer"],
        "confidence_score": confidence,
        "agent_breakdown": outputs
    }


def run_analysis_engine(user_input, context=""):
    agents = [strategist, skeptic, risk_analyst]
    outputs = []

    for agent in agents:
        raw = agent.run(user_input, context)
        parsed = json.loads(raw)
        outputs.append(parsed)

    combined_reasoning = "\n".join([o.get("reasoning", "") for o in outputs])

    synth_prompt = f"""
    User Question: {user_input}

    Perspectives:
    {combined_reasoning}
    """

    synth_raw = synthesizer.run(synth_prompt)
    synth_parsed = json.loads(synth_raw)

    return {
        "mode": "ANALYSIS",
        "final_answer": synth_parsed["final_answer"],
        "perspectives": outputs
    }