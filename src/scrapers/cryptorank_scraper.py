"""
CryptoRank API scraper for Web3 Data Aggregator
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .base_scraper import APIBasedScraper
from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..config import config

class CryptoRankScraper(APIBasedScraper):
    """Scraper for CryptoRank funding rounds API"""
    
    def __init__(self):
        super().__init__(
            source_name="CryptoRank",
            source_url="https://cryptorank.io/funding-rounds",
            api_key=config.cryptorank_api_key
        )
        self.api_base_url = "https://api.cryptorank.io/v2"
    
    async def scrape(self) -> ScrapingResult:
        """Scrape funding rounds from CryptoRank API"""
        result = ScrapingResult(source=self.source_name)
        
        try:
            # Get recent funding rounds
            funding_rounds = await self.get_funding_rounds()
            
            if not funding_rounds:
                result.success = False
                result.error = "No funding rounds data received"
                return result
            
            # Process each funding round
            for round_data in funding_rounds:
                project = await self.process_funding_round(round_data)
                if project:
                    result.add_project(project)
            
            result.success = True
            
        except Exception as e:
            logger.error("CryptoRank scraping failed", error=e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def get_funding_rounds(self) -> Optional[List[Dict[str, Any]]]:
        """Get recent funding rounds from CryptoRank API"""
        try:
            # Calculate date range for recent funding rounds (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                'limit': 100,
                'offset': 0,
                'dateFrom': start_date.strftime('%Y-%m-%d'),
                'dateTo': end_date.strftime('%Y-%m-%d')
            }
            
            url = f"{self.api_base_url}/currencies/funding-rounds"
            data = await self.make_api_request(url, params=params)
            
            if data and 'data' in data:
                return data['data']
            
            return None
            
        except Exception as e:
            logger.error("Failed to get funding rounds", error=e, source=self.source_name)
            return None
    
    async def process_funding_round(self, round_data: Dict[str, Any]) -> Optional[ProjectData]:
        """Process a single funding round and extract project data"""
        try:
            # Extract basic project info from funding round
            currency = round_data.get('currency', {})
            
            project_name = currency.get('name')
            if not project_name:
                return None
            
            # Get project details
            project_details = await self.get_project_details(currency.get('id'))
            
            website = None
            twitter = None
            linkedin = None
            
            if project_details:
                links = project_details.get('links', [])
                
                for link in links:
                    link_type = link.get('type', '').lower()
                    url = link.get('url', '')
                    
                    if link_type == 'website' and not website:
                        website = url
                    elif link_type in ['twitter', 'x'] and not twitter:
                        twitter = url
                    elif link_type == 'linkedin' and not linkedin:
                        linkedin = url
            
            # Create project data
            project = self.create_project(
                name=project_name,
                website=website,
                twitter=twitter,
                linkedin=linkedin
            )
            
            return project
            
        except Exception as e:
            logger.error("Failed to process funding round", error=e, source=self.source_name)
            return None
    
    async def get_project_details(self, currency_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed project information by currency ID"""
        try:
            if not currency_id:
                return None
            
            url = f"{self.api_base_url}/currencies/{currency_id}"
            data = await self.make_api_request(url)
            
            if data and 'data' in data:
                return data['data']
            
            return None
            
        except Exception as e:
            logger.error("Failed to get project details", error=e, currency_id=currency_id, source=self.source_name)
            return None

