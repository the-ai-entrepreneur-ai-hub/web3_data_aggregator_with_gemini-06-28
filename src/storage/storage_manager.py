"""
Storage manager for Web3 Data Aggregator
"""
from typing import List, Protocol

from .google_sheets_storage import google_sheets_storage
from .airtable_storage import airtable_storage
from ..utils.models import ProjectData
from ..utils.logger import logger
from ..config import config

class StorageInterface(Protocol):
    """Protocol for storage implementations"""
    
    async def initialize(self) -> bool:
        """Initialize storage connection"""
        ...
    
    async def store_projects(self, projects: List[ProjectData]) -> tuple[int, int]:
        """Store projects and return (stored_count, skipped_count)"""
        ...
    
    async def get_project_count(self) -> int:
        """Get total number of projects"""
        ...
    
    async def test_connection(self) -> bool:
        """Test storage connection"""
        ...

class StorageManager:
    """Manages storage operations and coordinates between different storage backends"""
    
    def __init__(self):
        self.storage_type = config.storage_type
        self.storage_backend: StorageInterface = self._get_storage_backend()
    
    def _get_storage_backend(self) -> StorageInterface:
        """Get the appropriate storage backend based on configuration"""
        if self.storage_type == 'google_sheets':
            return google_sheets_storage
        elif self.storage_type == 'airtable':
            return airtable_storage
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    async def initialize(self) -> bool:
        """Initialize the storage backend"""
        try:
            logger.info("Initializing storage backend", storage_type=self.storage_type)
            success = await self.storage_backend.initialize()
            
            if success:
                logger.success("Storage backend initialized", storage_type=self.storage_type)
            else:
                logger.error("Failed to initialize storage backend", storage_type=self.storage_type)
            
            return success
            
        except Exception as e:
            logger.error("Storage initialization failed", error=e, storage_type=self.storage_type)
            return False
    
    async def store_projects(self, projects: List[ProjectData]) -> tuple[int, int]:
        """Store projects using the configured storage backend"""
        if not projects:
            logger.info("No projects to store")
            return 0, 0
        
        try:
            logger.info("Starting project storage", 
                       project_count=len(projects),
                       storage_type=self.storage_type)
            
            stored_count, skipped_count = await self.storage_backend.store_projects(projects)
            
            logger.success("Project storage completed", 
                         stored=stored_count,
                         skipped=skipped_count,
                         storage_type=self.storage_type)
            
            return stored_count, skipped_count
            
        except Exception as e:
            logger.error("Project storage failed", error=e, storage_type=self.storage_type)
            raise
    
    async def get_project_count(self) -> int:
        """Get total number of projects in storage"""
        try:
            count = await self.storage_backend.get_project_count()
            logger.info("Retrieved project count", count=count, storage_type=self.storage_type)
            return count
            
        except Exception as e:
            logger.error("Failed to get project count", error=e, storage_type=self.storage_type)
            return 0
    
    async def test_connection(self) -> bool:
        """Test the storage connection"""
        try:
            logger.info("Testing storage connection", storage_type=self.storage_type)
            success = await self.storage_backend.test_connection()
            
            if success:
                logger.success("Storage connection test passed", storage_type=self.storage_type)
            else:
                logger.error("Storage connection test failed", storage_type=self.storage_type)
            
            return success
            
        except Exception as e:
            logger.error("Storage connection test error", error=e, storage_type=self.storage_type)
            return False
    
    def get_storage_type(self) -> str:
        """Get the current storage type"""
        return self.storage_type
    
    def switch_storage_backend(self, new_storage_type: str) -> bool:
        """Switch to a different storage backend"""
        try:
            if new_storage_type not in ['google_sheets', 'airtable']:
                logger.error("Invalid storage type", storage_type=new_storage_type)
                return False
            
            old_type = self.storage_type
            self.storage_type = new_storage_type
            self.storage_backend = self._get_storage_backend()
            
            logger.info("Switched storage backend", 
                       from_type=old_type,
                       to_type=new_storage_type)
            
            return True
            
        except Exception as e:
            logger.error("Failed to switch storage backend", error=e, storage_type=new_storage_type)
            return False

# Global storage manager instance
storage_manager = StorageManager()

