# Web3 Data Aggregator

An automated system for discovering, collecting, enriching, and storing information about new Web3 projects from multiple online sources.

## 🚀 Features

- **Multi-Source Data Collection**: Automatically scrapes data from 8 major Web3 platforms
- **Data Enrichment**: Finds business emails and LinkedIn company pages
- **Flexible Storage**: Supports both Google Sheets and Airtable
- **Deduplication**: Prevents duplicate entries based on website domains
- **Scheduling**: Configurable daily or weekly automated runs
- **Robust Error Handling**: Graceful handling of individual source failures
- **Anti-Bot Measures**: User-agent rotation and request delays

## 📊 Data Sources

1. **CryptoRank** - Funding rounds data via API
2. **ICO Drops** - ICO and token sale listings
3. **CoinMarketCap** - New cryptocurrency listings via API
4. **DappRadar** - New decentralized applications via API
5. **Zealy** - New Web3 communities
6. **DAO Maker** - Launchpad projects
7. **Polkastarter** - IDO platform projects
8. **DropsTab** - Token drops and airdrops (when available)

## 📋 Data Output Format

| Project | Website | Twitter | LinkedIn | Email | Source | Date Added |
|---------|---------|---------|----------|-------|--------|-------------|
| Project Name | https://... | https://twitter.com/... | https://linkedin.com/company/... | contact@... | Source URL | 2025-06-25 |

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- Google Service Account (for Google Sheets) OR Airtable account
- API keys for data sources and enrichment services

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd web3_data_aggregator
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Storage Configuration
STORAGE_TYPE=google_sheets  # Options: 'google_sheets' or 'airtable'
RUN_SCHEDULE=daily  # Options: 'daily' or 'weekly'

# Google Sheets Configuration (if using Google Sheets)
GOOGLE_SHEETS_KEY=/path/to/service-account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_SHEETS_SHEET_NAME=Sheet1

# Airtable Configuration (if using Airtable)
AIRTABLE_PAT=your-personal-access-token
AIRTABLE_BASE_ID=your-base-id
AIRTABLE_TABLE_NAME=Projects

# API Keys for Data Sources
HUNTER_IO_API_KEY=your-hunter-io-api-key
COINMARKETCAP_API_KEY=your-coinmarketcap-api-key
CRYPTORANK_API_KEY=your-cryptorank-api-key
DAPPRADAR_API_KEY=your-dappradar-api-key

# Email Enrichment Service
EMAIL_ENRICHMENT_SERVICE=hunter  # Options: 'hunter' or 'snov'
SNOV_IO_API_KEY=your-snov-io-api-key  # Only if using Snov.io
```

### Google Sheets Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API and Google Drive API
3. Create a Service Account and download the JSON key file
4. Share your Google Sheet with the service account email
5. Set `GOOGLE_SHEETS_KEY` to the path of your JSON key file

### Airtable Setup

1. Create an Airtable base
2. Create a table with the required columns
3. Generate a Personal Access Token (PAT)
4. Set the Airtable configuration variables

## 🚀 Usage

### Command Line Interface

```bash
# Run full aggregation process
python cli.py run

# Test all system components
python cli.py test

# Show current system status
python cli.py status

# Run scraping only (no enrichment or storage)
python cli.py scrape

# Enable verbose logging
python cli.py run --verbose
```

### Scheduler

```bash
# Start the scheduler (runs based on RUN_SCHEDULE config)
python scheduler.py start

# Run aggregation once immediately
python scheduler.py run-now

# Show scheduler status
python scheduler.py status
```

### Programmatic Usage

```python
from src.main import app

# Run full aggregation
result = await app.run_full_aggregation()

# Run individual components
projects = await app.run_scraping_only()
enriched = await app.run_enrichment_only(projects)

# Test system
test_results = await app.test_all_components()
```

## 📁 Project Structure

```
web3_data_aggregator/
├── src/
│   ├── scrapers/           # Data source scrapers
│   │   ├── base_scraper.py
│   │   ├── cryptorank_scraper.py
│   │   ├── icodrops_scraper.py
│   │   └── ...
│   ├── enrichment/         # Data enrichment services
│   │   ├── email_enrichment.py
│   │   └── linkedin_enrichment.py
│   ├── storage/           # Storage backends
│   │   ├── google_sheets_storage.py
│   │   └── airtable_storage.py
│   ├── utils/             # Utility functions and models
│   │   ├── models.py
│   │   ├── logger.py
│   │   └── helpers.py
│   ├── config.py          # Configuration management
│   └── main.py           # Main application
├── config/               # Configuration files
├── logs/                # Log files
├── cli.py               # Command-line interface
├── scheduler.py         # Automated scheduler
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 API Keys Required

### Data Sources
- **CoinMarketCap**: Free tier available at [coinmarketcap.com/api](https://coinmarketcap.com/api/)
- **CryptoRank**: API access at [cryptorank.io/api](https://cryptorank.io/api)
- **DappRadar**: API access at [dappradar.com/api](https://dappradar.com/api)

### Enrichment Services
- **Hunter.io**: Email finder API at [hunter.io](https://hunter.io/)
- **Snov.io**: Alternative email finder at [snov.io](https://snov.io/)

## 📊 Success Metrics

The system tracks the following metrics:

- **Data Accuracy**: >90% accuracy for extracted project names and websites
- **Data Completeness**: >95% of projects have required fields populated
- **Enrichment Rate**: 
  - LinkedIn: >60% of projects enriched
  - Email: >40% of projects enriched
- **System Uptime**: >95% of scheduled runs complete successfully
- **Deduplication**: <5% duplicate entries

## 🛡️ Error Handling

- **Graceful Degradation**: Individual scraper failures don't stop the entire process
- **Retry Logic**: Automatic retries with exponential backoff for transient errors
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Rate Limiting**: Respects API rate limits and implements delays

## 🔒 Security Features

- **Secure Credential Storage**: Environment variables and service account files
- **HTTPS Only**: All external communications use HTTPS
- **Anti-Bot Measures**: User-agent rotation and randomized delays
- **Input Validation**: Sanitization of scraped data

## 📈 Monitoring and Logging

Logs are stored in the `logs/` directory with the following information:

- Successful operations (data fetched, enriched, stored)
- Detailed errors with context
- Performance metrics
- Deduplication statistics

## 🚀 Deployment

### Local Development
```bash
# Run once
python cli.py run

# Start scheduler
python scheduler.py start
```

### Production Deployment

1. **Cloud Platforms**: Deploy on platforms like Render, Railway, or Replit
2. **Cron Jobs**: Set up system cron jobs for scheduling
3. **Docker**: Containerize for consistent deployment
4. **Environment Variables**: Use platform-specific secret management

### Example Cron Job
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/web3_data_aggregator && python cli.py run
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the logs in the `logs/` directory
2. Run `python cli.py test` to diagnose issues
3. Verify your API keys and configuration
4. Check the GitHub issues page

## 🔄 Updates and Maintenance

- **Regular Updates**: Keep dependencies updated
- **API Changes**: Monitor data source APIs for changes
- **Performance Optimization**: Regular performance reviews
- **Security Updates**: Keep security dependencies current

---

**Note**: This system is designed for legitimate business research and lead generation. Please respect the terms of service of all data sources and implement appropriate rate limiting.

