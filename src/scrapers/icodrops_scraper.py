"""
ICO Drops scraper for Web3 Data Aggregator
"""
from typing import List, Optional
from bs4 import BeautifulSoup
import re

from .base_scraper import BaseScraper
from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..utils.helpers import request_utils, text_utils

class ICODropsScraper(BaseScraper):
    """Scraper for ICO Drops website"""
    
    def __init__(self):
        super().__init__(
            source_name="ICO Drops",
            source_url="https://icodrops.com/"
        )
    
    async def scrape(self) -> ScrapingResult:
        """Scrape projects from ICO Drops"""
        result = ScrapingResult(source=self.source_name)
        
        try:
            # Get the main page content
            response = request_utils.get(self.source_url)
            
            if not response:
                result.success = False
                result.error = "Failed to fetch ICO Drops page"
                return result
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find project cards/listings
            projects = await self.extract_projects(soup)
            
            for project in projects:
                if project:
                    result.add_project(project)
            
            result.success = True
            
        except Exception as e:
            logger.error("ICO Drops scraping failed", error=e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def extract_projects(self, soup: BeautifulSoup) -> List[Optional[ProjectData]]:
        """Extract project data from the page"""
        projects = []
        
        try:
            # Look for project containers (common patterns on ICO listing sites)
            project_containers = soup.find_all(['div', 'article'], class_=re.compile(r'(project|ico|card|item)', re.I))
            
            if not project_containers:
                # Try alternative selectors
                project_containers = soup.find_all('div', class_=re.compile(r'(row|col)', re.I))
            
            for container in project_containers[:20]:  # Limit to first 20 projects
                project = await self.extract_project_from_container(container)
                if project:
                    projects.append(project)
            
            # If no projects found with containers, try table rows
            if not projects:
                table_rows = soup.find_all('tr')
                for row in table_rows[:20]:
                    project = await self.extract_project_from_row(row)
                    if project:
                        projects.append(project)
        
        except Exception as e:
            logger.error("Failed to extract projects from ICO Drops", error=e)
        
        return projects
    
    async def extract_project_from_container(self, container) -> Optional[ProjectData]:
        """Extract project data from a container element"""
        try:
            # Extract project name
            name_element = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'], class_=re.compile(r'(name|title)', re.I))
            if not name_element:
                name_element = container.find('a')
            
            if not name_element:
                return None
            
            project_name = text_utils.clean_text(name_element.get_text())
            if not project_name:
                return None
            
            # Extract website link
            website = None
            website_link = container.find('a', href=re.compile(r'^https?://'))
            if website_link:
                href = website_link.get('href')
                if href and not any(domain in href for domain in ['icodrops.com', 'twitter.com', 'linkedin.com']):
                    website = href
            
            # Extract social links
            social_links = text_utils.extract_social_links(container, self.source_url)
            
            # Create project
            project = self.create_project(
                name=project_name,
                website=website,
                twitter=social_links.get('twitter'),
                linkedin=social_links.get('linkedin')
            )
            
            return project
            
        except Exception as e:
            logger.error("Failed to extract project from container", error=e, source=self.source_name)
            return None
    
    async def extract_project_from_row(self, row) -> Optional[ProjectData]:
        """Extract project data from a table row"""
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                return None
            
            # First cell usually contains project name/link
            first_cell = cells[0]
            
            # Extract project name
            name_element = first_cell.find('a') or first_cell
            project_name = text_utils.clean_text(name_element.get_text())
            
            if not project_name or len(project_name) < 2:
                return None
            
            # Extract website
            website = None
            link = first_cell.find('a')
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('http') and 'icodrops.com' not in href:
                    website = href
            
            # Look for social links in other cells
            twitter = None
            linkedin = None
            
            for cell in cells[1:]:
                social_links = text_utils.extract_social_links(cell, self.source_url)
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
            logger.error("Failed to extract project from row", error=e, source=self.source_name)
            return None

