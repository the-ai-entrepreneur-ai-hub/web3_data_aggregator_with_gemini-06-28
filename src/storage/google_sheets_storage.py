"""
Google Sheets storage module for Web3 Data Aggregator
"""
import gspread
from typing import List, Optional, Set
from google.oauth2.service_account import Credentials

from ..utils.models import ProjectData
from ..utils.logger import logger
from ..utils.helpers import dedup_utils
from ..config import config

class GoogleSheetsStorage:
    """Storage handler for Google Sheets"""
    
    def __init__(self):
        self.credentials_file = config.google_sheets_key
        self.spreadsheet_id = config.google_sheets_spreadsheet_id
        self.sheet_name = config.google_sheets_sheet_name
        self.client = None
        self.worksheet = None
        
        # Column headers as defined in the PRD
        self.headers = ['Project', 'Website', 'Twitter', 'LinkedIn', 'Email', 'Source', 'Date Added']
    
    async def initialize(self) -> bool:
        """Initialize Google Sheets connection"""
        try:
            # Set up credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # Create client
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet and worksheet
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            try:
                self.worksheet = spreadsheet.worksheet(self.sheet_name)
            except gspread.WorksheetNotFound:
                # Create worksheet if it doesn't exist
                self.worksheet = spreadsheet.add_worksheet(
                    title=self.sheet_name, 
                    rows=1000, 
                    cols=len(self.headers)
                )
            
            # Ensure headers are set
            await self._ensure_headers()
            
            logger.success("Google Sheets connection initialized", 
                         spreadsheet_id=self.spreadsheet_id,
                         sheet_name=self.sheet_name)
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Google Sheets connection", error=e)
            return False
    
    async def _ensure_headers(self):
        """Ensure the worksheet has the correct headers"""
        try:
            # Get first row
            first_row = self.worksheet.row_values(1)
            
            # If first row is empty or doesn't match headers, set headers
            if not first_row or first_row != self.headers:
                self.worksheet.update('A1', [self.headers])
                logger.info("Headers updated in Google Sheets")
            
        except Exception as e:
            logger.error("Failed to ensure headers", error=e)
    
    async def store_projects(self, projects: List[ProjectData]) -> tuple[int, int]:
        """Store projects in Google Sheets with deduplication"""
        if not self.worksheet:
            if not await self.initialize():
                raise Exception("Failed to initialize Google Sheets connection")
        
        logger.storage_start("Google Sheets", len(projects))
        
        try:
            # Get existing data for deduplication
            existing_domains = await self._get_existing_domains()
            existing_names = await self._get_existing_names()
            
            # Filter out duplicates
            new_projects = []
            skipped_count = 0
            
            for project in projects:
                if await self._is_duplicate(project, existing_domains, existing_names):
                    skipped_count += 1
                    logger.info("Skipping duplicate project", 
                               project=project.project_name,
                               domain=project.get_domain())
                else:
                    new_projects.append(project)
                    # Add to existing sets to prevent duplicates within this batch
                    if project.get_domain():
                        existing_domains.add(project.get_domain())
                    existing_names.add(dedup_utils.normalize_project_name(project.project_name))
            
            # Store new projects
            stored_count = 0
            if new_projects:
                rows_to_add = []
                for project in new_projects:
                    row_data = [
                        project.project_name or '',
                        project.website or '',
                        project.twitter or '',
                        project.linkedin or '',
                        project.email or '',
                        project.source or '',
                        project.date_added
                    ]
                    rows_to_add.append(row_data)
                
                # Append all rows at once for better performance
                self.worksheet.append_rows(rows_to_add)
                stored_count = len(rows_to_add)
                
                logger.success("Projects stored in Google Sheets", 
                             stored=stored_count,
                             skipped=skipped_count)
            
            logger.storage_success("Google Sheets", stored_count, skipped_count)
            return stored_count, skipped_count
            
        except Exception as e:
            logger.storage_error("Google Sheets", e)
            raise
    
    async def _get_existing_domains(self) -> Set[str]:
        """Get set of existing website domains for deduplication"""
        try:
            # Get all website URLs (column B)
            website_column = self.worksheet.col_values(2)  # Column B (Website)
            
            domains = set()
            for url in website_column[1:]:  # Skip header
                if url:
                    domain = dedup_utils.normalize_domain(url)
                    if domain:
                        domains.add(domain)
            
            return domains
            
        except Exception as e:
            logger.error("Failed to get existing domains", error=e)
            return set()
    
    async def _get_existing_names(self) -> Set[str]:
        """Get set of existing project names for deduplication"""
        try:
            # Get all project names (column A)
            name_column = self.worksheet.col_values(1)  # Column A (Project)
            
            names = set()
            for name in name_column[1:]:  # Skip header
                if name:
                    normalized_name = dedup_utils.normalize_project_name(name)
                    names.add(normalized_name)
            
            return names
            
        except Exception as e:
            logger.error("Failed to get existing names", error=e)
            return set()
    
    async def _is_duplicate(self, project: ProjectData, existing_domains: Set[str], existing_names: Set[str]) -> bool:
        """Check if project is a duplicate"""
        # Check domain-based deduplication (primary)
        domain = project.get_domain()
        if domain and domain in existing_domains:
            return True
        
        # Check name-based deduplication (secondary)
        normalized_name = dedup_utils.normalize_project_name(project.project_name)
        if normalized_name in existing_names:
            return True
        
        return False
    
    async def get_project_count(self) -> int:
        """Get total number of projects in the sheet"""
        try:
            if not self.worksheet:
                if not await self.initialize():
                    return 0
            
            # Get all values and count non-empty rows (excluding header)
            all_values = self.worksheet.get_all_values()
            return len(all_values) - 1 if all_values else 0
            
        except Exception as e:
            logger.error("Failed to get project count", error=e)
            return 0
    
    async def test_connection(self) -> bool:
        """Test the Google Sheets connection"""
        try:
            return await self.initialize()
        except Exception as e:
            logger.error("Google Sheets connection test failed", error=e)
            return False

# Global Google Sheets storage instance
google_sheets_storage = GoogleSheetsStorage()

