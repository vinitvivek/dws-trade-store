"""Scheduler for checking and marking expired trades."""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.trade_service import TradeService

logger = logging.getLogger(__name__)


class ExpiryScheduler:
    """Scheduler for automatic trade expiry checks."""
    
    def __init__(self, trade_service: TradeService, interval_minutes: int = 60):
        """Initialize expiry scheduler."""
        self.trade_service = trade_service
        self.interval_minutes = interval_minutes
        self.scheduler = BackgroundScheduler()
    
    def check_and_mark_expired(self):
        """Check and mark expired trades."""
        try:
            logger.info("Running expiry check...")
            count = self.trade_service.mark_expired_trades()
            logger.info(f"Expiry check completed. Marked {count} trades as expired.")
        except Exception as e:
            logger.error(f"Error during expiry check: {str(e)}")
            self.trade_service.mongodb_repo.log_event(
                event_type="EXPIRY_CHECK_ERROR",
                data={"error": str(e)},
                severity="error"
            )
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.add_job(
            func=self.check_and_mark_expired,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id='expiry_check_job',
            name='Check and mark expired trades',
            replace_existing=True
        )
        
        # Run once on startup
        self.check_and_mark_expired()
        
        self.scheduler.start()
        logger.info(f"Expiry scheduler started. Running every {self.interval_minutes} minutes.")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Expiry scheduler stopped.")
