# 🚀 Setup Guide - Get Started in 5 Minutes

Complete step-by-step guide to set up the Legal Lead Generation Engine.

## Quick Start (TL;DR)

```bash
# 1. Clone and navigate
cd Lead-Engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run setup wizard
python src/setup_wizard.py

# 4. Extract your first 100 leads
python src/examples/quick_demo.py
```

That's it! You now have real company data extracted legally and for free.

---

## Detailed Setup

### Prerequisites

#### Required
- **Python 3.8+** (check with `python --version`)
- **pip** (Python package installer)
- **Internet connection**

#### Optional
- Git (for cloning repository)
- Virtual environment (recommended)

### Step 1: Environment Setup

#### Option A: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Option B: System-Wide Install

```bash
# Just install directly (not recommended)
pip install -r requirements.txt
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**Packages installed:**
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation
- `rich` - Beautiful console output
- `google-generativeai` - Google AI Studio (optional)
- `groq` - Groq API (optional)
- And more...

**Installation time**: 1-2 minutes

### Step 3: Configure Free APIs (Optional but Recommended)

AI enrichment is optional but highly recommended. All APIs are FREE.

#### Google AI Studio (Gemini)

**Free Tier**: 1 million tokens/day

**Setup:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

**Add to .env file:**
```bash
echo "GOOGLE_AI_API_KEY=your-key-here" >> .env
```

#### Groq (Fast Inference)

**Free Tier**: 14,400 requests/day

**Setup:**
1. Visit https://console.groq.com/keys
2. Sign up (free)
3. Create API key
4. Copy the key

**Add to .env file:**
```bash
echo "GROQ_API_KEY=your-key-here" >> .env
```

#### Together AI (Optional)

**Free Tier**: $25 free credits

**Setup:**
1. Visit https://api.together.xyz/signup
2. Sign up
3. Get API key from dashboard

**Add to .env file:**
```bash
echo "TOGETHER_API_KEY=your-key-here" >> .env
```

### Step 4: Create Data Directories

```bash
mkdir -p data/raw data/processed results
```

### Step 5: Test Installation

```bash
# Run quick test
python src/examples/quick_demo.py
```

**What this does:**
1. Extracts 20 companies from SEC EDGAR
2. Extracts 10 companies from OpenCorporates
3. Extracts 20 federal contractors
4. Tests AI enrichment (if configured)
5. Exports data to CSV

**Expected output:**
```
🎯 LEGAL LEAD GENERATION ENGINE - LIVE DEMO
============================================================

📊 STEP 1: SEC EDGAR - Public Companies
Extracting technology companies from SEC filings...
✅ Extracted 20 public companies

🌍 STEP 2: OpenCorporates - International Companies
✅ Extracted 10 international companies

🏛️  STEP 3: USASpending - Federal Contractors
✅ Extracted 20 federal contractors

📊 Total Leads Extracted: 50
💰 Total Cost: $0.00
⚖️  Legal Compliance: 100%
```

---

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```bash
# AI APIs (Optional - for enrichment)
GOOGLE_AI_API_KEY=your-google-ai-key
GROQ_API_KEY=your-groq-key
TOGETHER_API_KEY=your-together-key

# OpenCorporates (Optional - for higher rate limits)
OPENCORPORATES_API_TOKEN=your-token

# User Agent (Required for SEC EDGAR)
USER_EMAIL=your-email@example.com
```

### Configuration File (config.yaml)

Optional: Create `config.yaml` for custom settings:

```yaml
extractors:
  sec_edgar:
    rate_limit: 5  # requests per second
    default_count: 100

  opencorporates:
    rate_limit: 1
    default_count: 50

  usaspending:
    rate_limit: 2
    min_contract_value: 100000

enrichment:
  enabled: true
  api_priority:
    - google_ai_studio
    - groq
    - together_ai

output:
  format: csv
  directory: data/processed
```

---

## Usage Examples

### Extract Tech Companies from SEC

```python
from extractors.sec_edgar_extractor import SECEdgarExtractor

extractor = SECEdgarExtractor(user_agent_email="your@email.com")

# Get 100 software companies
companies = extractor.extract_leads(
    count=100,
    sic_codes=['7372']  # Prepackaged Software
)

