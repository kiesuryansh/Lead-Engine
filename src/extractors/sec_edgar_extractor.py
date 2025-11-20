"""
SEC EDGAR Extractor - 100% Legal Public Data Source

Extracts company information from SEC EDGAR database.
All data is public domain under US law (17 U.S.C. § 105).

API Documentation: https://www.sec.gov/edgar/sec-api-documentation
Rate Limit: 10 requests/second (enforced)
"""

import requests
import time
import json
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class Company:
    """Company information from SEC filings"""
    cik: str
    name: str
    ticker: Optional[str]
    sic: Optional[str]  # Standard Industrial Classification
    sic_description: Optional[str]
    business_address: Optional[Dict]
    mailing_address: Optional[Dict]
    business_phone: Optional[str]
    website: Optional[str]
    state_of_incorporation: Optional[str]
    fiscal_year_end: Optional[str]
    category: Optional[str]
    entity_type: Optional[str]

    def to_dict(self):
        return {
            'cik': self.cik,
            'company_name': self.name,
            'ticker': self.ticker,
            'industry_code': self.sic,
            'industry': self.sic_description,
            'address': self.business_address,
            'phone': self.business_phone,
            'website': self.website,
            'state': self.state_of_incorporation,
            'entity_type': self.entity_type,
            'source': 'SEC EDGAR',
            'extracted_at': datetime.now().isoformat()
        }


