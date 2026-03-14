import psutil
import logging

logger = logging.getLogger(__name__)

def get_system_metrics():
    """Returns basic system metrics like CPU and RAM usage."""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()

    metrics = {
        "cpu_percent": cpu_percent,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2)
    }
    return metrics

def get_top_processes(n=5, sort_by="memory"):
    """Returns the top N processes by memory or cpu usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            info = proc.info
            # Filter out idle/system processes if needed
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if sort_by == "memory":
        processes = sorted(processes, key=lambda p: (p['memory_percent'] or 0), reverse=True)
    else:
        processes = sorted(processes, key=lambda p: (p['cpu_percent'] or 0), reverse=True)

    top_procs = processes[:n]
    
    # Format nicely
    formatted = []
    for p in top_procs:
        formatted.append({
            "name": p['name'],
            "pid": p['pid'],
            "memory_percent": round(p['memory_percent'] or 0, 2),
            "cpu_percent": round(p['cpu_percent'] or 0, 2)
        })
        
    return formatted

def analyze_system_health():
    """Provides an insight string if system is under load."""
    metrics = get_system_metrics()
    
    if metrics["ram_percent"] > 85 or metrics["cpu_percent"] > 80:
        top_procs = get_top_processes(n=3, sort_by="memory" if metrics["ram_percent"] > 85 else "cpu")
        proc_names = [p['name'] for p in top_procs]
        
        issue = "RAM" if metrics["ram_percent"] > 85 else "CPU"
        value = metrics["ram_percent"] if issue == "RAM" else metrics["cpu_percent"]
        
        insight = f"{issue} usage is high ({value}%). Top consumers: {', '.join(proc_names)}."
        return insight
        
    return None
