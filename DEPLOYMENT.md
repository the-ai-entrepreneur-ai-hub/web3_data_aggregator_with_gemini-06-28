# Web3 Data Aggregator - Deployment Guide

## 🚀 Quick Start

### 1. System Requirements
- Python 3.11 or higher
- 2GB RAM minimum
- Internet connection
- Google Service Account (for Google Sheets) OR Airtable account

### 2. Installation Steps

```bash
# 1. Navigate to the project directory
cd web3_data_aggregator

# 2. Create virtual environment
python3.11 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
playwright install

# 6. Configure environment variables
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

### 3. Configuration

Edit the `.env` file with your actual values:

```env
# Storage Configuration
STORAGE_TYPE=google_sheets  # or 'airtable'
RUN_SCHEDULE=daily  # or 'weekly'

# Google Sheets (if using)
GOOGLE_SHEETS_KEY=/path/to/your/service-account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_SHEETS_SHEET_NAME=Sheet1

# API Keys (provided in your configuration)
HUNTER_IO_API_KEY=9fad732f490631c79f6701587358b4d42e4a5db2
COINMARKETCAP_API_KEY=1340d162-d090-44ef-8315-a1bff07031b2
CRYPTORANK_API_KEY=b87b77b0608115de1457334bfe34735bcdd17f518760d97b30645e974fa4
DAPPRADAR_API_KEY=NbzkSsvlIF28xHpEKa4Ni26Enkd3IOLX4PxEjwMU
```

### 4. Test the System

```bash
# Test all components
python cli.py test

# Check system status
python cli.py status
```

### 5. Run the Application

```bash
# Run once immediately
python cli.py run

# Start automated scheduler
python scheduler.py start

# Run scraping only (for testing)
python cli.py scrape
```

## 📊 Google Sheets Setup

Your Google Sheets is already configured with:
- **Spreadsheet ID**: `1yGyn18aBWH5cqLcp41AbNm_VF8Q7ndKxlYlqqFEGxOk`
- **Service Account**: `lead-intelligence-bot@lead-intelligence-platform.iam.gserviceaccount.com`

The service account credentials are already included in `config/google_service_account.json`.

## 🔑 API Keys Included

All necessary API keys are pre-configured:
- ✅ Hunter.io (Email enrichment)
- ✅ CoinMarketCap (New coins data)
- ✅ CryptoRank (Funding rounds)
- ✅ DappRadar (New dapps)

## 🕐 Scheduling Options

### Option 1: Built-in Scheduler
```bash
python scheduler.py start
```

### Option 2: System Cron Job
```bash
# Edit crontab
crontab -e

# Add daily run at 9 AM
0 9 * * * cd /path/to/web3_data_aggregator && source venv/bin/activate && python cli.py run

# Add weekly run on Monday at 9 AM
0 9 * * 1 cd /path/to/web3_data_aggregator && source venv/bin/activate && python cli.py run
```

## 🌐 Cloud Deployment

### Render.com
1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Use `python scheduler.py start` as the start command

### Railway.app
1. Connect repository
2. Add environment variables
3. Deploy with automatic scheduling

### Replit
1. Import project
2. Set secrets (environment variables)
3. Use the built-in scheduler

## 📈 Monitoring

### Logs
- Check `logs/` directory for detailed logs
- Logs are rotated daily
- Include success/failure information

### Status Checking
```bash
# Check current status
python cli.py status

# View scheduler status
python scheduler.py status
```

## 🔧 Troubleshooting

### Common Issues

1. **Google Sheets Permission Error**
   - Ensure the service account email has edit access to your sheet
   - Check that the spreadsheet ID is correct

2. **API Rate Limits**
   - The system includes built-in delays and rate limiting
   - If you hit limits, increase delays in config

3. **Playwright Browser Issues**
   - Run `playwright install` again
   - Check system dependencies

4. **Memory Issues**
   - Reduce concurrent scrapers in scraper_manager.py
   - Increase system memory if possible

### Debug Commands
```bash
# Verbose logging
python cli.py run --verbose

# Test individual components
python cli.py test

# Check configuration
python cli.py status
```

## 📊 Expected Results

The system will:
- ✅ Scrape 7 major Web3 data sources
- ✅ Find 20-100+ new projects per run
- ✅ Enrich 40-60% with email addresses
- ✅ Enrich 60%+ with LinkedIn pages
- ✅ Prevent duplicates automatically
- ✅ Store data in your Google Sheet

## 🔄 Maintenance

### Regular Tasks
- Monitor logs for errors
- Update API keys if they expire
- Check for new data sources
- Review and clean duplicate data

### Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Playwright browsers
playwright install
```

## 📞 Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Run `python cli.py test` to diagnose
3. Verify API keys and configuration
4. Check Google Sheets permissions

---

**Your Web3 Data Aggregator is ready to use! 🚀**

