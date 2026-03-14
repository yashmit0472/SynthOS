from backend.agents.strategist import strategist
from backend.agents.skeptic import skeptic
from backend.agents.risk_analyst import risk_analyst
from backend.agents.synthesizer import synthesizer
from backend.agents.router import router
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_query(user_input, context=""):
    # Step 1: Route intent
    logger.info(f"Routing query: {user_input[:50]}...")
    start_time = time.time()
    route_raw = router.run(user_input)
    route = json.loads(route_raw)
    logger.info(f"Routing complete in {time.time() - start_time:.2f}s. Route: {route}")

    query_type = route.get("query_type", "ANALYSIS")

    if query_type == "DECISION":
        return run_decision_engine(user_input, context)
    else:
        return run_analysis_engine(user_input, context)


def run_decision_engine(user_input, context=""):
    agents = [strategist, skeptic, risk_analyst]
    outputs = []

    logger.info(f"Running Decision Engine with {len(agents)} agents...")
    start_time = time.time()
    
    def run_agent(agent):
        logger.info(f"Starting {agent.role}...")
        raw = agent.run(user_input, context)
        parsed = json.loads(raw)
        logger.info(f"{agent.role} finished.")
        return parsed

    with ThreadPoolExecutor(max_workers=len(agents)) as executor:
        outputs = list(executor.map(run_agent, agents))

    logger.info(f"All agents finished in {time.time() - start_time:.2f}s")

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

    logger.info("Running Synthesis...")
    synth_start = time.time()
    synth_raw = synthesizer.run(synth_prompt)
    synth_parsed = json.loads(synth_raw)
    logger.info(f"Synthesis complete in {time.time() - synth_start:.2f}s")

    return {
        "mode": "DECISION",
        "final_answer": synth_parsed["final_answer"],
        "confidence_score": confidence,
        "agent_breakdown": outputs
    }


def run_analysis_engine(user_input, context=""):
    agents = [strategist, skeptic, risk_analyst]
    outputs = []

    logger.info(f"Running Analysis Engine with {len(agents)} agents...")
    start_time = time.time()
    
    def run_agent(agent):
        logger.info(f"Starting {agent.role}...")
        raw = agent.run(user_input, context)
        parsed = json.loads(raw)
        logger.info(f"{agent.role} finished.")
        return parsed

    with ThreadPoolExecutor(max_workers=len(agents)) as executor:
        outputs = list(executor.map(run_agent, agents))

    logger.info(f"All agents finished in {time.time() - start_time:.2f}s")

    combined_reasoning = "\n".join([o.get("reasoning", "") for o in outputs])

    synth_prompt = f"""
    User Question: {user_input}

    Perspectives:
    {combined_reasoning}
    """

    logger.info("Running Synthesis...")
    synth_start = time.time()
    synth_raw = synthesizer.run(synth_prompt)
    synth_parsed = json.loads(synth_raw)
    logger.info(f"Synthesis complete in {time.time() - synth_start:.2f}s")

    return {
        "mode": "ANALYSIS",
        "final_answer": synth_parsed["final_answer"],
        "perspectives": outputs
    }