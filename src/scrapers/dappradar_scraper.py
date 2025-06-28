"""
DappRadar API scraper for Web3 Data Aggregator
"""
from typing import List, Optional, Dict, Any

from .base_scraper import APIBasedScraper
from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..config import config

class DappRadarScraper(APIBasedScraper):
    """Scraper for DappRadar new dapps API"""
    
    def __init__(self):
        super().__init__(
            source_name="DappRadar",
            source_url="https://dappradar.com/rankings?new=true",
            api_key=config.dappradar_api_key
        )
        self.api_base_url = "https://api.dappradar.com"
    
    async def scrape(self) -> ScrapingResult:
        """Scrape new dapps from DappRadar API"""
        result = ScrapingResult(source=self.source_name)
        
        try:
            # Get new dapps
            new_dapps = await self.get_new_dapps()
            
            if not new_dapps:
                result.success = False
                result.error = "No new dapps data received"
                return result
            
            # Process each dapp
            for dapp_data in new_dapps:
                project = await self.process_dapp_data(dapp_data)
                if project:
                    result.add_project(project)
            
            result.success = True
            
        except Exception as e:
            logger.error("DappRadar scraping failed", error=e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def get_new_dapps(self) -> Optional[List[Dict[str, Any]]]:
        """Get new dapps from DappRadar API"""
        try:
            params = {
                'limit': 50,
                'offset': 0,
                'sort': 'newest',
                'order': 'desc'
            }
            
            headers = {
                'X-API-Key': self.api_key,
                'Accept': 'application/json'
            }
            
            # Try different API endpoints
            endpoints = [
                f"{self.api_base_url}/v2/dapps",
                f"{self.api_base_url}/v1/dapps/search",
                f"{self.api_base_url}/dapps"
            ]
            
            for endpoint in endpoints:
                data = await self.make_api_request(endpoint, headers=headers, params=params)
                
                if data:
                    # Handle different response formats
                    if 'results' in data:
                        return data['results']
                    elif 'data' in data:
                        return data['data']
                    elif isinstance(data, list):
                        return data
                    else:
                        return [data]
            
            return None
            
        except Exception as e:
            logger.error("Failed to get new dapps", error=e, source=self.source_name)
            return None
    
    async def process_dapp_data(self, dapp_data: Dict[str, Any]) -> Optional[ProjectData]:
        """Process a single dapp and extract project data"""
        try:
            # Extract project name
            project_name = dapp_data.get('name') or dapp_data.get('title')
            if not project_name:
                return None
            
            # Extract website
            website = dapp_data.get('website') or dapp_data.get('url') or dapp_data.get('link')
            
            # Extract social links
            twitter = None
            linkedin = None
            
            # Check for social links in various fields
            social_links = dapp_data.get('social', {}) or dapp_data.get('links', {})
            
            if isinstance(social_links, dict):
                twitter = social_links.get('twitter') or social_links.get('x')
                linkedin = social_links.get('linkedin')
            
            # Alternative: check for social links in a links array
            links = dapp_data.get('links', [])
            if isinstance(links, list):
                for link in links:
                    if isinstance(link, dict):
                        link_type = link.get('type', '').lower()
                        url = link.get('url', '')
                        
                        if link_type == 'twitter' and not twitter:
                            twitter = url
                        elif link_type == 'linkedin' and not linkedin:
                            linkedin = url
                        elif link_type == 'website' and not website:
                            website = url
            
            # Create project data
            project = self.create_project(
                name=project_name,
                website=website,
                twitter=twitter,
                linkedin=linkedin
            )
            
            return project
            
        except Exception as e:
            logger.error("Failed to process dapp data", error=e, source=self.source_name)
            return None

