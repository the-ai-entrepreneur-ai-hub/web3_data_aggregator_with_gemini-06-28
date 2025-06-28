#!/usr/bin/env python3
"""
Command-line interface for Web3 Data Aggregator
"""
import asyncio
import argparse
import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.main import app
from src.utils.logger import logger
from src.config import config

async def run_aggregation():
    """Run the full aggregation process"""
    print("Starting Web3 Data Aggregation...")
    print(f"Storage: {config.storage_type}")
    print(f"Schedule: {config.run_schedule}")
    print("-" * 50)
    
    result = await app.run_full_aggregation()
    
    print("\n" + "=" * 50)
    print("AGGREGATION RESULTS")
    print("=" * 50)
    
    if result['success']:
        print(f"Status: SUCCESS")
        print(f"Total Projects Processed: {result['total_projects']}")
        print(f"🆕 New Projects Added: {result['new_projects']}")
        print(f"Duplicate Projects Skipped: {result.get('skipped_projects', 0)}")
        print(f"💾 Storage Type: {result.get('storage_type', 'Unknown')}")
        print(f"Duration: {result['duration']:.2f} seconds")
    else:
        print(f"Status: FAILED")
        print(f"Error: {result['error']}")
        print(f"Duration: {result['duration']:.2f} seconds")
    
    print("=" * 50)
    return result['success']

async def test_system():
    """Test all system components"""
    print("Testing Web3 Data Aggregator Components...")
    print("-" * 50)
    
    results = await app.test_all_components()
    
    print("\n" + "=" * 50)
    print("🧪 TEST RESULTS")
    print("=" * 50)
    
    print(f"Configuration: {'PASS' if results['config'] else 'FAIL'}")
    print(f"Storage: {'PASS' if results['storage'] else 'FAIL'}")
    print(f"Enrichment: {'PASS' if results['enrichment'] else 'FAIL'}")
    
    print("\n📡 Scrapers:")
    for scraper, passed in results['scrapers'].items():
        status = 'PASS' if passed else 'FAIL'
        print(f"   {scraper}: {status}")
    
    print("=" * 50)
    
    # Return True if all critical components pass
    critical_pass = results['config'] and results['storage']
    return critical_pass

async def show_status():
    """Show current system status"""
    print("Web3 Data Aggregator Status")
    print("-" * 50)
    
    status = await app.get_system_status()
    
    if 'error' in status:
        print(f"❌ Error: {status['error']}")
        return False
    
    print(f"💾 Storage Type: {status['storage_type']}")
    print(f"Total Projects: {status['total_projects']}")
    print(f"Config Valid: {'Yes' if status['config_valid'] else 'No'}")
    
    print(f"\n📡 Enabled Scrapers ({len(status['enabled_scrapers'])}):")
    for scraper in status['enabled_scrapers']:
        print(f"   {scraper}")
    
    disabled_scrapers = set(status['available_scrapers']) - set(status['enabled_scrapers'])
    if disabled_scrapers:
        print(f"\n📡 Disabled Scrapers ({len(disabled_scrapers)}):")
        for scraper in disabled_scrapers:
            print(f"   {scraper}")
    
    print("-" * 50)
    return True

async def run_scraping_only():
    """Run only the scraping process"""
    print("Running Scraping Only...")
    print("-" * 50)
    
    projects = await app.run_scraping_only()
    
    print(f"\nScraped {len(projects)} projects")
    
    # Show summary by source
    source_counts = {}
    for project in projects:
        source = project.source or 'Unknown'
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print("\nProjects by Source:")
    for source, count in source_counts.items():
        print(f"   {source}: {count}")
    
    return len(projects) > 0

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Web3 Data Aggregator - Automated Web3 project data collection and enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py run                 # Run full aggregation process
  python cli.py test                # Test all system components
  python cli.py status              # Show current system status
  python cli.py scrape              # Run scraping only
        """
    )
    
    parser.add_argument(
        'command',
        choices=['run', 'test', 'status', 'scrape'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the appropriate command
    try:
        if args.command == 'run':
            success = asyncio.run(run_aggregation())
        elif args.command == 'test':
            success = asyncio.run(test_system())
        elif args.command == 'status':
            success = asyncio.run(show_status())
        elif args.command == 'scrape':
            success = asyncio.run(run_scraping_only())
        else:
            print(f"Unknown command: {args.command}")
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logger.error("CLI error", error=e)
        sys.exit(1)

if __name__ == "__main__":
    main()

