# ⚖️ Legal Compliance Documentation

## Overview

This system uses ONLY legal, publicly available data sources. We do NOT scrape any websites that prohibit it in their Terms of Service.

## Legal Data Sources

### 1. SEC EDGAR (Securities and Exchange Commission)

**Legal Status**: ✅ 100% Legal - Public Domain

- **Source**: https://www.sec.gov/edgar
- **License**: Public domain, freely redistributable
- **Data**: All US public company filings
- **API**: https://www.sec.gov/edgar/sec-api-documentation
- **Terms**: Explicitly allows automated access with rate limiting (10 requests/second)
- **What we extract**: Company names, addresses, industry codes, business descriptions, executive contacts

**Legal Basis**:
- Securities Exchange Act of 1934 requires public disclosure
- SEC explicitly provides bulk data access
- No copyright on government data (17 U.S.C. § 105)

### 2. OpenCorporates

**Legal Status**: ✅ Legal - Open Database License

- **Source**: https://opencorporates.com
- **License**: Open Database License (ODbL)
- **API**: https://api.opencorporates.com (free tier: 500 calls/month)
- **Data**: 200M+ companies from official registries worldwide
- **What we extract**: Company names, registration numbers, addresses, directors

**Legal Basis**:
- Aggregates official government registry data
- ODbL allows commercial use with attribution
- Free API tier explicitly provided

### 3. Companies House (UK)

**Legal Status**: ✅ Legal - Open Government License

- **Source**: https://www.companieshouse.gov.uk
- **License**: Open Government Licence v3.0
- **API**: https://developer.company-information.service.gov.uk/ (free)
- **Data**: 4M+ UK companies
- **What we extract**: Company details, filing history, officers

**Legal Basis**:
- UK government open data initiative
- Explicitly licensed for commercial reuse
- Free API with documentation

### 4. USPTO (US Patent and Trademark Office)

**Legal Status**: ✅ Legal - Public Domain

- **Source**: https://www.uspto.gov
- **License**: Public domain
- **API**: https://developer.uspto.gov (free)
- **Data**: Trademark owners, patent assignees
- **What we extract**: Business names, addresses from trademark registrations

**Legal Basis**:
- Federal government data (public domain)
- Bulk data downloads provided
- API explicitly for public use

### 5. Data.gov

**Legal Status**: ✅ Legal - Public Domain

- **Source**: https://data.gov
- **License**: Public domain (most datasets)
- **Data**: Government contracts, grants, business registrations
- **What we extract**: Federal contractors, grant recipients, certified businesses

**Legal Basis**:
- Open government initiative
- Explicitly for public reuse
- 250,000+ datasets available

### 6. Job Posting APIs (Public Listings)

#### Adzuna API
**Legal Status**: ✅ Legal - Licensed API

- **Source**: https://developer.adzuna.com
- **License**: API license agreement
- **Free Tier**: 5,000 calls/month
- **What we extract**: Company names, hiring signals, tech stack from job descriptions

**Legal Basis**:
- Provides free API tier for developers
- Job postings are publicly listed
- Within API terms of service

#### USAJobs API
**Legal Status**: ✅ Legal - Public Domain

- **Source**: https://developer.usajobs.gov
- **License**: Public domain
- **Data**: Federal job openings and contractors
- **What we extract**: Government contractors, hiring companies

**Legal Basis**:
- Federal government API
- Public data, freely available
- No restrictions on use

### 7. Free Email/Company APIs (Within Terms)

#### Hunter.io Free Tier
**Legal Status**: ✅ Legal - Within API Terms

- **Free Tier**: 25 searches/month
- **License**: Terms of Service
- **What we use**: Email pattern verification only
- **Compliance**: Stay within free tier limits

#### Abstract API
**Legal Status**: ✅ Legal - Free Tier

- **Free Tier**: 100 requests/month
- **What we use**: Email validation (format/MX record check)
- **Compliance**: Within terms of service

## What We Do NOT Do

❌ **We do NOT scrape**:
- LinkedIn (prohibits scraping)
- Apollo.io (prohibits scraping)
- Crunchbase (paid data, prohibits scraping)
- Facebook/Instagram (prohibits scraping)
- Any site with robots.txt disallow
- Any site with explicit ToS prohibition

❌ **We do NOT**:
- Bypass CAPTCHAs
- Use "stealth" browsers to evade detection
- Rotate IPs to avoid rate limits
- Access paid databases without authorization
- Collect personal emails without consent
- Violate any Terms of Service

## Compliance Checklist

Before using any data source, we verify:

✅ **Legal Access**
- [ ] Data is publicly available
- [ ] Source provides explicit permission (API, open license, or public domain)
- [ ] No ToS violations

✅ **Ethical Use**
- [ ] No personal data without consent
- [ ] Respect rate limits
- [ ] Provide attribution where required
- [ ] Follow robots.txt

✅ **Data Quality**
- [ ] Source is authoritative
- [ ] Data is recent/maintained
- [ ] Proper data validation

## GDPR Compliance

For EU data sources:
- ✅ We only collect business data from official registries
- ✅ Business contact information is considered "legitimate interest"
- ✅ We provide data deletion upon request
- ✅ We maintain data processing records
- ✅ Data subjects can access their information

## Rate Limiting & Respectful Access

We implement:
- Rate limiting per API terms
- Exponential backoff on errors
- User-agent identification
- Respect for robots.txt
- Off-peak hour scheduling where possible

## Attribution

Where required, we provide:
- Source attribution in data exports
- Links to original data sources
- License information
- Terms of use references

## Legal Disclaimer

This system is designed for legal lead generation using publicly available data. Users are responsible for:
- Complying with applicable laws in their jurisdiction
- Respecting API terms of service
- Obtaining consent before contacting leads
- Following email marketing regulations (CAN-SPAM, GDPR)

## Questions?

If you have concerns about any data source or practice, please review:
1. The source's Terms of Service
2. Applicable data protection laws
3. This documentation

**When in doubt, don't use it.** We prioritize legal compliance over data volume.
