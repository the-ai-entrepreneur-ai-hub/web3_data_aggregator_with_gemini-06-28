"""
Email enrichment service for Web3 Data Aggregator
"""
import re
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from ..utils.models import ProjectData, EnrichmentResult
from ..utils.logger import logger
from ..utils.helpers import request_utils, text_utils
from ..config import config

class EmailEnrichmentService:
    """Service for finding email addresses for projects"""
    
    def __init__(self):
        self.hunter_api_key = config.hunter_io_api_key
        self.snov_api_key = config.snov_io_api_key
        self.service = config.email_enrichment_service
    
    async def enrich_project_email(self, project: ProjectData) -> EnrichmentResult:
        """Find email address for a project"""
        result = EnrichmentResult(
            project_name=project.project_name,
            enrichment_type='email'
        )
        
        try:
            logger.enrichment_start(project.project_name, 'email')
            
            # First try to find email on the project website
            if project.website:
                email = await self._find_email_on_website(project.website)
                if email:
                    result.result = email
                    result.success = True
                    logger.enrichment_success(project.project_name, 'email', email)
                    return result
            
            # If no email found on website, try API services
            if project.website:
                domain = self._extract_domain(project.website)
                if domain:
                    if self.service == 'hunter' and self.hunter_api_key:
                        email = await self._find_email_with_hunter(domain)
                    elif self.service == 'snov' and self.snov_api_key:
                        email = await self._find_email_with_snov(domain)
                    else:
                        email = None
                    
                    if email:
                        result.result = email
                        result.success = True
                        logger.enrichment_success(project.project_name, 'email', email)
                        return result
            
            # No email found
            result.success = True  # Not finding an email is not an error
            result.result = None
            logger.info("No email found for project", project=project.project_name)
            
        except Exception as e:
            logger.enrichment_error(project.project_name, 'email', e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def _find_email_on_website(self, website_url: str) -> Optional[str]:
        """Find email address by scraping the project website"""
        try:
            # Try common pages that might contain contact information
            pages_to_check = [
                website_url,
                f"{website_url.rstrip('/')}/contact",
                f"{website_url.rstrip('/')}/about",
                f"{website_url.rstrip('/')}/team",
                f"{website_url.rstrip('/')}/contact-us"
            ]
            
            for page_url in pages_to_check:
                try:
                    response = request_utils.get(page_url)
                    if response and response.status_code == 200:
                        # Extract email from page content
                        email = text_utils.extract_email(response.text)
                        if email:
                            return email
                        
                        # Also try parsing with BeautifulSoup for better text extraction
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text_content = soup.get_text()
                        email = text_utils.extract_email(text_content)
                        if email:
                            return email
                
                except Exception as e:
                    logger.debug(f"Failed to check page for email", url=page_url, error=str(e))
                    continue
            
            return None
            
        except Exception as e:
            logger.error("Failed to find email on website", error=e, website=website_url)
            return None
    
    async def _find_email_with_hunter(self, domain: str) -> Optional[str]:
        """Find email using Hunter.io API"""
        try:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key,
                'limit': 1
            }
            
            response = request_utils.get(url, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'emails' in data['data']:
                    emails = data['data']['emails']
                    if emails:
                        # Return the first email found
                        return emails[0].get('value')
            
            return None
            
        except Exception as e:
            logger.error("Hunter.io API request failed", error=e, domain=domain)
            return None
    
    async def _find_email_with_snov(self, domain: str) -> Optional[str]:
        """Find email using Snov.io API"""
        try:
            url = "https://app.snov.io/restapi/get-domain-emails-with-info"
            params = {
                'domain': domain,
                'type': 'all',
                'limit': 1
            }
            headers = {
                'Authorization': f'Bearer {self.snov_api_key}'
            }
            
            response = request_utils.get(url, params=params, headers=headers)
            
            if response and response.status_code == 200:
                data = response.json()
                
                if 'emails' in data and data['emails']:
                    # Return the first email found
                    return data['emails'][0].get('email')
            
            return None
            
        except Exception as e:
            logger.error("Snov.io API request failed", error=e, domain=domain)
            return None
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
            
        except Exception:
            return None

# Global email enrichment service instance
email_enrichment_service = EmailEnrichmentService()

