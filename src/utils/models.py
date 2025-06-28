"""
Data models for Web3 Data Aggregator
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urlparse

@dataclass
class ProjectData:
    """Data model for a Web3 project"""
    project_name: str
    website: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    date_added: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    
    def __post_init__(self):
        """Clean and validate data after initialization"""
        # Clean project name
        if self.project_name:
            self.project_name = self.project_name.strip()
        
        # Clean and validate URLs
        self.website = self._clean_url(self.website)
        self.twitter = self._clean_social_url(self.twitter, 'twitter.com')
        self.linkedin = self._clean_social_url(self.linkedin, 'linkedin.com')
        
        # Clean email
        if self.email:
            self.email = self.email.strip().lower()
    
    def _clean_url(self, url: Optional[str]) -> Optional[str]:
        """Clean and validate a URL"""
        if not url:
            return None
        
        url = url.strip()
        if not url:
            return None
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                return url
        except:
            pass
        
        return None
    
    def _clean_social_url(self, url: Optional[str], platform: str) -> Optional[str]:
        """Clean and validate social media URLs"""
        if not url:
            return None
        
        url = url.strip()
        if not url:
            return None
        
        # Handle @username format for Twitter
        if platform == 'twitter.com' and url.startswith('@'):
            url = f"https://twitter.com/{url[1:]}"
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            if platform in url:
                url = 'https://' + url
            else:
                # Assume it's a username
                if platform == 'twitter.com':
                    url = f"https://twitter.com/{url}"
                elif platform == 'linkedin.com':
                    url = f"https://linkedin.com/company/{url}"
        
        try:
            parsed = urlparse(url)
            if platform in parsed.netloc:
                return url
        except:
            pass
        
        return None
    
    def get_domain(self) -> Optional[str]:
        """Get the domain from the website URL for deduplication"""
        if not self.website:
            return None
        
        try:
            parsed = urlparse(self.website)
            domain = parsed.netloc.lower()
            # Remove www. prefix for better matching
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for storage"""
        return {
            'Project': self.project_name or '',
            'Website': self.website or '',
            'Twitter': self.twitter or '',
            'LinkedIn': self.linkedin or '',
            'Email': self.email or '',
            'Source': self.source or '',
            'Date Added': self.date_added
        }
    
    def is_valid(self) -> bool:
        """Check if the project has minimum required data"""
        return bool(self.project_name and (self.website or self.twitter))
    
    def __str__(self) -> str:
        return f"ProjectData(name='{self.project_name}', website='{self.website}')"
    
    def __repr__(self) -> str:
        return self.__str__()

@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    source: str
    projects: List[ProjectData] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
    
    def add_project(self, project: ProjectData):
        """Add a project to the result"""
        if project.is_valid():
            project.source = self.source
            self.projects.append(project)
    
    def get_project_count(self) -> int:
        """Get the number of valid projects"""
        return len(self.projects)

@dataclass
class EnrichmentResult:
    """Result of an enrichment operation"""
    project_name: str
    enrichment_type: str  # 'email' or 'linkedin'
    result: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

