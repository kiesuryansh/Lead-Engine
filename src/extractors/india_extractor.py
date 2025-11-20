"""
India Company Extractor - Legal Public Data Sources

Extracts company information from Indian public sources:
1. OpenCorporates (Indian companies)
2. India Trade Data (import/export companies)
3. Public databases

All data is from legal, public sources.
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class IndianCompany:
    """Indian company information"""
    name: str
    cin: Optional[str]  # Corporate Identity Number
    industry: Optional[str]
    state: Optional[str]
    city: Optional[str]
    registration_date: Optional[str]
    company_type: Optional[str]
    status: Optional[str]
    registered_address: Optional[str]

    def to_dict(self):
        return {
            'company_name': self.name,
            'cin': self.cin,
            'industry': self.industry,
            'state': self.state,
            'city': self.city,
            'registration_date': self.registration_date,
            'company_type': self.company_type,
            'status': self.status,
            'address': self.registered_address,
            'country': 'India',
            'source': 'India Extractor',
            'extracted_at': datetime.now().isoformat()
        }


class IndiaExtractor:
    """
    Extract company data from Indian public sources

    Data Source: OpenCorporates + public Indian company registries
    Legal Basis: Publicly available company registration data
    Cost: $0 (using free OpenCorporates API)
    """

    def __init__(self):
        # Will use OpenCorporates for Indian companies
        from extractors.opencorporates_extractor import OpenCorporatesExtractor
        self.opencorp = OpenCorporatesExtractor()

        self.target_states = [
            'Maharashtra',      # Mumbai, Pune
            'Karnataka',        # Bangalore
            'Delhi',           # New Delhi
            'Tamil Nadu',      # Chennai
            'Gujarat',         # Ahmedabad
            'Telangana',       # Hyderabad
            'Haryana',         # Gurgaon
            'West Bengal'      # Kolkata
        ]

    def search_companies_by_industry(self,
                                     industry_keywords: List[str],
                                     state: Optional[str] = None,
                                     limit: int = 100) -> List[IndianCompany]:
        """
        Search Indian companies by industry

        Args:
            industry_keywords: List of keywords (e.g., ["FMCG", "retail"])
            state: Filter by state (e.g., "Maharashtra")
            limit: Maximum results

        Returns:
            List of Indian companies

        Example:
            >>> extractor = IndiaExtractor()
            >>> fmcg_companies = extractor.search_companies_by_industry(
            ...     industry_keywords=["FMCG", "consumer goods"],
            ...     state="Maharashtra",
            ...     limit=50
            ... )
        """
        print(f"🇮🇳 Searching Indian companies: {', '.join(industry_keywords)}")

        # Combine keywords for search
        search_query = ' OR '.join(industry_keywords)

        # Search using OpenCorporates
        opencorp_results = self.opencorp.search_companies(
            query=search_query,
            jurisdiction_code="in",
            max_results=limit
        )

        companies = []

        for result in opencorp_results:
            # Parse state from address if available
            company_state = None
            address = result.get('address', '')
            if address:
                for state_name in self.target_states:
                    if state_name.lower() in address.lower():
                        company_state = state_name
                        break

            # Filter by state if specified
            if state and company_state and state.lower() not in company_state.lower():
                continue

            company = IndianCompany(
                name=result.get('company_name', ''),
                cin=result.get('company_number'),
                industry=None,  # Not provided by OpenCorporates
                state=company_state,
                city=None,
                registration_date=result.get('incorporation_date'),
                company_type=result.get('company_type'),
                status=result.get('status'),
                registered_address=address
            )

            companies.append(company)

        print(f"✅ Found {len(companies)} Indian companies")
        return companies

    def extract_fmcg_companies(self, limit: int = 100) -> List[Dict]:
        """Extract FMCG companies from India"""
        keywords = [
            "FMCG", "consumer goods", "packaged foods",
            "beverages", "personal care", "household products"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_ecommerce_companies(self, limit: int = 100) -> List[Dict]:
        """Extract E-commerce companies from India"""
        keywords = [
            "ecommerce", "e-commerce", "online retail",
            "marketplace", "online shopping"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_retail_companies(self, limit: int = 100) -> List[Dict]:
        """Extract retail companies from India"""
        keywords = [
            "retail", "supermarket", "stores", "mall",
            "shopping", "chain stores"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_by_state(self, state: str, industry: str = None, limit: int = 50) -> List[Dict]:
        """
        Extract companies from specific state

        Args:
            state: State name (e.g., "Maharashtra", "Karnataka")
            industry: Industry type (e.g., "FMCG", "ecommerce")
            limit: Maximum results

        Returns:
            List of companies from that state
        """
        keywords = []

        if industry:
            # Map industry to keywords
            industry_map = {
                'fmcg': ["FMCG", "consumer goods", "packaged"],
                'ecommerce': ["ecommerce", "online retail", "marketplace"],
                'qcommerce': ["quick commerce", "delivery", "grocery delivery"],
                'cpg': ["consumer packaged goods", "CPG"],
                'retail': ["retail", "stores", "supermarket"]
            }
            keywords = industry_map.get(industry.lower(), [industry])
        else:
            keywords = ["private limited", "limited"]  # Get all companies

        companies = self.search_companies_by_industry(
            keywords,
            state=state,
            limit=limit
        )

        return [c.to_dict() for c in companies]

    def extract_major_cities(self, industry: str = None, limit: int = 100) -> Dict[str, List[Dict]]:
        """
        Extract companies from major Indian cities

        Returns:
            Dictionary with city as key and list of companies as value
        """
        major_cities = {
            'Mumbai': 'Maharashtra',
            'Bangalore': 'Karnataka',
            'Delhi': 'Delhi',
            'Chennai': 'Tamil Nadu',
            'Hyderabad': 'Telangana',
            'Pune': 'Maharashtra',
            'Ahmedabad': 'Gujarat',
            'Kolkata': 'West Bengal'
        }

        results = {}

        for city, state in major_cities.items():
            print(f"\n🏙️  Extracting from {city}, {state}...")

            companies = self.extract_by_state(
                state=state,
                industry=industry,
                limit=limit // len(major_cities)
            )

            # Filter by city name in address
            city_companies = [
                c for c in companies
                if c.get('address') and city.lower() in c['address'].lower()
            ]

            results[city] = city_companies
            print(f"   Found {len(city_companies)} companies in {city}")

        return results

    def export_to_csv(self, leads: List[Dict], filename: str):
        """Export leads to CSV"""
        df = pd.DataFrame(leads)
        df.to_csv(filename, index=False)
        print(f"💾 Exported {len(leads)} Indian companies to {filename}")


if __name__ == "__main__":
    # Demo
    extractor = IndiaExtractor()

    print("🎯 DEMO: Extracting Indian Companies")
    print("=" * 60)

    # Extract FMCG companies
    print("\n1. FMCG Companies:")
    fmcg = extractor.extract_fmcg_companies(limit=10)

    for i, company in enumerate(fmcg[:5], 1):
        print(f"\n{i}. {company['company_name']}")
        print(f"   State: {company['state']}")
        print(f"   Status: {company['status']}")

    # Extract E-commerce companies
    print("\n\n2. E-commerce Companies:")
    ecommerce = extractor.extract_ecommerce_companies(limit=10)

    for i, company in enumerate(ecommerce[:3], 1):
        print(f"\n{i}. {company['company_name']}")
        print(f"   State: {company['state']}")

    # Extract by state
    print("\n\n3. Maharashtra Companies:")
    maharashtra = extractor.extract_by_state(state="Maharashtra", industry="retail", limit=10)

    print(f"\nFound {len(maharashtra)} retail companies in Maharashtra")

    # Export
    all_companies = fmcg + ecommerce + maharashtra
    extractor.export_to_csv(all_companies, 'data/raw/india_companies.csv')

    print(f"\n✅ Total extracted: {len(all_companies)} Indian companies")
    print(f"💰 Cost: $0.00")
    print(f"⚖️  Legal: 100% (Public company registry data)")
