# 🎯 Targeted Lead Generation Guide

Extract leads from **specific geographies** and **specific industries** with precision.

## Target Markets

### Geographies
- 🇮🇳 **India** - Major cities: Mumbai, Bangalore, Delhi, Chennai, Hyderabad
- 🇺🇸 **United States** - All states, focus on major business hubs
- 🇪🇺 **Europe** - UK, Germany, France, Netherlands, Ireland
- 🇸🇬 **Singapore** - Complete coverage

### Industries
- **FMCG** - Fast Moving Consumer Goods (food, beverages, personal care)
- **E-Commerce** - Online retail, marketplaces, digital commerce
- **Quick Commerce** - Instant delivery, grocery delivery, on-demand
- **CPG** - Consumer Packaged Goods
- **Retail** - Stores, supermarkets, chains

## Quick Start

### Extract from All Markets

```bash
# Extract 100 leads from all geographies and industries
python src/targeted_extraction.py --geography all --industry all --count 100
```

### Extract from Specific Geography

```bash
# India only - all industries
python src/targeted_extraction.py --geography india --industry all --count 100

# Singapore only - e-commerce
python src/targeted_extraction.py --geography singapore --industry ecommerce --count 50

# Europe only - FMCG
python src/targeted_extraction.py --geography europe --industry fmcg --count 100

# USA only - retail
python src/targeted_extraction.py --geography us --industry retail --count 150
```

### Extract Specific Industry Across All Geographies

```bash
# FMCG companies from all geographies
python src/targeted_extraction.py --geography all --industry fmcg --count 200

# E-commerce companies globally
python src/targeted_extraction.py --geography all --industry ecommerce --count 150
```

### With AI Enrichment

```bash
# Extract and enrich with free AI
python src/targeted_extraction.py --geography india --industry fmcg --enrich --count 100
```

## Data Sources by Geography

### India 🇮🇳
- **Source**: OpenCorporates (Indian company registry)
- **Coverage**: Private and public companies
- **Fields**: Company name, CIN, state, address, incorporation date
- **Focus States**: Maharashtra, Karnataka, Delhi, Tamil Nadu, Gujarat

### USA 🇺🇸
- **Sources**:
  - SEC EDGAR (public companies)
  - USASpending.gov (federal contractors)
- **Coverage**: 8,000+ public companies + federal contractors
- **Fields**: Company name, ticker, SIC/NAICS, address, phone, financials

### Europe 🇪🇺
- **Source**: OpenCorporates (national registries)
- **Coverage**:
  - UK: Companies House
  - Germany: Handelsregister
  - France: INPI
  - Netherlands: KVK
  - Ireland: CRO
- **Fields**: Company number, address, directors, registration date

### Singapore 🇸🇬
- **Source**: OpenCorporates (ACRA registry)
- **Coverage**: All Singapore registered companies
- **Fields**: Company name, UEN, entity type, address

## Industry Mapping

### FMCG (Fast Moving Consumer Goods)

**Includes:**
- Food products
- Beverages
- Personal care items
- Household products
- Packaged goods

**SIC Codes (US):** 2000, 2080, 2840, 2844, 5140
**UK SIC:** 10, 11, 20.4, 46.3

### E-Commerce

**Includes:**
- Online retailers
- Marketplaces
- Digital commerce platforms
- Direct-to-consumer brands

**SIC Codes (US):** 5961, 7375, 5999
**UK SIC:** 47.91, 62.01

### Quick Commerce

**Includes:**
- Instant delivery services
- Grocery delivery
- On-demand delivery
- Dark stores

**SIC Codes (US):** 5961, 5411
**NAICS:** 4541, 4921

### CPG (Consumer Packaged Goods)

**Includes:**
- Packaged foods
- Beverages
- Household products
- Personal care

**SIC Codes (US):** 2000, 2800, 2840
**UK SIC:** 10, 20, 22

### Retail

**Includes:**
- Physical stores
- Supermarkets
- Department stores
- Chain stores
- Specialty retail

**SIC Codes (US):** 5200-5900 series
**UK SIC:** 47 (all subsectors)

## Output Files

### File Structure

Results are exported to `data/processed/`:

```
data/processed/
├── targeted_leads_20240115_143022.csv        # All leads combined
├── india_leads_20240115_143022.csv           # India only
├── singapore_leads_20240115_143022.csv       # Singapore only
├── europe_leads_20240115_143022.csv          # Europe only
└── us_leads_20240115_143022.csv              # USA only
```

### Data Fields

Each lead contains:
- `company_name` - Official company name
- `country` / `state` - Location
- `industry` - Industry classification
- `address` - Registered address
- `status` - Active/Inactive
- `registration_date` - Incorporation date
- `target_geography` - Your target market
- `target_industry` - Your target sector
- `source` - Data source used
- `extracted_at` - Extraction timestamp

## Configuration

### Custom Configuration

Edit `config/target_config.yaml` to customize:

```yaml
# Focus states for India
geographies:
  india:
    focus_states: ["Maharashtra", "Karnataka", "Delhi"]

# Custom industry keywords
industries:
  fmcg:
    keywords: ["FMCG", "consumer goods", "beverages"]
    sic_codes: ["2000", "2080"]
```

