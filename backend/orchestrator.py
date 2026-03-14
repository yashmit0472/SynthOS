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

from backend.system.process_monitor import analyze_system_health, get_top_processes
from backend.system.battery_monitor import analyze_battery_health
from backend.search.semantic_search import perform_semantic_search

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
    elif query_type == "FILE_SEARCH":
        return run_file_search(user_input)
    elif query_type == "SYSTEM_INSIGHT":
        return run_system_insight()
    else:
        return run_analysis_engine(user_input, context)

def run_file_search(user_input):
    logger.info("Running Semantic File Search...")
    results = perform_semantic_search(user_input)
    results["mode"] = "FILE_SEARCH"
    return results

def run_system_insight():
    logger.info("Running System Insight...")
    sys_health = analyze_system_health() or "System memory and CPU are within normal limits."
    batt_health = analyze_battery_health() or "Battery status looks good."
    
    # Can also fetch raw top processes for UI rendering
    top_proc = get_top_processes(3)
    
    return {
        "mode": "SYSTEM_INSIGHT",
        "final_answer": f"{sys_health}\n{batt_health}",
        "raw_processes": top_proc
    }


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