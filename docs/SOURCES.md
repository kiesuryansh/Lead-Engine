# 📊 Data Sources Documentation

Complete guide to all legal, free data sources used in this system.

## Overview

All sources are:
- ✅ **100% Legal** - Public domain or openly licensed
- ✅ **100% Free** - No paid subscriptions required
- ✅ **Reliable** - Government or established open databases
- ✅ **Maintained** - Regularly updated

---

## 1. SEC EDGAR (Securities and Exchange Commission)

### What is it?
Official database of all US public company filings maintained by the Securities and Exchange Commission.

### Legal Status
- **License**: Public domain (17 U.S.C. § 105)
- **Redistribution**: Freely allowed
- **Commercial use**: ✅ Yes

### Data Available
- Company names and tickers
- Business addresses and phone numbers
- Industry classifications (SIC codes)
- Business descriptions
- Executive information
- Financial filings
- State of incorporation

### Access Details
- **Website**: https://www.sec.gov/edgar
- **API**: https://www.sec.gov/edgar/sec-api-documentation
- **Rate Limit**: 10 requests/second
- **Cost**: $0
- **Registration**: Not required
- **Coverage**: All US public companies (~8,000+)

### How to Use

```python
from extractors.sec_edgar_extractor import SECEdgarExtractor

extractor = SECEdgarExtractor(user_agent_email="your-email@example.com")

# Get tech companies
tech_companies = extractor.extract_leads(
    count=100,
    sic_codes=['7372']  # Software companies
)
```

### Best For
- US public companies
- Tech companies
- Large corporations
- Companies with financial filings

### Data Quality
- **Accuracy**: ⭐⭐⭐⭐⭐ (official government data)
- **Completeness**: ⭐⭐⭐⭐ (very complete)
- **Freshness**: ⭐⭐⭐⭐ (updated as filings occur)

---

## 2. OpenCorporates

### What is it?
World's largest open database of companies with 200M+ companies from official registries worldwide.

### Legal Status
- **License**: Open Database License (ODbL)
- **Redistribution**: ✅ With attribution
- **Commercial use**: ✅ Yes

### Data Available
- Company names and registration numbers
- Registered addresses
- Incorporation dates
- Company status (active/dissolved)
- Officers and directors (some jurisdictions)
- Industry codes

### Access Details
- **Website**: https://opencorporates.com
- **API**: https://api.opencorporates.com
- **Rate Limit**: 200 calls/day, 500/month (free tier)
- **Cost**: $0 (free tier)
- **Registration**: Optional (higher limits with account)
- **Coverage**: 200M+ companies in 140+ jurisdictions

### How to Use

```python
from extractors.opencorporates_extractor import OpenCorporatesExtractor

extractor = OpenCorporatesExtractor(api_token="optional")

# Search companies
companies = extractor.extract_leads(
    country="us",
    query="technology",
    count=50
)
```

### Best For
- International companies
- UK companies (excellent coverage)
- Delaware corporations
- Company registration verification

### Data Quality
- **Accuracy**: ⭐⭐⭐⭐⭐ (from official registries)
- **Completeness**: ⭐⭐⭐⭐ (varies by jurisdiction)
- **Freshness**: ⭐⭐⭐⭐ (updated from official sources)

### Important Jurisdictions
- `us_de` - Delaware (popular for incorporation)
- `us_ca` - California
- `us_ny` - New York
- `gb` - United Kingdom (excellent data)
- `ie` - Ireland (many tech companies)

---

## 3. USASpending.gov (Federal Spending Data)

### What is it?
Official database of all US federal government spending, including contracts and grants.

### Legal Status
- **License**: Public domain (federal government data)
- **Redistribution**: Freely allowed
- **Commercial use**: ✅ Yes

### Data Available
- Contractor/recipient names
- Contract values and types
- Awarding agencies
- NAICS industry codes
- Grant amounts
- Contract descriptions
- Location data

### Access Details
- **Website**: https://www.usaspending.gov
- **API**: https://api.usaspending.gov
- **Rate Limit**: None (be respectful)
- **Cost**: $0
- **Registration**: Not required
- **Coverage**: All federal spending (billions in contracts)

### How to Use

```python
from extractors.datagov_extractor import DataGovExtractor

extractor = DataGovExtractor()

# Get IT contractors
contractors = extractor.extract_leads(
    industry="541512",  # Computer Systems Design
    min_value=100000,
    count=100
)
```

