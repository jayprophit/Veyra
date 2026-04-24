"""Task Scheduler - Background job scheduling and automation.

Features:
- Cron-like scheduling for tasks
- Automatic data updates
- Report generation
- Maintenance jobs
- Health check scheduling
"""

import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger('TaskScheduler')

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ScheduledTask:
    """Definition of a scheduled task."""
    name: str
    function: Callable
    schedule: str  # cron-like: "daily@02:00", "hourly", "every_15_min"
    priority: TaskPriority
    enabled: bool = True
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class TaskScheduler:
    """Central task scheduler for Financial Master."""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def register_task(self, task: ScheduledTask):
        """Register a new scheduled task."""
        with self._lock:
            self.tasks[task.name] = task
            self._setup_schedule(task)
        logger.info(f"Registered task: {task.name}")
    
    def _setup_schedule(self, task: ScheduledTask):
        """Setup schedule based on task definition."""
        if not task.enabled:
            return
        
        schedule.clear(task.name)
        
        if task.schedule == "hourly":
            schedule.every().hour.do(self._run_task, task).tag(task.name)
        elif task.schedule == "daily":
            schedule.every().day.at("02:00").do(self._run_task, task).tag(task.name)
        elif task.schedule.startswith("daily@"):
            time_str = task.schedule.split("@")[1]
            schedule.every().day.at(time_str).do(self._run_task, task).tag(task.name)
        elif task.schedule == "weekly":
            schedule.every().sunday.at("03:00").do(self._run_task, task).tag(task.name)
        elif task.schedule.startswith("every_"):
            minutes = int(task.schedule.split("_")[1].replace("_min", ""))
            schedule.every(minutes).minutes.do(self._run_task, task).tag(task.name)
    
    def _run_task(self, task: ScheduledTask):
        """Execute a task with error handling."""
        logger.info(f"Running task: {task.name}")
        task.last_run = datetime.now()
        
        try:
            if asyncio.iscoroutinefunction(task.function):
                asyncio.run(task.function())
            else:
                task.function()
            
            task.last_status = "success"
            task.retry_count = 0
            logger.info(f"Task {task.name} completed successfully")
            
        except Exception as e:
            task.last_status = f"error: {str(e)}"
            logger.error(f"Task {task.name} failed: {e}")
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"Retrying task {task.name} (attempt {task.retry_count})")
                time.sleep(5)
                self._run_task(task)
    
    def start(self):
        """Start the scheduler in background thread."""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Task scheduler started")
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        logger.info("Task scheduler stopped")
    
    def get_status(self) -> Dict:
        """Get scheduler status."""
        return {
            "running": self.running,
            "tasks": [
                {
                    "name": t.name,
                    "schedule": t.schedule,
                    "enabled": t.enabled,
                    "last_run": t.last_run.isoformat() if t.last_run else None,
                    "last_status": t.last_status
                }
                for t in self.tasks.values()
            ]
        }
    
    def run_task_now(self, task_name: str):
        """Manually trigger a task."""
        if task_name in self.tasks:
            self._run_task(self.tasks[task_name])
        else:
            logger.error(f"Task not found: {task_name}")
    
    def enable_task(self, task_name: str):
        """Enable a task."""
        if task_name in self.tasks:
            self.tasks[task_name].enabled = True
            self._setup_schedule(self.tasks[task_name])
    
    def disable_task(self, task_name: str):
        """Disable a task."""
        if task_name in self.tasks:
            self.tasks[task_name].enabled = False
            schedule.clear(task_name)

# Pre-defined tasks for Financial Master

async def update_market_data():
    """Update market prices from Yahoo Finance."""
    from data_scraper import YahooFinanceScraper
    
    scraper = YahooFinanceScraper()
    await scraper.init(headless=True)
    
    # Update common tickers
    tickers = ["VUAG", "VUSA", "VUKG", "VAPX", "VJPN"]
    for ticker in tickers:
        try:
            quote = await scraper.get_quote(ticker)
            logger.info(f"Updated {ticker}: {quote}")
        except Exception as e:
            logger.error(f"Failed to update {ticker}: {e}")
        await asyncio.sleep(1)
    
    await scraper.close()

def generate_daily_report():
    """Generate daily portfolio report."""
    logger.info("Generating daily report...")
    
    # This would query database and generate report
    report_data = {
        "date": datetime.now().isoformat(),
        "portfolio_value": 0,  # Would fetch from DB
        "day_change": 0,
        "top_gainers": [],
        "top_losers": []
    }
    
    # Save report
    report_file = f"reports/daily_{datetime.now().strftime('%Y%m%d')}.json"
    import json
    import os
    os.makedirs("reports", exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    logger.info(f"Daily report saved: {report_file}")

def cleanup_old_logs():
    """Clean up log files older than 30 days."""
    import os
    from pathlib import Path
    
    log_dir = Path("./logs")
    if not log_dir.exists():
        return
    
    cutoff = datetime.now() - timedelta(days=30)
    removed = 0
    
    for log_file in log_dir.glob("*.log"):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
            log_file.unlink()
            removed += 1
    
    logger.info(f"Cleaned up {removed} old log files")

def check_system_health():
    """Run system health checks."""
    from logging_monitor import HealthChecker, get_logger_manager
    
    lm = get_logger_manager()
    hc = HealthChecker(lm)
    results = hc.run_all_checks()
    
    overall = hc.get_overall_status()
    logger.info(f"Health check complete: {overall}")
    
    if overall != "healthy":
        # Could send alert here
        logger.warning(f"System health issues detected: {results}")

def create_default_scheduler() -> TaskScheduler:
    """Create scheduler with default Financial Master tasks."""
    scheduler = TaskScheduler()
    
    # Market data update every 15 minutes during trading hours
    scheduler.register_task(ScheduledTask(
        name="market_data_update",
        function=update_market_data,
        schedule="every_15_min",
        priority=TaskPriority.HIGH
    ))
    
    # Daily report at market close
    scheduler.register_task(ScheduledTask(
        name="daily_report",
        function=generate_daily_report,
        schedule="daily@16:30",
        priority=TaskPriority.MEDIUM
    ))
    
    # Weekly log cleanup
    scheduler.register_task(ScheduledTask(
        name="cleanup_logs",
        function=cleanup_old_logs,
        schedule="weekly",
        priority=TaskPriority.LOW
    ))
    
    # Hourly health checks
    scheduler.register_task(ScheduledTask(
        name="health_check",
        function=check_system_health,
        schedule="hourly",
        priority=TaskPriority.HIGH
    ))
    
    return scheduler

if __name__ == "__main__":
    # Example usage
    scheduler = create_default_scheduler()
    scheduler.start()
    
    print("Scheduler running. Press Ctrl+C to stop.")
    print("Tasks:")
    for task in scheduler.tasks.values():
        print(f"  - {task.name}: {task.schedule}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nScheduler stopped.")
