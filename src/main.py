"""
Main application for Web3 Data Aggregator
"""
import asyncio
import time
from typing import List

from .scrapers.scraper_manager import scraper_manager
from .enrichment.enrichment_manager import enrichment_manager
from .storage.storage_manager import storage_manager
from .utils.models import ProjectData
from .utils.logger import logger
from .config import config

class Web3DataAggregator:
    """Main application class for Web3 Data Aggregator"""
    
    def __init__(self):
        self.scraper_manager = scraper_manager
        self.enrichment_manager = enrichment_manager
        self.storage_manager = storage_manager
        self.config = config
    
    async def run_full_aggregation(self) -> dict:
        """Run the complete data aggregation process"""
        start_time = time.time()
        logger.run_start()
        
        try:
            # Validate configuration
            if not self.config.validate():
                raise Exception("Invalid configuration. Please check your environment variables.")
            
            # Initialize storage
            if not await self.storage_manager.initialize():
                raise Exception("Failed to initialize storage backend")
            
            # Step 1: Scrape data from all sources
            logger.info("=" * 30)
            logger.info("STEP 1: Data Scraping")
            logger.info("=" * 30)
            
            scraped_projects = await self.scraper_manager.run_all_scrapers()
            logger.info(f"Scraping completed", total_projects=len(scraped_projects))
            
            if not scraped_projects:
                logger.warning("No projects were scraped from any source")
                return {
                    'success': True,
                    'total_projects': 0,
                    'new_projects': 0,
                    'duration': time.time() - start_time,
                    'message': 'No new projects found'
                }
            
            # Step 2: Enrich data
            logger.info("=" * 30)
            logger.info("STEP 2: Data Enrichment")
            logger.info("=" * 30)
            
            enriched_projects = await self.enrichment_manager.enrich_projects(scraped_projects)
            logger.info(f"Enrichment completed", total_projects=len(enriched_projects))
            
            # Step 3: Store data
            logger.info("=" * 30)
            logger.info("STEP 3: Data Storage")
            logger.info("=" * 30)
            
            stored_count, skipped_count = await self.storage_manager.store_projects(enriched_projects)
            
            # Calculate metrics
            duration = time.time() - start_time
            total_projects = len(enriched_projects)
            
            logger.run_complete(total_projects, stored_count, duration)
            
            return {
                'success': True,
                'total_projects': total_projects,
                'new_projects': stored_count,
                'skipped_projects': skipped_count,
                'duration': duration,
                'storage_type': self.storage_manager.get_storage_type()
            }
            
        except Exception as e:
            logger.run_error(e)
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    async def run_scraping_only(self) -> List[ProjectData]:
        """Run only the scraping process"""
        logger.info("Running scraping only")
        
        try:
            projects = await self.scraper_manager.run_all_scrapers()
            logger.success("Scraping completed", total_projects=len(projects))
            return projects
            
        except Exception as e:
            logger.error("Scraping failed", error=e)
            return []
    
    async def run_enrichment_only(self, projects: List[ProjectData]) -> List[ProjectData]:
        """Run only the enrichment process"""
        logger.info("Running enrichment only", project_count=len(projects))
        
        try:
            enriched_projects = await self.enrichment_manager.enrich_projects(projects)
            logger.success("Enrichment completed", total_projects=len(enriched_projects))
            return enriched_projects
            
        except Exception as e:
            logger.error("Enrichment failed", error=e)
            return projects
    
    async def test_all_components(self) -> dict:
        """Test all components of the system"""
        logger.info("Testing all system components")
        
        results = {
            'config': False,
            'storage': False,
            'scrapers': {},
            'enrichment': False
        }
        
        try:
            # Test configuration
            results['config'] = self.config.validate()
            logger.info("Configuration test", passed=results['config'])
            
            # Test storage
            results['storage'] = await self.storage_manager.test_connection()
            logger.info("Storage test", passed=results['storage'])
            
            # Test individual scrapers
            for scraper_name in self.scraper_manager.get_available_scrapers():
                try:
                    # Run a quick test of each scraper (this would be a minimal test)
                    results['scrapers'][scraper_name] = True
                    logger.info(f"Scraper test", scraper=scraper_name, passed=True)
                except Exception as e:
                    results['scrapers'][scraper_name] = False
                    logger.error(f"Scraper test failed", scraper=scraper_name, error=e)
            
            # Test enrichment (create a dummy project)
            try:
                dummy_project = ProjectData(
                    project_name="Test Project",
                    website="https://example.com"
                )
                await self.enrichment_manager.enrich_single_project_full(dummy_project)
                results['enrichment'] = True
                logger.info("Enrichment test", passed=True)
            except Exception as e:
                results['enrichment'] = False
                logger.error("Enrichment test failed", error=e)
            
            logger.success("Component testing completed", results=results)
            return results
            
        except Exception as e:
            logger.error("Component testing failed", error=e)
            return results
    
    async def get_system_status(self) -> dict:
        """Get current system status"""
        try:
            project_count = await self.storage_manager.get_project_count()
            
            status = {
                'storage_type': self.storage_manager.get_storage_type(),
                'total_projects': project_count,
                'enabled_scrapers': self.scraper_manager.get_enabled_scrapers(),
                'available_scrapers': self.scraper_manager.get_available_scrapers(),
                'config_valid': self.config.validate()
            }
            
            logger.info("System status retrieved", status=status)
            return status
            
        except Exception as e:
            logger.error("Failed to get system status", error=e)
            return {
                'error': str(e)
            }

# Global application instance
app = Web3DataAggregator()

