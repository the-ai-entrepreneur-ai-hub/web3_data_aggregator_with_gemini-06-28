"""
Zealy Communities scraper for Web3 Data Aggregator
"""
from typing import List, Optional
from bs4 import BeautifulSoup
import asyncio

from .base_scraper import BaseScraper
from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..utils.helpers import text_utils

class ZealyScraper(BaseScraper):
    """Scraper for Zealy new Web3 communities"""
    
    def __init__(self):
        super().__init__(
            source_name="Zealy",
            source_url="https://zealy.io/explore/new-web3-communities"
        )
    
    async def scrape(self) -> ScrapingResult:
        """Scrape new Web3 communities from Zealy"""
        result = ScrapingResult(source=self.source_name)
        
        try:
            # Navigate to the page
            if not await self.navigate_to_page(self.source_url):
                result.success = False
                result.error = "Failed to navigate to Zealy page"
                return result
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Try to wait for community cards to load
            try:
                await self.page.wait_for_selector('[data-testid*="community"], .community-card, .card', timeout=10000)
            except:
                # Continue even if specific selectors aren't found
                pass
            
            # Get page content
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract projects
            projects = await self.extract_projects(soup)
            
            for project in projects:
                if project:
                    result.add_project(project)
            
            result.success = True
            
        except Exception as e:
            logger.error("Zealy scraping failed", error=e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def extract_projects(self, soup: BeautifulSoup) -> List[Optional[ProjectData]]:
        """Extract project data from Zealy page"""
        projects = []
        
        try:
            # Look for community cards with various selectors
            selectors = [
                '[data-testid*="community"]',
                '.community-card',
                '.card',
                '[class*="community"]',
                '[class*="card"]'
            ]
            
            community_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    community_elements = elements
                    break
            
            # If no specific cards found, look for any containers with links
            if not community_elements:
                community_elements = soup.find_all('div', class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['item', 'row', 'col', 'container']
                ))
            
            for element in community_elements[:20]:  # Limit to first 20
                project = await self.extract_project_from_element(element)
                if project:
                    projects.append(project)
        
        except Exception as e:
            logger.error("Failed to extract projects from Zealy", error=e)
        
        return projects
    
    async def extract_project_from_element(self, element) -> Optional[ProjectData]:
        """Extract project data from a single element"""
        try:
            # Extract project name
            name_element = element.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if not name_element:
                name_element = element.find('a')
            if not name_element:
                # Try to find any text that looks like a project name
                text_content = element.get_text().strip()
                if len(text_content) > 50:  # Too long to be a project name
                    return None
                name_element = element
            
            project_name = text_utils.clean_text(name_element.get_text())
            if not project_name or len(project_name) < 2:
                return None
            
            # Extract links
            website = None
            twitter = None
            linkedin = None
            
            # Look for external links
            links = element.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                
                # Skip internal Zealy links
                if 'zealy.io' in href:
                    continue
                
                # Categorize links
                if any(domain in href.lower() for domain in ['twitter.com', 'x.com']) and not twitter:
                    twitter = href
                elif 'linkedin.com' in href.lower() and not linkedin:
                    linkedin = href
                elif href.startswith('http') and not website:
                    # Check if it's not a social media link
                    if not any(social in href.lower() for social in ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com']):
                        website = href
            
            # Extract social links using utility function
            social_links = text_utils.extract_social_links(element, self.source_url)
            if not twitter:
                twitter = social_links.get('twitter')
            if not linkedin:
                linkedin = social_links.get('linkedin')
            
            # Create project
            project = self.create_project(
                name=project_name,
                website=website,
                twitter=twitter,
                linkedin=linkedin
            )
            
            return project
            
        except Exception as e:
            logger.error("Failed to extract project from Zealy element", error=e, source=self.source_name)
            return None

