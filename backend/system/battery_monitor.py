import psutil
import logging

logger = logging.getLogger(__name__)

def get_battery_status():
    """Returns battery information using psutil."""
    if not hasattr(psutil, "sensors_battery"):
        return {"error": "Battery monitoring not supported on this device."}
        
    battery = psutil.sensors_battery()
    
    if battery is None:
        return {"error": "No battery detected."}
        
    metrics = {
        "percent": battery.percent,
        "power_plugged": battery.power_plugged,
        "time_left_mins": round(battery.secsleft / 60) if battery.secsleft > 0 and battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1
    }
    return metrics

def analyze_battery_health():
    """Returns an insight string if battery is low and discharging."""
    status = get_battery_status()
    
    if "error" in status:
        return None
        
    if not status["power_plugged"] and status["percent"] < 20:
        mins_left = status["time_left_mins"]
        time_str = f"approximately {mins_left} minutes" if mins_left > 0 else "a short time"
        
        insight = f"Battery is low ({status['percent']}%). It will last {time_str}. Enable power saver mode or plug in to charge."
        return insight
        
    return None
