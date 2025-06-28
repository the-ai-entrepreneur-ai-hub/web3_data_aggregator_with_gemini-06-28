"""
Logging utilities for Web3 Data Aggregator
"""
import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Custom logger for the Web3 Data Aggregator"""
    
    def __init__(self, name: str = "web3_aggregator"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler
        log_file = os.path.join(log_dir, f"aggregator_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        self.logger.info(full_message)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception and context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        
        if error:
            full_message += f" | Error: {str(error)}"
        
        self.logger.error(full_message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        self.logger.warning(full_message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        self.logger.debug(full_message)
    
    def success(self, message: str, **kwargs):
        """Log successful operation"""
        self.info(f"SUCCESS: {message}", **kwargs)
    
    def scraping_start(self, source: str, url: str):
        """Log start of scraping operation"""
        self.info("Starting scraping operation", source=source, url=url)
    
    def scraping_success(self, source: str, projects_found: int):
        """Log successful scraping operation"""
        self.success("Scraping completed", source=source, projects_found=projects_found)
    
    def scraping_error(self, source: str, error: Exception, url: str = None):
        """Log scraping error"""
        self.error("Scraping failed", error=error, source=source, url=url)
    
    def enrichment_start(self, project_name: str, enrichment_type: str):
        """Log start of enrichment operation"""
        self.info("Starting enrichment", project=project_name, type=enrichment_type)
    
    def enrichment_success(self, project_name: str, enrichment_type: str, result: str):
        """Log successful enrichment"""
        self.success("Enrichment completed", project=project_name, type=enrichment_type, result=result)
    
    def enrichment_error(self, project_name: str, enrichment_type: str, error: Exception):
        """Log enrichment error"""
        self.error("Enrichment failed", error=error, project=project_name, type=enrichment_type)
    
    def storage_start(self, storage_type: str, project_count: int):
        """Log start of storage operation"""
        self.info("Starting data storage", storage_type=storage_type, project_count=project_count)
    
    def storage_success(self, storage_type: str, stored_count: int, skipped_count: int):
        """Log successful storage operation"""
        self.success("Data storage completed", 
                    storage_type=storage_type, 
                    stored=stored_count, 
                    skipped=skipped_count)
    
    def storage_error(self, storage_type: str, error: Exception):
        """Log storage error"""
        self.error("Data storage failed", error=error, storage_type=storage_type)
    
    def run_start(self):
        """Log start of full aggregation run"""
        self.info("=" * 50)
        self.info("Starting Web3 Data Aggregation Run")
        self.info("=" * 50)
    
    def run_complete(self, total_projects: int, new_projects: int, duration: float):
        """Log completion of full aggregation run"""
        self.info("=" * 50)
        self.success("Web3 Data Aggregation Run Completed", 
                    total_projects=total_projects,
                    new_projects=new_projects,
                    duration_seconds=round(duration, 2))
        self.info("=" * 50)
    
    def run_error(self, error: Exception):
        """Log critical run error"""
        self.error("CRITICAL: Aggregation run failed", error=error)

# Global logger instance
logger = Logger()

