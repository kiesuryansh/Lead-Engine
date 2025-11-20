"""
Data.gov Extractor - Federal Government Data

Extracts business information from US government datasets:
- Federal contracts (USASpending.gov)
- Government grants
- Certified small businesses
- Federal vendor registrations

All data is public domain under US law.

API Documentation: https://api.usaspending.gov
Rate Limit: None (reasonable use expected)
Cost: $0
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class Contractor:
    """Federal contractor information"""
    contractor_name: str
    duns: Optional[str]
    location: Optional[Dict]
    contract_value: Optional[float]
    contracting_agency: Optional[str]
    naics_code: Optional[str]
    naics_description: Optional[str]
    contracts_count: int
    website: Optional[str]
    parent_company: Optional[str]

    def to_dict(self):
        return {
            'company_name': self.contractor_name,
            'duns': self.duns,
            'location': self.location,
            'total_contract_value': self.contract_value,
            'primary_agency': self.contracting_agency,
            'industry_code': self.naics_code,
            'industry': self.naics_description,
            'contracts_count': self.contracts_count,
            'website': self.website,
            'parent_company': self.parent_company,
            'source': 'USASpending.gov',
            'extracted_at': datetime.now().isoformat()
        }


class DataGovExtractor:
    """
    Extract business data from Data.gov and USASpending.gov

    Data Source: US Government federal spending data
    Legal Basis: Public domain (federal government data)
    Rate Limit: None (be respectful)
    Cost: $0
    """

    USASPENDING_API = "https://api.usaspending.gov/api/v2"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Lead-Generation-Engine',
            'Content-Type': 'application/json'
        })
        self.last_request_time = 0
        self.request_delay = 0.5  # Be respectful

    def _rate_limit(self):
        """Be respectful with requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def search_contractors(self,
                          keyword: Optional[str] = None,
                          naics_code: Optional[str] = None,
                          min_contract_value: float = 0,
                          limit: int = 100) -> List[Contractor]:
        """
        Search federal contractors

        Args:
            keyword: Search term (company name, description)
            naics_code: Industry code (6-digit NAICS)
            min_contract_value: Minimum total contract value
            limit: Maximum results

        Returns:
            List of contractors

        Example:
            >>> extractor = DataGovExtractor()
            >>> # Find IT contractors
            >>> it_contractors = extractor.search_contractors(
            ...     naics_code="541512",  # Computer Systems Design
            ...     min_contract_value=1000000,
            ...     limit=50
            ... )
        """
        print(f"🔍 Searching federal contractors...")

        endpoint = f"{self.USASPENDING_API}/search/spending_by_award"

        payload = {
            "filters": {
                "time_period": [
                    {
                        "start_date": "2020-01-01",
                        "end_date": "2024-12-31"
                    }
                ],
                "award_type_codes": ["A", "B", "C", "D"],  # Contracts
            },
            "fields": [
                "Recipient Name",
                "Award Amount",
                "awarding_agency_name",
                "recipient_location_country_name",
                "naics_code",
                "naics_description"
            ],
            "limit": limit,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc"
        }

        if keyword:
            payload["filters"]["keywords"] = [keyword]

        if naics_code:
            payload["filters"]["naics_codes"] = [naics_code]

        self._rate_limit()

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()

            contractors = []
            results = data.get('results', [])

            print(f"✅ Found {len(results)} contractors")

            # Group by contractor name and aggregate
            contractor_dict = {}

            for result in results:
                name = result.get('Recipient Name', '')
                if not name:
                    continue

                if name not in contractor_dict:
                    contractor_dict[name] = {
                        'name': name,
                        'total_value': 0,
                        'contracts': 0,
                        'agencies': set(),
                        'naics': set(),
                        'naics_desc': set()
                    }

                contractor_dict[name]['total_value'] += float(result.get('Award Amount', 0))
                contractor_dict[name]['contracts'] += 1

                if result.get('awarding_agency_name'):
                    contractor_dict[name]['agencies'].add(result['awarding_agency_name'])

                if result.get('naics_code'):
                    contractor_dict[name]['naics'].add(result['naics_code'])

                if result.get('naics_description'):
                    contractor_dict[name]['naics_desc'].add(result['naics_description'])

            # Convert to Contractor objects
            for name, data in contractor_dict.items():
                if data['total_value'] >= min_contract_value:
                    contractor = Contractor(
                        contractor_name=name,
                        duns=None,
                        location=None,
                        contract_value=data['total_value'],
                        contracting_agency=list(data['agencies'])[0] if data['agencies'] else None,
                        naics_code=list(data['naics'])[0] if data['naics'] else None,
                        naics_description=list(data['naics_desc'])[0] if data['naics_desc'] else None,
                        contracts_count=data['contracts'],
                        website=None,
                        parent_company=None
                    )
                    contractors.append(contractor)

            # Sort by contract value
            contractors.sort(key=lambda x: x.contract_value or 0, reverse=True)

            return contractors[:limit]

        except Exception as e:
            print(f"❌ Error searching contractors: {e}")
            return []

    def get_contractors_by_agency(self, agency_name: str, limit: int = 50) -> List[Contractor]:
        """
        Get contractors for a specific agency

        Args:
            agency_name: Federal agency name (e.g., "Department of Defense")
            limit: Maximum results

        Returns:
            List of contractors
        """
        print(f"🔍 Finding contractors for {agency_name}...")

        endpoint = f"{self.USASPENDING_API}/search/spending_by_award"

        payload = {
            "filters": {
                "time_period": [{"start_date": "2020-01-01", "end_date": "2024-12-31"}],
                "award_type_codes": ["A", "B", "C", "D"],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": agency_name}]
            },
            "limit": limit,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc"
        }

        self._rate_limit()

        try:
            response = self.session.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()

            contractors = []
            for result in data.get('results', []):
                contractor = Contractor(
                    contractor_name=result.get('Recipient Name', ''),
                    duns=result.get('recipient_uei'),
                    location=None,
                    contract_value=float(result.get('Award Amount', 0)),
                    contracting_agency=agency_name,
                    naics_code=result.get('naics_code'),
                    naics_description=result.get('naics_description'),
                    contracts_count=1,
                    website=None,
                    parent_company=None
                )
                contractors.append(contractor)

            print(f"✅ Found {len(contractors)} contractors")
            return contractors

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def extract_leads(self,
                     industry: Optional[str] = None,
                     min_value: float = 0,
                     count: int = 100) -> List[Dict]:
        """
        Extract contractor leads

        Args:
            industry: NAICS code or keyword
            min_value: Minimum contract value
            count: Number of leads

        Returns:
            List of contractor dictionaries
        """
        # Check if industry is a NAICS code
        naics_code = industry if industry and industry.isdigit() else None
        keyword = industry if not naics_code else None

        contractors = self.search_contractors(
            keyword=keyword,
            naics_code=naics_code,
            min_contract_value=min_value,
            limit=count
        )

        leads = [c.to_dict() for c in contractors]

        print(f"✅ Extracted {len(leads)} contractor leads")
        return leads

    def export_to_csv(self, leads: List[Dict], filename: str):
        """Export to CSV"""
        df = pd.DataFrame(leads)
        df.to_csv(filename, index=False)
        print(f"💾 Exported {len(leads)} leads to {filename}")


