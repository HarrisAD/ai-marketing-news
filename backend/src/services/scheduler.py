import schedule
import time
import threading
import logging
from datetime import datetime
from services.crawler_service import CrawlerService
from services.config import settings

logger = logging.getLogger(__name__)

class NewsScheduler:
    """Simple scheduler for automated news updates"""
    
    def __init__(self):
        self.crawler_service = CrawlerService()
        self.is_running = False
        self.thread = None
        
    def start(self):
        """Start the scheduler in a background thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        logger.info(f"Starting news scheduler - updates at {settings.cron_time}")
        
        # Schedule daily updates
        schedule.every().day.at(settings.cron_time).do(self._run_update)
        
        # Start scheduler thread
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("News scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
            
        logger.info("Stopping news scheduler...")
        self.is_running = False
        schedule.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("News scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _run_update(self):
        """Run the news update process"""
        logger.info("🕒 Scheduled news update starting...")
        
        try:
            result = self.crawler_service.run_full_update()
            
            if result['success']:
                logger.info(f"✅ Scheduled update completed - saved {result['stories_saved']} new stories")
            else:
                logger.error(f"❌ Scheduled update failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Scheduled update failed with exception: {e}")
    
    def run_update_now(self):
        """Manually trigger an update (for API endpoints)"""
        logger.info("🚀 Manual update triggered")
        return self._run_update()

# Global scheduler instance
scheduler = NewsScheduler()