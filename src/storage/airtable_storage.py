"""
Airtable storage module for Web3 Data Aggregator
"""
from pyairtable import Api
from typing import List, Optional, Set, Dict, Any

from ..utils.models import ProjectData
from ..utils.logger import logger
from ..utils.helpers import dedup_utils
from ..config import config

class AirtableStorage:
    """Storage handler for Airtable"""
    
    def __init__(self):
        self.personal_access_token = config.airtable_pat
        self.base_id = config.airtable_base_id
        self.table_name = config.airtable_table_name
        self.api = None
        self.table = None
        
        # Field mapping for Airtable
        self.field_mapping = {
            'Project': 'Project',
            'Website': 'Website', 
            'Twitter': 'Twitter',
            'LinkedIn': 'LinkedIn',
            'Email': 'Email',
            'Source': 'Source',
            'Date Added': 'Date Added'
        }
    
    async def initialize(self) -> bool:
        """Initialize Airtable connection"""
        try:
            # Create API client
            self.api = Api(self.personal_access_token)
            
            # Get table
            self.table = self.api.table(self.base_id, self.table_name)
            
            # Test connection by getting table info
            table_info = self.table.schema()
            
            logger.success("Airtable connection initialized", 
                         base_id=self.base_id,
                         table_name=self.table_name)
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Airtable connection", error=e)
            return False
    
    async def store_projects(self, projects: List[ProjectData]) -> tuple[int, int]:
        """Store projects in Airtable with deduplication"""
        if not self.table:
            if not await self.initialize():
                raise Exception("Failed to initialize Airtable connection")
        
        logger.storage_start("Airtable", len(projects))
        
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
                records_to_create = []
                for project in new_projects:
                    record_data = {
                        self.field_mapping['Project']: project.project_name or '',
                        self.field_mapping['Website']: project.website or '',
                        self.field_mapping['Twitter']: project.twitter or '',
                        self.field_mapping['LinkedIn']: project.linkedin or '',
                        self.field_mapping['Email']: project.email or '',
                        self.field_mapping['Source']: project.source or '',
                        self.field_mapping['Date Added']: project.date_added
                    }
                    records_to_create.append(record_data)
                
                # Create records in batches (Airtable has a limit of 10 records per batch)
                batch_size = 10
                for i in range(0, len(records_to_create), batch_size):
                    batch = records_to_create[i:i + batch_size]
                    self.table.batch_create(batch)
                    stored_count += len(batch)
                
                logger.success("Projects stored in Airtable", 
                             stored=stored_count,
                             skipped=skipped_count)
            
            logger.storage_success("Airtable", stored_count, skipped_count)
            return stored_count, skipped_count
            
        except Exception as e:
            logger.storage_error("Airtable", e)
            raise
    
    async def _get_existing_domains(self) -> Set[str]:
        """Get set of existing website domains for deduplication"""
        try:
            # Get all records
            records = self.table.all()
            
            domains = set()
            for record in records:
                website = record['fields'].get(self.field_mapping['Website'], '')
                if website:
                    domain = dedup_utils.normalize_domain(website)
                    if domain:
                        domains.add(domain)
            
            return domains
            
        except Exception as e:
            logger.error("Failed to get existing domains", error=e)
            return set()
    
    async def _get_existing_names(self) -> Set[str]:
        """Get set of existing project names for deduplication"""
        try:
            # Get all records
            records = self.table.all()
            
            names = set()
            for record in records:
                project_name = record['fields'].get(self.field_mapping['Project'], '')
                if project_name:
                    normalized_name = dedup_utils.normalize_project_name(project_name)
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
        """Get total number of projects in the table"""
        try:
            if not self.table:
                if not await self.initialize():
                    return 0
            
            # Get all records and count them
            records = self.table.all()
            return len(records)
            
        except Exception as e:
            logger.error("Failed to get project count", error=e)
            return 0
    
    async def test_connection(self) -> bool:
        """Test the Airtable connection"""
        try:
            return await self.initialize()
        except Exception as e:
            logger.error("Airtable connection test failed", error=e)
            return False

# Global Airtable storage instance
airtable_storage = AirtableStorage()