# Common NAICS codes for federal contractors
FEDERAL_CONTRACTOR_NAICS = {
    '541512': 'Computer Systems Design Services',
    '541511': 'Custom Computer Programming Services',
    '541513': 'Computer Facilities Management Services',
    '541519': 'Other Computer Related Services',
    '541330': 'Engineering Services',
    '541611': 'Administrative Management Consulting Services',
    '541618': 'Other Management Consulting Services',
    '336411': 'Aircraft Manufacturing',
    '336413': 'Other Aircraft Parts Manufacturing',
    '541715': 'Research and Development in Physical, Engineering Sciences',
}


if __name__ == "__main__":
    # Demo
    extractor = DataGovExtractor()

    print("🎯 DEMO: Extracting federal contractors")
    print("=" * 60)

    # Get IT contractors
    it_contractors = extractor.extract_leads(
        industry="541512",  # Computer Systems Design
        min_value=100000,
        count=10
    )

    print("\n📋 Sample Federal Contractors:")
    for i, contractor in enumerate(it_contractors[:5], 1):
        print(f"\n{i}. {contractor['company_name']}")
        print(f"   Industry: {contractor['industry']}")
        print(f"   Total Contracts: ${contractor['total_contract_value']:,.0f}")
        print(f"   Number of Contracts: {contractor['contracts_count']}")
        print(f"   Primary Agency: {contractor['primary_agency']}")

    # Export
    extractor.export_to_csv(
        it_contractors,
        '/home/user/Lead-Engine/data/raw/federal_contractors.csv'
    )

    print(f"\n✅ Successfully extracted {len(it_contractors)} contractors")
    print(f"💰 Cost: $0.00")
    print(f"⚖️  Legal: 100% (Public domain government data)")
