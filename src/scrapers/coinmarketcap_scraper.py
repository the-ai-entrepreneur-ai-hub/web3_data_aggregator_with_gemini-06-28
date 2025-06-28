"""
CoinMarketCap API scraper for Web3 Data Aggregator
"""
from typing import List, Optional, Dict, Any

from .base_scraper import APIBasedScraper
from ..utils.models import ProjectData, ScrapingResult
from ..utils.logger import logger
from ..config import config

class CoinMarketCapScraper(APIBasedScraper):
    """Scraper for CoinMarketCap new coins API"""
    
    def __init__(self):
        super().__init__(
            source_name="CoinMarketCap",
            source_url="https://coinmarketcap.com/new/",
            api_key=config.coinmarketcap_api_key
        )
        self.api_base_url = "https://pro-api.coinmarketcap.com/v1"
    
    async def scrape(self) -> ScrapingResult:
        """Scrape new coins from CoinMarketCap API"""
        result = ScrapingResult(source=self.source_name)
        
        try:
            # Get latest listings
            latest_coins = await self.get_latest_listings()
            
            if not latest_coins:
                result.success = False
                result.error = "No latest coins data received"
                return result
            
            # Process each coin
            for coin_data in latest_coins:
                project = await self.process_coin_data(coin_data)
                if project:
                    result.add_project(project)
            
            result.success = True
            
        except Exception as e:
            logger.error("CoinMarketCap scraping failed", error=e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def get_latest_listings(self) -> Optional[List[Dict[str, Any]]]:
        """Get latest coin listings from CoinMarketCap API"""
        try:
            params = {
                'start': 1,
                'limit': 50,  # Get top 50 new listings
                'sort': 'date_added',
                'sort_dir': 'desc'
            }
            
            headers = {
                'X-CMC_PRO_API_KEY': self.api_key,
                'Accept': 'application/json'
            }
            
            url = f"{self.api_base_url}/cryptocurrency/listings/latest"
            data = await self.make_api_request(url, headers=headers, params=params)
            
            if data and 'data' in data:
                return data['data']
            
            return None
            
        except Exception as e:
            logger.error("Failed to get latest listings", error=e, source=self.source_name)
            return None
    
    async def process_coin_data(self, coin_data: Dict[str, Any]) -> Optional[ProjectData]:
        """Process a single coin and extract project data"""
        try:
            project_name = coin_data.get('name')
            if not project_name:
                return None
            
            # Get additional metadata
            coin_id = coin_data.get('id')
            metadata = await self.get_coin_metadata(coin_id) if coin_id else None
            
            website = None
            twitter = None
            linkedin = None
            
            if metadata:
                urls = metadata.get('urls', {})
                
                # Extract website
                websites = urls.get('website', [])
                if websites:
                    website = websites[0]
                
                # Extract Twitter
                twitter_urls = urls.get('twitter', [])
                if twitter_urls:
                    twitter = twitter_urls[0]
                
                # Extract other social links
                technical_doc = urls.get('technical_doc', [])
                if technical_doc and not website:
                    website = technical_doc[0]
            
            # Create project data
            project = self.create_project(
                name=project_name,
                website=website,
                twitter=twitter,
                linkedin=linkedin
            )
            
            return project
            
        except Exception as e:
            logger.error("Failed to process coin data", error=e, source=self.source_name)
            return None
    
    async def get_coin_metadata(self, coin_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed coin metadata by ID"""
        try:
            if not coin_id:
                return None
            
            params = {
                'id': coin_id
            }
            
            headers = {
                'X-CMC_PRO_API_KEY': self.api_key,
                'Accept': 'application/json'
            }
            
            url = f"{self.api_base_url}/cryptocurrency/info"
            data = await self.make_api_request(url, headers=headers, params=params)
            
            if data and 'data' in data and str(coin_id) in data['data']:
                return data['data'][str(coin_id)]
            
            return None
            
        except Exception as e:
            logger.error("Failed to get coin metadata", error=e, coin_id=coin_id, source=self.source_name)
            return None