### Extraction Settings

```yaml
extraction_settings:
  min_leads_per_geography: 100
  min_leads_per_industry: 50
  enable_ai_enrichment: true
  export_format: "csv"
```

## Use Cases

### 1. Market Entry Research

**Scenario**: Entering Indian FMCG market

```bash
python src/targeted_extraction.py \
  --geography india \
  --industry fmcg \
  --count 500 \
  --enrich
```

**Result**: 500 FMCG companies in India with AI-generated insights

### 2. Competitor Analysis

**Scenario**: Analyze e-commerce landscape in Southeast Asia

```bash
python src/targeted_extraction.py \
  --geography singapore \
  --industry ecommerce \
  --count 200
```

**Result**: 200 e-commerce companies in Singapore

### 3. B2B Sales Prospecting

**Scenario**: Target retail chains in US and Europe

```bash
python src/targeted_extraction.py \
  --geography all \
  --industry retail \
  --count 1000
```

**Result**: 1000 retail companies across all geographies

### 4. Investment Research

**Scenario**: Find CPG companies for investment analysis

```bash
python src/targeted_extraction.py \
  --geography all \
  --industry cpg \
  --count 300 \
  --enrich
```

**Result**: 300 CPG companies with market insights

## Performance

### Extraction Speed

| Geography | Companies/Minute | Daily Limit |
|-----------|------------------|-------------|
| India | 10-20 | 200 (OpenCorporates free tier) |
| Singapore | 10-20 | 200 (OpenCorporates free tier) |
| Europe | 10-20 | 200 (OpenCorporates free tier) |
| USA (SEC) | 50-100 | Unlimited |
| USA (Federal) | 100+ | Unlimited |

### Cost Analysis

| Operation | Cost | Alternative Paid Service |
|-----------|------|-------------------------|
| Geographic targeting | $0 | $200-500/month |
| Industry filtering | $0 | $100-300/month |
| Data enrichment | $0 | $150-400/month |
| Export & CRM integration | $0 | $50-200/month |
| **Total** | **$0/month** | **$500-1,400/month** |

## Best Practices

### 1. Start Small
```bash
# Test with small dataset first
python src/targeted_extraction.py --geography india --industry fmcg --count 10
```

### 2. Use Daily Limits Wisely
- OpenCorporates: 200 calls/day free
- Spread extraction across multiple days for large datasets
- Use SEC EDGAR (unlimited) for US companies

### 3. Combine Sources
```bash
# Get diverse data by using multiple geographies
python src/targeted_extraction.py --geography all --industry ecommerce --count 200
```

### 4. Enrich Strategically
```bash
# Enrich only your best leads
python src/targeted_extraction.py --geography singapore --industry qcommerce --count 50 --enrich
```

## Troubleshooting

### "API limit reached"
**Solution**: OpenCorporates free tier is 200 calls/day. Wait 24 hours or:
- Focus on US companies (unlimited via SEC EDGAR)
- Reduce `--count` parameter
- Target specific geography instead of "all"

### "No companies found"
**Solution**:
- Try different industry keywords
- Check spelling of geography names
- Some industry-geography combinations may have few companies

### "Extraction too slow"
**Solution**:
- US extraction is fastest (SEC EDGAR has no rate limits)
- Reduce `--count` for international extractions
- Run during off-peak hours

## Advanced Usage

### Python API

```python
from targeted_extraction import TargetedExtractor
import yaml

# Load config
with open('config/target_config.yaml') as f:
    config = yaml.safe_load(f)

# Initialize
extractor = TargetedExtractor(config)

# Extract
results = extractor.extract_targeted_leads(
    geographies=['india', 'singapore'],
    industries=['fmcg', 'ecommerce'],
    total_count=200
)

# Results structure: {geography: {industry: [leads]}}
india_fmcg = results['india']['fmcg']
```

### Custom Filtering

```python
from extractors.india_extractor import IndiaExtractor

extractor = IndiaExtractor()

# Extract from specific state
maharashtra_companies = extractor.extract_by_state(
    state="Maharashtra",
    industry="fmcg",
    limit=100
)

# Extract by major cities
city_results = extractor.extract_major_cities(
    industry="ecommerce",
    limit=200
)
```

## Legal Compliance

All extraction is:
✅ **100% Legal** - Public registry data only
✅ **Within API Terms** - Respects rate limits
✅ **Properly Licensed** - ODbL, public domain
✅ **Business Data Only** - No personal information

See `docs/LEGAL.md` for full legal documentation.

## Support

### Need Help?
1. Check `docs/SETUP.md` for setup issues
2. See `docs/SOURCES.md` for data source details
3. Review `docs/LEGAL.md` for compliance questions

### Want More Data?
- Increase `--count` parameter (respect rate limits)
- Run extraction daily to build database
- Combine multiple geographies and industries
- Use enrichment for additional insights

---

**Ready to extract targeted leads?**

```bash
python src/targeted_extraction.py --geography all --industry all --count 500
```

Get 500 targeted leads from your exact markets in minutes! 🚀
