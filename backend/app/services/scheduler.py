"""
Background Task Scheduler for DoR-Dash
Handles periodic knowledge base updates and other maintenance tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.services.knowledge_base import knowledge_service

logger = logging.getLogger(__name__)

class PeriodicScheduler:
    def __init__(self):
        self.running = False
        self.tasks = []
    
    async def start_scheduler(self):
        """Start the background scheduler"""
        self.running = True
        logger.info("Starting periodic scheduler")
        
        # Schedule knowledge base snapshots every 6 hours
        asyncio.create_task(self.schedule_knowledge_snapshots())
        
        # Schedule weekly cleanup tasks
        asyncio.create_task(self.schedule_cleanup_tasks())
    
    async def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        logger.info("Stopping periodic scheduler")
    
    async def schedule_knowledge_snapshots(self):
        """Schedule periodic knowledge base snapshots"""
        snapshot_interval = 6 * 60 * 60  # 6 hours in seconds
        
        while self.running:
            try:
                # Wait for the interval
                await asyncio.sleep(snapshot_interval)
                
                if not self.running:
                    break
                
                logger.info("Starting scheduled knowledge base snapshot")
                
                # Create knowledge base snapshot
                snapshot = await knowledge_service.snapshot_submissions()
                
                logger.info(
                    f"Knowledge base snapshot completed: "
                    f"{snapshot.new_terms_found} new terms from "
                    f"{snapshot.total_submissions} submissions"
                )
                
                # Log summary for monitoring
                if snapshot.new_terms_found > 0:
                    logger.info(f"Top new terms: {snapshot.top_terms[:5]}")
                
            except Exception as e:
                logger.error(f"Error during scheduled knowledge snapshot: {e}")
                # Continue running even if one snapshot fails
                continue
    
    async def schedule_cleanup_tasks(self):
        """Schedule weekly cleanup and maintenance tasks"""
        cleanup_interval = 7 * 24 * 60 * 60  # 7 days in seconds
        
        while self.running:
            try:
                # Wait for the interval
                await asyncio.sleep(cleanup_interval)
                
                if not self.running:
                    break
                
                logger.info("Starting scheduled cleanup tasks")
                
                # Clean up old low-confidence terms
                await self.cleanup_low_confidence_terms()
                
                # Generate weekly knowledge base report
                await self.generate_weekly_report()
                
                logger.info("Scheduled cleanup tasks completed")
                
            except Exception as e:
                logger.error(f"Error during scheduled cleanup: {e}")
                continue
    
    async def cleanup_low_confidence_terms(self):
        """Remove very low confidence terms that haven't improved"""
        try:
            import sqlite3
            
            with sqlite3.connect(knowledge_service.db_path) as conn:
                # Remove terms with very low confidence that are old
                old_date = datetime.now() - timedelta(days=30)
                
                result = conn.execute('''
                    DELETE FROM terminology 
                    WHERE confidence_score < 0.2 
                    AND user_approved = FALSE 
                    AND last_seen < ?
                ''', (old_date.isoformat(),))
                
                if result.rowcount > 0:
                    logger.info(f"Cleaned up {result.rowcount} low-confidence terms")
                
        except Exception as e:
            logger.error(f"Error during term cleanup: {e}")
    
    async def generate_weekly_report(self):
        """Generate a weekly summary report of knowledge base activity"""
        try:
            import sqlite3
            
            with sqlite3.connect(knowledge_service.db_path) as conn:
                # Get statistics for the past week
                week_ago = datetime.now() - timedelta(days=7)
                
                # New terms added this week
                new_terms = conn.execute('''
                    SELECT COUNT(*) FROM terminology 
                    WHERE first_seen > ?
                ''', (week_ago.isoformat(),)).fetchone()[0]
                
                # Terms approved this week (approximation)
                approved_terms = conn.execute('''
                    SELECT COUNT(*) FROM terminology 
                    WHERE user_approved = TRUE AND last_seen > ?
                ''', (week_ago.isoformat(),)).fetchone()[0]
                
                # Most active categories
                active_categories = conn.execute('''
                    SELECT category, COUNT(*) as count
                    FROM terminology 
                    WHERE last_seen > ?
                    GROUP BY category 
                    ORDER BY count DESC 
                    LIMIT 5
                ''', (week_ago.isoformat(),)).fetchall()
                
                logger.info(
                    f"Weekly Knowledge Base Report: "
                    f"{new_terms} new terms, "
                    f"{approved_terms} approved terms, "
                    f"Active categories: {dict(active_categories)}"
                )
                
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")

# Global scheduler instance
scheduler = PeriodicScheduler()

# Startup/shutdown functions for FastAPI
async def start_background_tasks():
    """Start background tasks when the application starts"""
    await scheduler.start_scheduler()

async def stop_background_tasks():
    """Stop background tasks when the application shuts down"""
    await scheduler.stop_scheduler()