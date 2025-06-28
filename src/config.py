"""
Configuration management for Web3 Data Aggregator
"""
import os
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Configuration class for the Web3 Data Aggregator"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Storage Configuration
        self.storage_type = os.getenv('STORAGE_TYPE', 'google_sheets')
        self.run_schedule = os.getenv('RUN_SCHEDULE', 'daily')
        
        # Google Sheets Configuration
        self.google_sheets_key = os.getenv('GOOGLE_SHEETS_KEY')
        self.google_sheets_spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.google_sheets_sheet_name = os.getenv('GOOGLE_SHEETS_SHEET_NAME', 'Sheet1')
        
        # Airtable Configuration
        self.airtable_pat = os.getenv('AIRTABLE_PAT')
        self.airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
        self.airtable_table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Projects')
        
        # API Keys
        self.hunter_io_api_key = os.getenv('HUNTER_IO_API_KEY')
        self.coinmarketcap_api_key = os.getenv('COINMARKETCAP_API_KEY')
        self.cryptorank_api_key = os.getenv('CRYPTORANK_API_KEY')
        self.dappradar_api_key = os.getenv('DAPPRADAR_API_KEY')
        
        # Email Enrichment
        self.email_enrichment_service = os.getenv('EMAIL_ENRICHMENT_SERVICE', 'hunter')
        self.snov_io_api_key = os.getenv('SNOV_IO_API_KEY')
        
        # Proxy Configuration (optional)
        self.proxy_host = os.getenv('PROXY_HOST')
        self.proxy_port = os.getenv('PROXY_PORT')
        self.proxy_username = os.getenv('PROXY_USERNAME')
        self.proxy_password = os.getenv('PROXY_PASSWORD')
        
        # Data Sources URLs
        self.data_sources = {
            'cryptorank': 'https://api.cryptorank.io/v2/currencies/funding-rounds',
            'icodrops': 'https://icodrops.com/',
            'dropstab': 'https://dropstab.com/',
            'dappradar': 'https://dappradar.com/rankings?new=true',
            'zealy': 'https://zealy.io/explore/new-web3-communities',
            'coinmarketcap': 'https://coinmarketcap.com/new/',
            'daomaker': 'https://app.daomaker.com/launchpad',
            'polkastarter': 'https://polkastarter.com/projects'
        }
        
        # Request settings
        self.request_timeout = 30
        self.min_delay = 2
        self.max_delay = 10
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if self.storage_type == 'google_sheets':
            if not self.google_sheets_key or not self.google_sheets_spreadsheet_id:
                return False
        elif self.storage_type == 'airtable':
            if not self.airtable_pat or not self.airtable_base_id:
                return False
        else:
            return False
            
        return True
    
    def get_proxy_config(self) -> Optional[dict]:
        """Get proxy configuration if available"""
        if all([self.proxy_host, self.proxy_port, self.proxy_username, self.proxy_password]):
            return {
                'server': f'http://{self.proxy_host}:{self.proxy_port}',
                'username': self.proxy_username,
                'password': self.proxy_password
            }
        return None

# Global config instance
config = Config()

