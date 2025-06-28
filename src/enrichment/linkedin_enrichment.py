"""
LinkedIn enrichment service for Web3 Data Aggregator
"""
import re
from typing import Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from ..utils.models import ProjectData, EnrichmentResult
from ..utils.logger import logger
from ..utils.helpers import request_utils, text_utils
from ..config import config

class LinkedInEnrichmentService:
    """Service for finding LinkedIn company pages for projects"""
    
    def __init__(self):
        pass
    
    async def enrich_project_linkedin(self, project: ProjectData) -> EnrichmentResult:
        """Find LinkedIn company page for a project"""
        result = EnrichmentResult(
            project_name=project.project_name,
            enrichment_type='linkedin'
        )
        
        try:
            logger.enrichment_start(project.project_name, 'linkedin')
            
            # First try to find LinkedIn link on the project website
            if project.website:
                linkedin_url = await self._find_linkedin_on_website(project.website)
                if linkedin_url:
                    result.result = linkedin_url
                    result.success = True
                    logger.enrichment_success(project.project_name, 'linkedin', linkedin_url)
                    return result
            
            # If no LinkedIn found on website, try Google search
            linkedin_url = await self._find_linkedin_via_google_search(project.project_name)
            if linkedin_url:
                result.result = linkedin_url
                result.success = True
                logger.enrichment_success(project.project_name, 'linkedin', linkedin_url)
                return result
            
            # No LinkedIn found
            result.success = True  # Not finding a LinkedIn page is not an error
            result.result = None
            logger.info("No LinkedIn page found for project", project=project.project_name)
            
        except Exception as e:
            logger.enrichment_error(project.project_name, 'linkedin', e)
            result.success = False
            result.error = str(e)
        
        return result
    
    async def _find_linkedin_on_website(self, website_url: str) -> Optional[str]:
        """Find LinkedIn company page by scraping the project website"""
        try:
            # Try common pages that might contain social links
            pages_to_check = [
                website_url,
                f"{website_url.rstrip('/')}/about",
                f"{website_url.rstrip('/')}/team",
                f"{website_url.rstrip('/')}/contact",
                f"{website_url.rstrip('/')}/contact-us"
            ]
            
            for page_url in pages_to_check:
                try:
                    response = request_utils.get(page_url)
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for LinkedIn links
                        linkedin_links = soup.find_all('a', href=re.compile(r'linkedin\.com/company/', re.I))
                        
                        for link in linkedin_links:
                            href = link.get('href')
                            if href and self._is_valid_linkedin_company_url(href):
                                return href
                        
                        # Also check for LinkedIn links in the general social links extraction
                        social_links = text_utils.extract_social_links(soup, website_url)
                        if social_links.get('linkedin'):
                            return social_links['linkedin']
                
                except Exception as e:
                    logger.debug(f"Failed to check page for LinkedIn", url=page_url, error=str(e))
                    continue
            
            return None
            
        except Exception as e:
            logger.error("Failed to find LinkedIn on website", error=e, website=website_url)
            return None
    
    async def _find_linkedin_via_google_search(self, project_name: str) -> Optional[str]:
        """Find LinkedIn company page via Google search"""
        try:
            # Construct Google search query
            search_query = f'site:linkedin.com/company "{project_name}"'
            google_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
            
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': request_utils.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = request_utils.get(google_url, headers=headers)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for LinkedIn company URLs in search results
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    if href and 'linkedin.com/company/' in href:
                        # Extract the actual LinkedIn URL from Google's redirect
                        linkedin_url = self._extract_linkedin_url_from_google_result(href)
                        if linkedin_url and self._is_valid_linkedin_company_url(linkedin_url):
                            return linkedin_url
            
            return None
            
        except Exception as e:
            logger.error("Failed to find LinkedIn via Google search", error=e, project=project_name)
            return None
    
    def _extract_linkedin_url_from_google_result(self, google_url: str) -> Optional[str]:
        """Extract LinkedIn URL from Google search result link"""
        try:
            # Google search results often wrap URLs in redirects
            if 'linkedin.com/company/' in google_url:
                # Try to extract the LinkedIn URL
                match = re.search(r'(https?://[^/]*linkedin\.com/company/[^&\s]+)', google_url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    def _is_valid_linkedin_company_url(self, url: str) -> bool:
        """Check if URL is a valid LinkedIn company page"""
        try:
            if not url:
                return False
            
            # Must contain linkedin.com/company/
            if 'linkedin.com/company/' not in url.lower():
                return False
            
            # Should not be a personal profile
            if '/in/' in url.lower():
                return False
            
            # Should have a company name after /company/
            match = re.search(r'linkedin\.com/company/([^/?&]+)', url, re.I)
            if match:
                company_slug = match.group(1)
                # Company slug should be reasonable length and not empty
                return len(company_slug) > 1 and len(company_slug) < 100
            
            return False
            
        except Exception:
            return False

# Global LinkedIn enrichment service instance
linkedin_enrichment_service = LinkedInEnrichmentService()

