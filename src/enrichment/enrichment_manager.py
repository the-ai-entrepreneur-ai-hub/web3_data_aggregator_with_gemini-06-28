"""
Enrichment manager for Web3 Data Aggregator
"""
import asyncio
from typing import List

from .email_enrichment import email_enrichment_service
from .linkedin_enrichment import linkedin_enrichment_service
from ..utils.models import ProjectData, EnrichmentResult
from ..utils.logger import logger

class EnrichmentManager:
    """Manages all enrichment services and coordinates the enrichment process"""
    
    def __init__(self):
        self.email_service = email_enrichment_service
        self.linkedin_service = linkedin_enrichment_service
        self.max_concurrent_enrichments = 5  # Limit concurrent enrichments
    
    async def enrich_projects(self, projects: List[ProjectData]) -> List[ProjectData]:
        """Enrich all projects with additional data"""
        logger.info("Starting enrichment process", total_projects=len(projects))
        
        enriched_projects = []
        successful_enrichments = 0
        failed_enrichments = 0
        
        # Process projects in batches to avoid overwhelming APIs
        for i in range(0, len(projects), self.max_concurrent_enrichments):
            batch = projects[i:i + self.max_concurrent_enrichments]
            
            # Enrich projects in this batch
            batch_results = await self._enrich_project_batch(batch)
            enriched_projects.extend(batch_results)
            
            # Count successes and failures
            for project in batch_results:
                if project.email or project.linkedin:
                    successful_enrichments += 1
                else:
                    failed_enrichments += 1
            
            # Add delay between batches to respect API rate limits
            if i + self.max_concurrent_enrichments < len(projects):
                await asyncio.sleep(2)
        
        logger.info("Enrichment process completed", 
                   total_projects=len(enriched_projects),
                   successful_enrichments=successful_enrichments,
                   failed_enrichments=failed_enrichments)
        
        return enriched_projects
    
    async def _enrich_project_batch(self, projects: List[ProjectData]) -> List[ProjectData]:
        """Enrich a batch of projects concurrently"""
        tasks = []
        
        for project in projects:
            task = asyncio.create_task(self._enrich_single_project(project))
            tasks.append(task)
        
        # Wait for all enrichments in the batch to complete
        enriched_projects = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_projects = []
        for i, result in enumerate(enriched_projects):
            if isinstance(result, Exception):
                logger.error("Project enrichment failed", error=result, project=projects[i].project_name)
                # Return original project if enrichment failed
                processed_projects.append(projects[i])
            else:
                processed_projects.append(result)
        
        return processed_projects
    
    async def _enrich_single_project(self, project: ProjectData) -> ProjectData:
        """Enrich a single project with email and LinkedIn data"""
        try:
            # Create a copy of the project to avoid modifying the original
            enriched_project = ProjectData(
                project_name=project.project_name,
                website=project.website,
                twitter=project.twitter,
                linkedin=project.linkedin,
                email=project.email,
                source=project.source,
                date_added=project.date_added
            )
            
            # Run email and LinkedIn enrichment concurrently
            email_task = asyncio.create_task(self._enrich_email(enriched_project))
            linkedin_task = asyncio.create_task(self._enrich_linkedin(enriched_project))
            
            email_result, linkedin_result = await asyncio.gather(
                email_task, linkedin_task, return_exceptions=True
            )
            
            # Apply email enrichment result
            if not isinstance(email_result, Exception) and email_result.success and email_result.result:
                enriched_project.email = email_result.result
            
            # Apply LinkedIn enrichment result
            if not isinstance(linkedin_result, Exception) and linkedin_result.success and linkedin_result.result:
                enriched_project.linkedin = linkedin_result.result
            
            return enriched_project
            
        except Exception as e:
            logger.error("Failed to enrich project", error=e, project=project.project_name)
            return project
    
    async def _enrich_email(self, project: ProjectData) -> EnrichmentResult:
        """Enrich project with email data"""
        try:
            # Skip if email already exists
            if project.email:
                result = EnrichmentResult(
                    project_name=project.project_name,
                    enrichment_type='email'
                )
                result.success = True
                result.result = project.email
                return result
            
            return await self.email_service.enrich_project_email(project)
            
        except Exception as e:
            logger.error("Email enrichment failed", error=e, project=project.project_name)
            result = EnrichmentResult(
                project_name=project.project_name,
                enrichment_type='email'
            )
            result.success = False
            result.error = str(e)
            return result
    
    async def _enrich_linkedin(self, project: ProjectData) -> EnrichmentResult:
        """Enrich project with LinkedIn data"""
        try:
            # Skip if LinkedIn already exists
            if project.linkedin:
                result = EnrichmentResult(
                    project_name=project.project_name,
                    enrichment_type='linkedin'
                )
                result.success = True
                result.result = project.linkedin
                return result
            
            return await self.linkedin_service.enrich_project_linkedin(project)
            
        except Exception as e:
            logger.error("LinkedIn enrichment failed", error=e, project=project.project_name)
            result = EnrichmentResult(
                project_name=project.project_name,
                enrichment_type='linkedin'
            )
            result.success = False
            result.error = str(e)
            return result
    
    async def enrich_single_project_full(self, project: ProjectData) -> ProjectData:
        """Enrich a single project with all available enrichment services"""
        return await self._enrich_single_project(project)

# Global enrichment manager instance
enrichment_manager = EnrichmentManager()

