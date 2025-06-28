"""
Scraper manager for Web3 Data Aggregator
"""
import asyncio
from typing import List, Dict, Type
from concurrent.futures import ThreadPoolExecutor

from .base_scraper import BaseScraper
from .cryptorank_scraper import CryptoRankScraper
from .icodrops_scraper import ICODropsScraper
from .coinmarketcap_scraper import CoinMarketCapScraper
from .dappradar_scraper import DappRadarScraper
from .zealy_scraper import ZealyScraper
from .daomaker_scraper import DAOMakerScraper
from .polkastarter_scraper import PolkastarterScraper

from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..config import config

class ScraperManager:
    """Manages all scrapers and coordinates the scraping process"""
    
    def __init__(self):
        self.scrapers: Dict[str, Type[BaseScraper]] = {
            'cryptorank': CryptoRankScraper,
            'icodrops': ICODropsScraper,
            'coinmarketcap': CoinMarketCapScraper,
            'dappradar': DappRadarScraper,
            'zealy': ZealyScraper,
            'daomaker': DAOMakerScraper,
            'polkastarter': PolkastarterScraper
        }
        
        self.enabled_scrapers = list(self.scrapers.keys())
        self.max_concurrent_scrapers = 3  # Limit concurrent scrapers to avoid overwhelming sites
    
    async def run_all_scrapers(self) -> List[ProjectData]:
        """Run all enabled scrapers and collect results"""
        logger.info("Starting scraping process", total_scrapers=len(self.enabled_scrapers))
        
        all_projects = []
        successful_scrapers = 0
        failed_scrapers = 0
        
        # Run scrapers in batches to avoid overwhelming the system
        for i in range(0, len(self.enabled_scrapers), self.max_concurrent_scrapers):
            batch = self.enabled_scrapers[i:i + self.max_concurrent_scrapers]
            
            # Create scraper instances for this batch
            scraper_instances = []
            for scraper_name in batch:
                try:
                    scraper_class = self.scrapers[scraper_name]
                    scraper_instance = scraper_class()
                    scraper_instances.append(scraper_instance)
                except Exception as e:
                    logger.error(f"Failed to create scraper instance", error=e, scraper=scraper_name)
                    failed_scrapers += 1
            
            # Run scrapers in this batch concurrently
            if scraper_instances:
                batch_results = await self._run_scraper_batch(scraper_instances)
                
                # Process results
                for result in batch_results:
                    if result.success:
                        all_projects.extend(result.projects)
                        successful_scrapers += 1
                        logger.success(f"Scraper completed successfully", 
                                     scraper=result.source, 
                                     projects_found=len(result.projects))
                    else:
                        failed_scrapers += 1
                        logger.error(f"Scraper failed", 
                                   scraper=result.source, 
                                   error=result.error)
            
            # Add delay between batches
            if i + self.max_concurrent_scrapers < len(self.enabled_scrapers):
                await asyncio.sleep(5)
        
        logger.info("Scraping process completed", 
                   total_projects=len(all_projects),
                   successful_scrapers=successful_scrapers,
                   failed_scrapers=failed_scrapers)
        
        return all_projects
    
    async def _run_scraper_batch(self, scrapers: List[BaseScraper]) -> List[ScrapingResult]:
        """Run a batch of scrapers concurrently"""
        tasks = []
        
        for scraper in scrapers:
            task = asyncio.create_task(scraper.run_scraper())
            tasks.append(task)
        
        # Wait for all scrapers in the batch to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create a failed result for exceptions
                failed_result = ScrapingResult(source=scrapers[i].source_name)
                failed_result.success = False
                failed_result.error = str(result)
                processed_results.append(failed_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def run_single_scraper(self, scraper_name: str) -> ScrapingResult:
        """Run a single scraper by name"""
        if scraper_name not in self.scrapers:
            result = ScrapingResult(source=scraper_name)
            result.success = False
            result.error = f"Unknown scraper: {scraper_name}"
            return result
        
        try:
            scraper_class = self.scrapers[scraper_name]
            scraper_instance = scraper_class()
            result = await scraper_instance.run_scraper()
            return result
        except Exception as e:
            logger.error(f"Failed to run scraper", error=e, scraper=scraper_name)
            result = ScrapingResult(source=scraper_name)
            result.success = False
            result.error = str(e)
            return result
    
    def enable_scraper(self, scraper_name: str):
        """Enable a specific scraper"""
        if scraper_name in self.scrapers and scraper_name not in self.enabled_scrapers:
            self.enabled_scrapers.append(scraper_name)
            logger.info(f"Enabled scraper", scraper=scraper_name)
    
    def disable_scraper(self, scraper_name: str):
        """Disable a specific scraper"""
        if scraper_name in self.enabled_scrapers:
            self.enabled_scrapers.remove(scraper_name)
            logger.info(f"Disabled scraper", scraper=scraper_name)
    
    def get_enabled_scrapers(self) -> List[str]:
        """Get list of enabled scrapers"""
        return self.enabled_scrapers.copy()
    
    def get_available_scrapers(self) -> List[str]:
        """Get list of all available scrapers"""
        return list(self.scrapers.keys())

# Global scraper manager instance
scraper_manager = ScraperManager()

