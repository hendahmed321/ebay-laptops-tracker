"""
Automated eBay Laptops Scraper with Scheduling
Runs automatically at specified intervals
"""

import schedule
import time
import logging
from datetime import datetime
import sys
import os
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ebay_scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import scraper functions
from ebay_scraper import scrape_ebay_laptops, MongoDBHandler

def run_scraping_job():
    """Main job function to run the scraper"""
    logger.info("=" * 60)
    logger.info(f"Starting eBay scraping job at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Scrape data
        logger.info("Step 1: Scraping data from eBay...")
        products = scrape_ebay_laptops(pages_to_scrape=3)  
        
        if not products:
            logger.warning("No products found")
            return False
        
        logger.info(f"Step 1 Complete: Found {len(products)} products")
        
        # Step 2: Save to MongoDB
        logger.info("Step 2: Saving to MongoDB...")
        mongodb = MongoDBHandler()
        saved_count = mongodb.save_products_fresh(products, delete_old=True)
        
        if saved_count > 0:
            logger.info(f"Step 2 Complete: Saved {saved_count} products to MongoDB")
            
            # Step 3: Create backup
            logger.info("Step 3: Creating backup file...")
            backup_file = mongodb.save_backup_json(products)
            logger.info(f"Step 3 Complete: Backup created: {backup_file}")
            
            # Step 4: Show quick statistics
            logger.info("Step 4: Generating statistics...")
            if mongodb.collection is not None:
                # Get brand distribution
                brand_stats = list(mongodb.collection.aggregate([
                    {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]))
                
                logger.info("Brand Distribution:")
                for stat in brand_stats[:5]:  # Top 5 brands
                    brand = stat['_id'] or 'Unknown'
                    logger.info(f"  - {brand}: {stat['count']} products")
            
            return True
        else:
            logger.warning("No products saved to database")
            return False
            
    except Exception as e:
        logger.error(f"Error in scraping job: {e}")
        logger.error(traceback.format_exc())
        return False
    
    finally:
        logger.info(f"Job completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

def setup_schedule():
    """Configure the scheduling intervals"""
    
    # Schedule every 6 hours
    schedule.every(6).hours.do(run_scraping_job)
    logger.info("Scheduled: Every 6 hours")
    
    # Schedule at specific times
    schedule.every().day.at("08:00").do(run_scraping_job)  # 8:00 AM
    schedule.every().day.at("14:00").do(run_scraping_job)  # 2:00 PM
    schedule.every().day.at("20:00").do(run_scraping_job)  # 8:00 PM
    
    logger.info("Scheduled daily at: 08:00, 14:00, 20:00")
    
    # Show all scheduled jobs
    logger.info("Current schedule:")
    for job in schedule.get_jobs():
        logger.info(f"  - {job}")

def main():
    """Main function to start the scheduler"""
    logger.info("=" * 60)
    logger.info("eBay Laptops Scraper Scheduler")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Setup schedule
    setup_schedule()
    
    # Run immediately on startup
    logger.info("Running initial job...")
    run_scraping_job()
    
    # Keep checking for scheduled jobs
    logger.info("Scheduler is running. Checking for scheduled jobs...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()