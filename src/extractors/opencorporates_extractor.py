"""
OpenCorporates Extractor - Legal Open Database

Extracts company information from OpenCorporates.com
License: Open Database License (ODbL) - Commercial use allowed with attribution

API Documentation: https://api.opencorporates.com/documentation/API-Reference
Free Tier: 500 calls/month, 200 calls/day
Cost: $0
"""

import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class OpenCorpCompany:
    """Company from OpenCorporates"""
    name: str
    company_number: str
    jurisdiction_code: str
    incorporation_date: Optional[str]
    company_type: Optional[str]
    registered_address: Optional[str]
    current_status: Optional[str]
    industry_codes: Optional[List]
    officers: Optional[List]
    opencorporates_url: str

    def to_dict(self):
        return {
            'company_name': self.name,
            'company_number': self.company_number,
            'country': self.jurisdiction_code,
            'incorporation_date': self.incorporation_date,
            'company_type': self.company_type,
            'address': self.registered_address,
            'status': self.current_status,
            'industries': self.industry_codes,
            'officers': self.officers,
            'url': self.opencorporates_url,
            'source': 'OpenCorporates',
            'extracted_at': datetime.now().isoformat()
        }


class OpenCorporatesExtractor:
    """
    Extract company data from OpenCorporates - Legal & Free

    Data Source: OpenCorporates (200M+ companies worldwide)
    Legal Basis: Open Database License (ODbL)
    Rate Limit: 200 calls/day, 500/month (free tier)
    Cost: $0
    Attribution: Required (automatically included)
    """

    BASE_URL = "https://api.opencorporates.com/v0.4"

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize OpenCorporates extractor

        Args:
            api_token: Optional API token for higher limits (still free)
                      Get one at: https://opencorporates.com/api_accounts/new
        """
        self.api_token = api_token
        self.session = requests.Session()
        self.calls_made = 0
        self.daily_limit = 200
        self.last_request_time = 0
        self.request_delay = 1.0  # 1 second between requests

    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        if self.calls_made >= self.daily_limit:
            print(f"⚠️  Daily API limit reached ({self.daily_limit} calls)")
            return None

        self._rate_limit()

        if params is None:
            params = {}

        if self.api_token:
            params['api_token'] = self.api_token

        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self.calls_made += 1
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None

    def search_companies(self,
                        query: str = None,
                        jurisdiction_code: str = None,
                        country_code: str = None,
                        industry_codes: List[str] = None,
                        per_page: int = 30,
                        max_results: int = 100) -> List[OpenCorpCompany]:
        """
        Search for companies

        Args:
            query: Search term (company name, etc)
            jurisdiction_code: e.g., 'us_ca', 'gb', 'us_de'
            country_code: e.g., 'us', 'gb', 'de'
            industry_codes: Filter by industry
            per_page: Results per page (max 100)
            max_results: Maximum total results

        Returns:
            List of companies

        Example:
            >>> extractor = OpenCorporatesExtractor()
            >>> # Search for US tech companies
            >>> companies = extractor.search_companies(
            ...     query="technology",
            ...     country_code="us",
            ...     max_results=50
            ... )
        """
        print(f"🔍 Searching OpenCorporates: '{query}'...")

        params = {'per_page': min(per_page, 100)}

        if query:
            params['q'] = query
        if jurisdiction_code:
            params['jurisdiction_code'] = jurisdiction_code
        if country_code:
            params['country_code'] = country_code
        if industry_codes:
            params['industry_codes'] = ','.join(industry_codes)

        companies = []
        page = 1

        while len(companies) < max_results:
            params['page'] = page

            data = self._make_request('companies/search', params)

            if not data or 'results' not in data:
                break

            results = data['results'].get('companies', [])

            if not results:
                break

            for item in results:
                company_data = item.get('company', {})

                company = OpenCorpCompany(
                    name=company_data.get('name', ''),
                    company_number=company_data.get('company_number', ''),
                    jurisdiction_code=company_data.get('jurisdiction_code', ''),
                    incorporation_date=company_data.get('incorporation_date'),
                    company_type=company_data.get('company_type'),
                    registered_address=company_data.get('registered_address_in_full'),
                    current_status=company_data.get('current_status'),
                    industry_codes=company_data.get('industry_codes'),
                    officers=None,  # Need separate call for officers
                    opencorporates_url=company_data.get('opencorporates_url', '')
                )

                companies.append(company)

                if len(companies) >= max_results:
                    break

            page += 1

            # Respect daily limits
            if self.calls_made >= self.daily_limit:
                print(f"⚠️  Reached daily API limit at {len(companies)} companies")
                break

        print(f"✅ Found {len(companies)} companies")
        return companies

    def get_company_officers(self, jurisdiction_code: str, company_number: str) -> List[Dict]:
        """
        Get officers/directors for a company

        Args:
            jurisdiction_code: e.g., 'us_ca', 'gb'
            company_number: Company registration number

        Returns:
            List of officers with names and positions
        """
        endpoint = f"companies/{jurisdiction_code}/{company_number}/officers"

        data = self._make_request(endpoint)

        if not data or 'results' not in data:
            return []

        officers = []
        for item in data['results'].get('officers', []):
            officer_data = item.get('officer', {})
            officers.append({
                'name': officer_data.get('name'),
                'position': officer_data.get('position'),
                'start_date': officer_data.get('start_date'),
                'end_date': officer_data.get('end_date')
            })

        return officers

    def extract_leads(self,
                     country: str = "us",
                     query: str = None,
                     count: int = 100) -> List[Dict]:
        """
        Extract company leads

        Args:
            country: Country code (us, gb, de, etc)
            query: Search query (industry, company type, etc)
            count: Number of companies to extract

        Returns:
            List of company dictionaries

        Example:
            >>> extractor = OpenCorporatesExtractor()
            >>> uk_companies = extractor.extract_leads(country="gb", count=50)
        """
        companies = self.search_companies(
            query=query,
            country_code=country,
            max_results=count
        )

        leads = [company.to_dict() for company in companies]

        print(f"✅ Extracted {len(leads)} companies from OpenCorporates")
        return leads

    def get_companies_by_industry(self,
                                  industry_code: str,
                                  country: str = "us",
                                  limit: int = 50) -> List[Dict]:
        """
        Get companies in specific industry

        Args:
            industry_code: Industry classification code
            country: Country code
            limit: Maximum companies

        Returns:
            List of companies
        """
        companies = self.search_companies(
            country_code=country,
            industry_codes=[industry_code],
            max_results=limit
        )

        return [company.to_dict() for company in companies]

    def export_to_csv(self, leads: List[Dict], filename: str):
        """Export leads to CSV"""
        df = pd.DataFrame(leads)

        # Add attribution as required by ODbL
        df['data_attribution'] = 'Data from OpenCorporates (opencorporates.com) - ODbL licensed'

        df.to_csv(filename, index=False)
        print(f"💾 Exported {len(leads)} leads to {filename}")


# Popular jurisdiction codes
JURISDICTIONS = {
    'us_de': 'Delaware, USA (popular for incorporation)',
    'us_ca': 'California, USA',
    'us_ny': 'New York, USA',
    'gb': 'United Kingdom',
    'ie': 'Ireland (many tech companies)',
    'sg': 'Singapore',
    'hk': 'Hong Kong',
    'au': 'Australia',
    'ca': 'Canada',
    'de': 'Germany',
}


if __name__ == "__main__":
    # Demo: Extract companies
    extractor = OpenCorporatesExtractor()

    print("🎯 DEMO: Extracting companies from OpenCorporates")
    print("=" * 60)

    # Search for technology companies in US
    tech_companies = extractor.extract_leads(
        country="us",
        query="technology software",
        count=10
    )

    print("\n📋 Sample Companies:")
    for i, company in enumerate(tech_companies[:5], 1):
        print(f"\n{i}. {company['company_name']}")
        print(f"   Country: {company['country']}")
        print(f"   Status: {company['status']}")
        print(f"   Incorporation: {company['incorporation_date']}")
        if company['address']:
            print(f"   Address: {company['address'][:100]}...")

    # Export
    extractor.export_to_csv(
        tech_companies,
        '/home/user/Lead-Engine/data/raw/opencorporates_leads.csv'
    )

    print(f"\n✅ Successfully extracted {len(tech_companies)} companies")
    print(f"💰 Cost: $0.00")
    print(f"⚖️  Legal: 100% (ODbL licensed)")
    print(f"📊 API calls used: {extractor.calls_made}/{extractor.daily_limit}")
