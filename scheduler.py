#!/usr/bin/env python3
"""
Scheduler for Web3 Data Aggregator
Runs the aggregation process on a configurable schedule
"""
import asyncio
import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import app
from src.utils.logger import logger
from src.config import config

class AggregatorScheduler:
    """Scheduler for running the Web3 Data Aggregator"""
    
    def __init__(self):
        self.is_running = False
        self.last_run_time = None
        self.last_run_result = None
    
    async def run_scheduled_aggregation(self):
        """Run the aggregation process (called by scheduler)"""
        if self.is_running:
            logger.warning("Aggregation already running, skipping this scheduled run")
            return
        
        self.is_running = True
        self.last_run_time = datetime.now()
        
        try:
            logger.info("🕐 Scheduled aggregation starting", 
                       time=self.last_run_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            result = await app.run_full_aggregation()
            self.last_run_result = result
            
            if result['success']:
                logger.success("✅ Scheduled aggregation completed successfully",
                             new_projects=result['new_projects'],
                             duration=result['duration'])
            else:
                logger.error("❌ Scheduled aggregation failed",
                           error=result['error'])
        
        except Exception as e:
            logger.error("💥 Scheduled aggregation crashed", error=e)
            self.last_run_result = {'success': False, 'error': str(e)}
        
        finally:
            self.is_running = False
    
    def setup_schedule(self):
        """Set up the schedule based on configuration"""
        schedule_type = config.run_schedule.lower()
        
        if schedule_type == 'daily':
            # Run daily at 9:00 AM
            schedule.every().day.at("09:00").do(self._run_async_job)
            logger.info("📅 Scheduled daily runs at 9:00 AM")
            
        elif schedule_type == 'weekly':
            # Run weekly on Monday at 9:00 AM
            schedule.every().monday.at("09:00").do(self._run_async_job)
            logger.info("📅 Scheduled weekly runs on Monday at 9:00 AM")
            
        else:
            logger.error("❌ Invalid schedule type", schedule=schedule_type)
            raise ValueError(f"Invalid schedule type: {schedule_type}")
    
    def _run_async_job(self):
        """Wrapper to run async function in scheduler"""
        asyncio.run(self.run_scheduled_aggregation())
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("🚀 Starting Web3 Data Aggregator Scheduler")
        logger.info(f"Storage: {config.storage_type}")
        logger.info(f"Schedule: {config.run_schedule}")
        
        try:
            # Set up the schedule
            self.setup_schedule()
            
            # Show next run time
            next_run = schedule.next_run()
            if next_run:
                logger.info(f"Next scheduled run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n" + "=" * 60)
            print("🤖 Web3 Data Aggregator Scheduler is now running...")
            print("📅 Schedule:", config.run_schedule)
            print("💾 Storage:", config.storage_type)
            if next_run:
                print("Next run:", next_run.strftime('%Y-%m-%d %H:%M:%S'))
            print("🛑 Press Ctrl+C to stop")
            print("=" * 60)
            
            # Run scheduler loop
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            print("\n🛑 Scheduler stopped")
        except Exception as e:
            logger.error("💥 Scheduler crashed", error=e)
            print(f"\n💥 Scheduler error: {e}")
            raise
    
    def run_once_now(self):
        """Run the aggregation once immediately"""
        logger.info("🚀 Running aggregation immediately")
        asyncio.run(self.run_scheduled_aggregation())
    
    def get_status(self):
        """Get scheduler status"""
        status = {
            'is_running': self.is_running,
            'schedule_type': config.run_schedule,
            'storage_type': config.storage_type,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'last_run_result': self.last_run_result,
            'next_run': schedule.next_run().isoformat() if schedule.next_run() else None
        }
        return status

def main():
    """Main scheduler function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Web3 Data Aggregator Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scheduler.py start         # Start the scheduler
  python scheduler.py run-now       # Run aggregation once immediately
  python scheduler.py status        # Show scheduler status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'run-now', 'status'],
        help='Scheduler command to execute'
    )
    
    args = parser.parse_args()
    
    scheduler = AggregatorScheduler()
    
    try:
        if args.command == 'start':
            scheduler.run_scheduler()
        elif args.command == 'run-now':
            scheduler.run_once_now()
        elif args.command == 'status':
            status = scheduler.get_status()
            print("\nScheduler Status:")
            print(f"   Running: {status['is_running']}")
            print(f"   Schedule: {status['schedule_type']}")
            print(f"   Storage: {status['storage_type']}")
            print(f"   Last Run: {status['last_run_time'] or 'Never'}")
            print(f"   Next Run: {status['next_run'] or 'Not scheduled'}")
            if status['last_run_result']:
                result = status['last_run_result']
                print(f"   Last Result: {'✅ Success' if result['success'] else '❌ Failed'}")
                if result['success']:
                    print(f"   New Projects: {result.get('new_projects', 0)}")
        
    except Exception as e:
        logger.error("Scheduler error", error=e)
        print(f"💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