# Export to CSV
extractor.export_to_csv(companies, 'tech_companies.csv')
```

### Extract Federal Contractors

```python
from extractors.datagov_extractor import DataGovExtractor

extractor = DataGovExtractor()

# Get IT contractors with $1M+ contracts
contractors = extractor.extract_leads(
    industry="541512",  # Computer Systems Design
    min_value=1000000,
    count=100
)
```

### Extract International Companies

```python
from extractors.opencorporates_extractor import OpenCorporatesExtractor

extractor = OpenCorporatesExtractor()

# Get UK tech companies
uk_companies = extractor.extract_leads(
    country="gb",
    query="software technology",
    count=50
)
```

### Enrich Leads with AI

```python
from processors.free_api_manager import FreeAPIManager

manager = FreeAPIManager()

# Enrich your leads
enriched_leads = manager.enrich_leads_batch(companies)

# Check costs (should be $0)
cost_report = manager.get_cost_report()
print(f"Total cost: ${cost_report['total_cost']}")  # $0.00
```

---

## Verification

### Test SEC EDGAR Connection

```python
import requests

response = requests.get("https://www.sec.gov/files/company_tickers.json")
print(f"Status: {response.status_code}")  # Should be 200
print(f"Companies: {len(response.json())}")  # Should be 8000+
```

### Test OpenCorporates API

```python
import requests

response = requests.get("https://api.opencorporates.com/v0.4/companies/search?q=google")
print(f"Status: {response.status_code}")  # Should be 200
```

### Test USASpending API

```python
import requests

response = requests.post(
    "https://api.usaspending.gov/api/v2/search/spending_by_award",
    json={"limit": 1}
)
print(f"Status: {response.status_code}")  # Should be 200
```

---

## Troubleshooting

### "Module not found" Error

```bash
# Make sure you're in the right directory
cd Lead-Engine

# Reinstall dependencies
pip install -r requirements.txt
```

### "Rate limit exceeded" Error

**Solution**: The free extractors have rate limits:
- SEC EDGAR: 10 requests/second (we use 5)
- OpenCorporates: 200 calls/day free
- USASpending: No limit

Wait a bit and try again, or configure API keys for higher limits.

### "No API key" Warning

**Solution**: AI enrichment requires API keys. Either:
1. Set up free API keys (see Step 3)
2. Run without enrichment (still works fine)

### SSL/Certificate Errors

```bash
# Update certificates
pip install --upgrade certifi

# Or use system certificates
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```

### Import Errors

```bash
# Make sure __init__.py files exist
touch src/__init__.py
touch src/extractors/__init__.py
touch src/processors/__init__.py
```

---

## Next Steps

Once setup is complete:

1. **Run the demo**: `python src/examples/quick_demo.py`
2. **Read data sources guide**: `docs/SOURCES.md`
3. **Understand legal compliance**: `docs/LEGAL.md`
4. **Customize extractors** for your target market
5. **Scale up** to 1000s of leads/day

---

## Production Deployment

### For Local Use

Just run the extractors on your machine. They're designed for local use.

### For Cloud Deployment

1. **Heroku/Railway/Render** (all have free tiers)
   ```bash
   # Add Procfile
   echo "worker: python src/main.py" > Procfile

   # Deploy
   git push heroku main
   ```

2. **Google Colab** (free GPU for enrichment)
   - Upload notebook
   - Install requirements
   - Run extractors

3. **GitHub Actions** (free automation)
   - Schedule daily extraction
   - Export to Google Sheets
   - Send email reports

See `docs/DEPLOYMENT.md` for detailed instructions.

---

## Support

### Getting Help

1. Check `docs/TROUBLESHOOTING.md`
2. Review `docs/LEGAL.md` for compliance questions
3. See `docs/SOURCES.md` for data source details

### Common Issues

**Problem**: Extraction is slow
**Solution**: Normal. Be respectful of rate limits. SEC EDGAR can handle 5 req/sec.

**Problem**: Not enough leads
**Solution**: Broaden your search criteria or use multiple sources.

**Problem**: Need more data fields
**Solution**: Combine with paid services (Hunter.io, Clearbit) or web research.

---

## What's Next?

You're now ready to:
- ✅ Extract 1000s of legal leads
- ✅ Enrich data with free AI
- ✅ Export to your CRM
- ✅ Build automated pipelines
- ✅ Scale to production

**All for $0.00 and 100% legally!**
