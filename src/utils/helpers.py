"""
Utility functions for Web3 Data Aggregator
"""
import random
import time
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

from ..config import config
from .logger import logger

class RequestUtils:
    """Utility class for making HTTP requests with anti-bot measures"""
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(config.user_agents)
    
    def add_delay(self):
        """Add random delay between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        min_delay = config.min_delay
        if time_since_last < min_delay:
            delay = random.uniform(min_delay, config.max_delay)
            time.sleep(delay)
        
        self.last_request_time = time.time()
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with anti-bot measures"""
        try:
            # Add delay
            self.add_delay()
            
            # Set headers
            headers = kwargs.get('headers', {})
            headers.update({
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            kwargs['headers'] = headers
            
            # Set timeout
            kwargs.setdefault('timeout', config.request_timeout)
            
            # Make request
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            logger.debug(f"Request successful", url=url, status_code=response.status_code)
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed", error=e, url=url)
            return None
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make GET request"""
        return self.make_request(url, 'GET', **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make POST request"""
        return self.make_request(url, 'POST', **kwargs)

class TextUtils:
    """Utility functions for text processing"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-\.\@\:\/]', '', text)
        
        return text
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address from text"""
        if not text:
            return None
        
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        if matches:
            # Filter out common non-business emails
            business_emails = []
            for email in matches:
                email = email.lower()
                if not any(domain in email for domain in ['example.com', 'test.com', 'gmail.com', 'yahoo.com', 'hotmail.com']):
                    business_emails.append(email)
            
            return business_emails[0] if business_emails else None
        
        return None
    
    @staticmethod
    def extract_social_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Optional[str]]:
        """Extract social media links from BeautifulSoup object"""
        social_links = {'twitter': None, 'linkedin': None}
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin(base_url, href)
            
            # Check for Twitter/X
            if any(domain in href.lower() for domain in ['twitter.com', 'x.com']) and not social_links['twitter']:
                social_links['twitter'] = href
            
            # Check for LinkedIn
            if 'linkedin.com/company' in href.lower() and not social_links['linkedin']:
                social_links['linkedin'] = href
        
        return social_links
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

class DeduplicationUtils:
    """Utility functions for deduplication"""
    
    @staticmethod
    def normalize_domain(url: str) -> Optional[str]:
        """Normalize domain for deduplication"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return None
    
    @staticmethod
    def normalize_project_name(name: str) -> str:
        """Normalize project name for deduplication"""
        if not name:
            return ""
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized.strip())
        
        return normalized

# Global utility instances
request_utils = RequestUtils()
text_utils = TextUtils()
dedup_utils = DeduplicationUtils()