### Best For
- Federal contractors
- Government vendors
- B2G (Business to Government) leads
- Large enterprise companies
- IT service providers

### Data Quality
- **Accuracy**: ⭐⭐⭐⭐⭐ (official federal data)
- **Completeness**: ⭐⭐⭐⭐⭐ (all federal spending)
- **Freshness**: ⭐⭐⭐⭐ (updated regularly)

### Valuable NAICS Codes
- `541512` - Computer Systems Design Services
- `541511` - Custom Computer Programming
- `541330` - Engineering Services
- `541611` - Management Consulting
- `336411` - Aircraft Manufacturing

---

## 4. Companies House (UK)

### What is it?
Official UK government registry of all UK companies.

### Legal Status
- **License**: Open Government Licence v3.0
- **Redistribution**: ✅ With attribution
- **Commercial use**: ✅ Yes

### Data Available
- Company details and registration numbers
- Registered addresses
- Officers and directors
- Filing history
- Company status
- SIC codes

### Access Details
- **Website**: https://www.companieshouse.gov.uk
- **API**: https://developer.company-information.service.gov.uk/
- **Rate Limit**: 600 requests per 5 minutes
- **Cost**: $0
- **Registration**: Required (free API key)
- **Coverage**: 4M+ UK companies

### How to Use

Can be accessed through OpenCorporates or directly via their API.

### Best For
- UK companies
- London startups
- European businesses with UK presence

---

## 5. Data.gov Datasets

### What is it?
Central repository of US government open datasets.

### Legal Status
- **License**: Mostly public domain (varies by dataset)
- **Redistribution**: Usually allowed
- **Commercial use**: ✅ Usually yes

### Data Available
- Government contracts
- Grant recipients
- Certified small businesses
- Business registrations
- Industry datasets

### Access Details
- **Website**: https://data.gov
- **Datasets**: 250,000+
- **Cost**: $0
- **Registration**: Not required

### Best For
- Niche industry data
- Grant recipients
- Certified businesses (8(a), HUBZone, etc.)
- Industry-specific lists

---

## Source Comparison

| Source | Coverage | Rate Limit | Best For |
|--------|----------|------------|----------|
| **SEC EDGAR** | 8K+ US public | 10/sec | Large US companies |
| **OpenCorporates** | 200M worldwide | 200/day free | International, UK |
| **USASpending** | All federal contractors | Unlimited | B2G, contractors |
| **Companies House** | 4M UK | 600/5min | UK companies |
| **Data.gov** | Varies | Varies | Niche datasets |

---

## Targeting Strategies

### For B2B SaaS
1. **SEC EDGAR**: SIC codes 7372, 7371 (software companies)
2. **OpenCorporates**: Search "software technology" in US/UK
3. **USASpending**: NAICS 541511, 541512 (IT services)

### For Enterprise Sales
1. **SEC EDGAR**: All public companies (have budget)
2. **USASpending**: High-value contractors (>$1M contracts)
3. **OpenCorporates**: Large registered companies

### For Government Contractors
1. **USASpending**: Current federal contractors
2. **Data.gov**: Certified small businesses
3. **SEC EDGAR**: Public defense contractors

### For Startups
1. **OpenCorporates**: Recent incorporations in DE, CA
2. **SEC EDGAR**: Recent IPOs
3. **Companies House**: UK startups (if targeting Europe)

---

## Legal Compliance Checklist

Before using any source, verify:

✅ **Access Rights**
- Data is publicly available
- No login/paywall required
- API is public and documented

✅ **Licensing**
- License permits commercial use
- Attribution requirements understood
- Redistribution rights confirmed

✅ **Rate Limits**
- Limits documented and respected
- Delays implemented
- Quota tracking in place

✅ **Data Ethics**
- Only business data (not personal)
- Legitimate business purpose
- Respects privacy where applicable

---

## Getting Help

### Issues with Sources
- Check API status pages
- Verify API keys are set correctly
- Respect rate limits
- Check docs for changes

### Adding New Sources
1. Verify it's legal (public domain/open license)
2. Check terms of service
3. Implement rate limiting
4. Add attribution where required
5. Document in this file

### Questions?
See `docs/LEGAL.md` for legal compliance details.
