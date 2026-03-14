from apscheduler.schedulers.background import BackgroundScheduler
import logging
from win10toast import ToastNotifier
import threading

from backend.system.process_monitor import analyze_system_health
from backend.system.battery_monitor import analyze_battery_health

logger = logging.getLogger(__name__)

# win10toast must run in a separate thread so it doesn't block the scheduler
def show_toast(title, msg):
    def toast_thread():
        try:
            toaster = ToastNotifier()
            toaster.show_toast(title, msg, duration=5, threaded=False)
        except Exception as e:
            logger.error(f"Failed to show toast notification: {e}")
    threading.Thread(target=toast_thread, daemon=True).start()

def check_system_metrics_job():
    logger.info("Running scheduled system metrics check...")
    
    # 1. Check RAM / CPU Load
    sys_insight = analyze_system_health()
    if sys_insight:
        logger.info(f"System insight triggered: {sys_insight}")
        show_toast("Nexis System Insight", sys_insight)

    # 2. Check Battery
    batt_insight = analyze_battery_health()
    if batt_insight:
        logger.info(f"Battery insight triggered: {batt_insight}")
        show_toast("Nexis Battery Alert", batt_insight)

def start_scheduler():
    logger.info("Starting Background Intelligence Scheduler...")
    scheduler = BackgroundScheduler()
    
    # Run every 5 minutes
    scheduler.add_job(check_system_metrics_job, 'interval', minutes=5)
    
    scheduler.start()
    return scheduler
