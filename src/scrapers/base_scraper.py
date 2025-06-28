"""
Base scraper class for Web3 Data Aggregator
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import asyncio
from playwright.async_api import async_playwright, Browser, Page

from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..utils.helpers import request_utils
from ..config import config

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, source_name: str, source_url: str):
        self.source_name = source_name
        self.source_url = source_url
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    @abstractmethod
    async def scrape(self) -> ScrapingResult:
        """Abstract method to scrape data from the source"""
        pass
    
    async def setup_browser(self) -> bool:
        """Set up Playwright browser"""
        try:
            playwright = await async_playwright().start()
            
            # Browser launch options
            launch_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            }
            
            # Add proxy if configured
            proxy_config = config.get_proxy_config()
            if proxy_config:
                launch_options['proxy'] = proxy_config
            
            self.browser = await playwright.chromium.launch(**launch_options)
            
            # Create new page with random user agent
            self.page = await self.browser.new_page()
            await self.page.set_extra_http_headers({
                'User-Agent': request_utils.get_random_user_agent()
            })
            
            return True
            
        except Exception as e:
            logger.error("Failed to setup browser", error=e, source=self.source_name)
            return False
    
    async def cleanup_browser(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.warning("Error during browser cleanup", error=e, source=self.source_name)
    
    async def navigate_to_page(self, url: str, wait_for: Optional[str] = None) -> bool:
        """Navigate to a page and optionally wait for an element"""
        try:
            if not self.page:
                return False
            
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            if wait_for:
                await self.page.wait_for_selector(wait_for, timeout=10000)
            
            return True
            
        except Exception as e:
            logger.error("Failed to navigate to page", error=e, url=url, source=self.source_name)
            return False
    
    def create_project(self, name: str, website: str = None, twitter: str = None, 
                      linkedin: str = None, email: str = None) -> Optional[ProjectData]:
        """Create a ProjectData object with validation"""
        try:
            project = ProjectData(
                project_name=name,
                website=website,
                twitter=twitter,
                linkedin=linkedin,
                email=email,
                source=self.source_url
            )
            
            if project.is_valid():
                return project
            else:
                logger.warning("Invalid project data", project_name=name, source=self.source_name)
                return None
                
        except Exception as e:
            logger.error("Failed to create project", error=e, project_name=name, source=self.source_name)
            return None
    
    async def run_scraper(self) -> ScrapingResult:
        """Run the scraper with proper setup and cleanup"""
        logger.scraping_start(self.source_name, self.source_url)
        
        result = ScrapingResult(source=self.source_name)
        
        try:
            # Setup browser if needed
            browser_setup = await self.setup_browser()
            if not browser_setup:
                result.success = False
                result.error = "Failed to setup browser"
                return result
            
            # Run the actual scraping
            result = await self.scrape()
            
            if result.success:
                logger.scraping_success(self.source_name, result.get_project_count())
            else:
                logger.scraping_error(self.source_name, Exception(result.error or "Unknown error"))
            
        except Exception as e:
            logger.scraping_error(self.source_name, e)
            result.success = False
            result.error = str(e)
        
        finally:
            # Always cleanup browser
            await self.cleanup_browser()
        
        return result

class APIBasedScraper(BaseScraper):
    """Base class for API-based scrapers"""
    
    def __init__(self, source_name: str, source_url: str, api_key: Optional[str] = None):
        super().__init__(source_name, source_url)
        self.api_key = api_key
    
    async def make_api_request(self, url: str, headers: dict = None, params: dict = None) -> Optional[dict]:
        """Make API request with proper error handling"""
        try:
            request_headers = headers or {}
            
            if self.api_key:
                # Add API key to headers (common patterns)
                if 'X-API-Key' not in request_headers:
                    request_headers['X-API-Key'] = self.api_key
            
            response = request_utils.get(url, headers=request_headers, params=params)
            
            if response and response.status_code == 200:
                return response.json()
            else:
                logger.error("API request failed", 
                           url=url, 
                           status_code=response.status_code if response else None,
                           source=self.source_name)
                return None
                
        except Exception as e:
            logger.error("API request error", error=e, url=url, source=self.source_name)
            return None