class SECEdgarExtractor:
    """
    Extract company data from SEC EDGAR - 100% Legal & Free

    Data Source: US Securities and Exchange Commission
    Legal Basis: Public domain government data
    Rate Limit: 10 requests/second (we use 5 to be safe)
    Cost: $0
    """

    BASE_URL = "https://www.sec.gov"
    COMPANY_TICKERS_URL = f"{BASE_URL}/files/company_tickers.json"
    SUBMISSIONS_URL = f"{BASE_URL}/cgi-bin/browse-edgar"

    # SEC requires identification in User-Agent
    HEADERS = {
        'User-Agent': 'Lead-Generation-Engine contact@example.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }

    # Rate limiting: 5 requests/second (conservative)
    REQUEST_DELAY = 0.2  # 200ms between requests

    def __init__(self, user_agent_email: str = "contact@example.com"):
        """
        Initialize SEC EDGAR extractor

        Args:
            user_agent_email: Your email for SEC user-agent identification
        """
        self.HEADERS['User-Agent'] = f'Lead-Generation-Engine {user_agent_email}'
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _rate_limit(self):
        """Enforce rate limiting to respect SEC's 10 req/sec limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    def get_all_company_tickers(self) -> pd.DataFrame:
        """
        Get complete list of all companies with SEC tickers

        Returns:
            DataFrame with CIK, ticker, company name for all public companies

        Example:
            >>> extractor = SECEdgarExtractor()
            >>> companies = extractor.get_all_company_tickers()
            >>> print(f"Found {len(companies)} public companies")
        """
        print(f"📊 Fetching all SEC registered companies...")

        self._rate_limit()
        response = self.session.get(self.COMPANY_TICKERS_URL)
        response.raise_for_status()

        data = response.json()

        # Convert to DataFrame
        companies = []
        for item in data.values():
            companies.append({
                'cik': str(item['cik_str']).zfill(10),
                'ticker': item['ticker'],
                'company_name': item['title']
            })

        df = pd.DataFrame(companies)
        print(f"✅ Found {len(df):,} public companies")

        return df

    def get_company_details(self, cik: str) -> Optional[Company]:
        """
        Get detailed information for a specific company

        Args:
            cik: Central Index Key (10-digit CIK)

        Returns:
            Company object with full details
        """
        cik = str(cik).zfill(10)

        # Get company facts JSON
        facts_url = f"{self.BASE_URL}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&output=json"

        self._rate_limit()

        try:
            response = self.session.get(facts_url)
            response.raise_for_status()
            data = response.json()

            # Parse company information
            company_info = data.get('company', {})

            company = Company(
                cik=cik,
                name=company_info.get('name', ''),
                ticker=company_info.get('ticker'),
                sic=company_info.get('sic'),
                sic_description=company_info.get('sicDescription'),
                business_address=company_info.get('addresses', {}).get('business'),
                mailing_address=company_info.get('addresses', {}).get('mailing'),
                business_phone=company_info.get('phone'),
                website=None,  # Not in basic API, needs filing extraction
                state_of_incorporation=company_info.get('stateOfIncorporation'),
                fiscal_year_end=company_info.get('fiscalYearEnd'),
                category=company_info.get('category'),
                entity_type=company_info.get('entityType')
            )

            return company

        except Exception as e:
            print(f"❌ Error fetching company {cik}: {e}")
            return None

    def extract_leads(self,
                     count: int = 100,
                     sic_codes: Optional[List[str]] = None,
                     states: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract company leads from SEC EDGAR

        Args:
            count: Number of companies to extract
            sic_codes: Filter by Standard Industrial Classification codes
            states: Filter by state of incorporation

        Returns:
            List of company dictionaries

        Example:
            >>> # Get 100 tech companies (SIC 7370-7379)
            >>> extractor = SECEdgarExtractor()
            >>> tech_companies = extractor.extract_leads(
            ...     count=100,
            ...     sic_codes=['7370', '7371', '7372', '7373']
            ... )
        """
        print(f"🔍 Extracting {count} companies from SEC EDGAR...")

        # Get base company list
        all_companies = self.get_all_company_tickers()

        leads = []
        processed = 0

        # Process companies
        for idx, row in all_companies.iterrows():
            if len(leads) >= count:
                break

            print(f"   Processing {processed + 1}/{count}: {row['company_name']}", end='\r')

            # Get detailed information
            company = self.get_company_details(row['cik'])

            if company:
                # Apply filters
                if sic_codes and company.sic not in sic_codes:
                    continue
                if states and company.state_of_incorporation not in states:
                    continue

                leads.append(company.to_dict())

            processed += 1

            # Safety limit to avoid processing entire database
            if processed >= count * 3:  # Try 3x target to account for filtering
                break

        print(f"\n✅ Extracted {len(leads)} companies from SEC EDGAR")

        return leads

    def get_companies_by_industry(self, sic_code: str, limit: int = 100) -> List[Dict]:
        """
        Get companies in a specific industry

        Args:
            sic_code: 4-digit SIC code
            limit: Maximum companies to return

        Returns:
            List of companies in that industry

        Example:
            >>> # Get software companies (SIC 7372)
            >>> extractor = SECEdgarExtractor()
            >>> software_companies = extractor.get_companies_by_industry('7372', limit=50)
        """
        return self.extract_leads(count=limit, sic_codes=[sic_code])

    def export_to_csv(self, leads: List[Dict], filename: str):
        """Export leads to CSV file"""
        df = pd.DataFrame(leads)
        df.to_csv(filename, index=False)
        print(f"💾 Exported {len(leads)} leads to {filename}")


# Common SIC codes for targeting
TECH_SIC_CODES = {
    '7370': 'Computer Programming, Data Processing',
    '7371': 'Computer Programming Services',
    '7372': 'Prepackaged Software',
    '7373': 'Computer Integrated Systems Design',
    '7374': 'Computer Processing & Data Preparation',
    '7375': 'Information Retrieval Services',
    '7379': 'Computer Related Services',
}

MANUFACTURING_SIC_CODES = {
    '3571': 'Electronic Computers',
    '3572': 'Computer Storage Devices',
    '3577': 'Computer Peripheral Equipment',
    '3600': 'Electronic Equipment',
}

FINANCE_SIC_CODES = {
    '6020': 'Commercial Banks',
    '6199': 'Finance Services',
    '6200': 'Security & Commodity Brokers',
    '6282': 'Investment Advice',
}


if __name__ == "__main__":
    # Demo: Extract 10 tech companies
    extractor = SECEdgarExtractor(user_agent_email="your-email@example.com")

    print("🎯 DEMO: Extracting tech companies from SEC EDGAR")
    print("=" * 60)

    tech_leads = extractor.extract_leads(
        count=10,
        sic_codes=list(TECH_SIC_CODES.keys())
    )

    print("\n📋 Sample Companies:")
    for i, lead in enumerate(tech_leads[:5], 1):
        print(f"\n{i}. {lead['company_name']}")
        print(f"   Industry: {lead['industry']}")
        print(f"   Ticker: {lead['ticker']}")
        if lead['phone']:
            print(f"   Phone: {lead['phone']}")
        if lead['address']:
            print(f"   Location: {lead['address'].get('city')}, {lead['address'].get('state')}")

    # Export to CSV
    extractor.export_to_csv(tech_leads, '/home/user/Lead-Engine/data/raw/sec_edgar_leads.csv')

    print(f"\n✅ Successfully extracted {len(tech_leads)} companies")
    print(f"💰 Cost: $0.00")
    print(f"⚖️  Legal: 100% (Public domain government data)")
