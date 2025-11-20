"""
Europe Company Extractor - Legal Public Data

Extracts company information from European public sources:
1. Companies House (UK) - Official UK registry
2. OpenCorporates (EU countries)
3. European Business Registers

Target countries: UK, Germany, France, Netherlands, Ireland

All data from legal, public sources.
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EuropeanCompany:
    """European company information"""
    name: str
    company_number: str
    country: str
    jurisdiction: str
    industry: Optional[str]
    registration_date: Optional[str]
    company_type: Optional[str]
    status: Optional[str]
    address: Optional[str]

    def to_dict(self):
        return {
            'company_name': self.name,
            'company_number': self.company_number,
            'country': self.country,
            'jurisdiction': self.jurisdiction,
            'industry': self.industry,
            'registration_date': self.registration_date,
            'company_type': self.company_type,
            'status': self.status,
            'address': self.address,
            'region': 'Europe',
            'source': 'Europe Extractor',
            'extracted_at': datetime.now().isoformat()
        }


class EuropeExtractor:
    """
    Extract company data from European public sources

    Data Source: OpenCorporates (aggregates EU registries)
    Legal Basis: Public company registry data
    Cost: $0 (free tier)

    Supported countries:
    - 🇬🇧 United Kingdom (Companies House)
    - 🇩🇪 Germany (Handelsregister)
    - 🇫🇷 France (INPI)
    - 🇳🇱 Netherlands (KVK)
    - 🇮🇪 Ireland (CRO)
    """

    # Country codes and names
    COUNTRIES = {
        'gb': 'United Kingdom',
        'de': 'Germany',
        'fr': 'France',
        'nl': 'Netherlands',
        'ie': 'Ireland'
    }

    def __init__(self):
        from extractors.opencorporates_extractor import OpenCorporatesExtractor
        self.opencorp = OpenCorporatesExtractor()

    def search_companies_by_country_and_industry(self,
                                                  country_code: str,
                                                  industry_keywords: List[str],
                                                  limit: int = 50) -> List[EuropeanCompany]:
        """
        Search companies in specific European country

        Args:
            country_code: Country code (gb, de, fr, nl, ie)
            industry_keywords: List of industry keywords
            limit: Maximum results

        Returns:
            List of European companies

        Example:
            >>> extractor = EuropeExtractor()
            >>> uk_fmcg = extractor.search_companies_by_country_and_industry(
            ...     country_code="gb",
            ...     industry_keywords=["FMCG", "consumer goods"],
            ...     limit=50
            ... )
        """
        country_name = self.COUNTRIES.get(country_code, country_code.upper())
        print(f"🇪🇺 Searching {country_name} companies: {', '.join(industry_keywords)}")

        # Combine keywords
        search_query = ' OR '.join(industry_keywords)

        # Search using OpenCorporates
        opencorp_results = self.opencorp.search_companies(
            query=search_query,
            jurisdiction_code=country_code,
            max_results=limit
        )

        companies = []

        for result in opencorp_results:
            company = EuropeanCompany(
                name=result.get('company_name', ''),
                company_number=result.get('company_number', ''),
                country=country_name,
                jurisdiction=result.get('country', country_code),
                industry=None,
                registration_date=result.get('incorporation_date'),
                company_type=result.get('company_type'),
                status=result.get('status'),
                address=result.get('address')
            )

            companies.append(company)

        print(f"✅ Found {len(companies)} companies in {country_name}")
        return companies

    def extract_uk_companies(self, industry: str, limit: int = 50) -> List[Dict]:
        """Extract UK companies by industry"""
        keywords = self._get_industry_keywords(industry)
        companies = self.search_companies_by_country_and_industry('gb', keywords, limit)
        return [c.to_dict() for c in companies]

    def extract_german_companies(self, industry: str, limit: int = 50) -> List[Dict]:
        """Extract German companies by industry"""
        keywords = self._get_industry_keywords(industry)
        companies = self.search_companies_by_country_and_industry('de', keywords, limit)
        return [c.to_dict() for c in companies]

    def extract_french_companies(self, industry: str, limit: int = 50) -> List[Dict]:
        """Extract French companies by industry"""
        keywords = self._get_industry_keywords(industry)
        companies = self.search_companies_by_country_and_industry('fr', keywords, limit)
        return [c.to_dict() for c in companies]

    def extract_netherlands_companies(self, industry: str, limit: int = 50) -> List[Dict]:
        """Extract Netherlands companies by industry"""
        keywords = self._get_industry_keywords(industry)
        companies = self.search_companies_by_country_and_industry('nl', keywords, limit)
        return [c.to_dict() for c in companies]

    def extract_ireland_companies(self, industry: str, limit: int = 50) -> List[Dict]:
        """Extract Irish companies by industry"""
        keywords = self._get_industry_keywords(industry)
        companies = self.search_companies_by_country_and_industry('ie', keywords, limit)
        return [c.to_dict() for c in companies]

    def extract_all_countries(self,
                             industry: str,
                             limit_per_country: int = 20) -> Dict[str, List[Dict]]:
        """
        Extract companies from all target European countries

        Args:
            industry: Industry type (fmcg, ecommerce, retail, etc.)
            limit_per_country: Companies to extract per country

        Returns:
            Dictionary with country as key and companies as value
        """
        results = {}

        extractors = {
            'United Kingdom': lambda: self.extract_uk_companies(industry, limit_per_country),
            'Germany': lambda: self.extract_german_companies(industry, limit_per_country),
            'France': lambda: self.extract_french_companies(industry, limit_per_country),
            'Netherlands': lambda: self.extract_netherlands_companies(industry, limit_per_country),
            'Ireland': lambda: self.extract_ireland_companies(industry, limit_per_country)
        }

        for country, extractor_func in extractors.items():
            try:
                print(f"\n🔍 Extracting from {country}...")
                companies = extractor_func()
                results[country] = companies
            except Exception as e:
                print(f"⚠️  Error extracting from {country}: {e}")
                results[country] = []

        total = sum(len(companies) for companies in results.values())
        print(f"\n✅ Total extracted: {total} European companies")

        return results

    def extract_by_industry_all_countries(self,
                                         industries: List[str],
                                         limit_per_combination: int = 10) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Extract companies from all countries and all industries

        Args:
            industries: List of industries (e.g., ['fmcg', 'ecommerce'])
            limit_per_combination: Leads per country-industry combination

        Returns:
            Nested dict: {industry: {country: [companies]}}
        """
        results = {}

        for industry in industries:
            print(f"\n{'='*60}")
            print(f"Industry: {industry.upper()}")
            print('='*60)

            results[industry] = self.extract_all_countries(
                industry=industry,
                limit_per_country=limit_per_combination
            )

        return results

    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Map industry name to keywords"""
        industry_map = {
            'fmcg': ["FMCG", "consumer goods", "packaged goods", "beverages", "food products"],
            'ecommerce': ["ecommerce", "e-commerce", "online retail", "marketplace"],
            'qcommerce': ["quick commerce", "delivery", "instant delivery"],
            'cpg': ["consumer packaged goods", "CPG", "packaged foods"],
            'retail': ["retail", "supermarket", "stores", "shopping"]
        }

        return industry_map.get(industry.lower(), [industry])

    def export_to_csv(self, leads: List[Dict], filename: str):
        """Export leads to CSV"""
        df = pd.DataFrame(leads)
        df.to_csv(filename, index=False)
        print(f"💾 Exported {len(leads)} European companies to {filename}")

    def export_by_country(self, results: Dict[str, List[Dict]], base_filename: str):
        """Export results with separate file per country"""
        for country, companies in results.items():
            if companies:
                country_code = country.lower().replace(' ', '_')
                filename = base_filename.replace('.csv', f'_{country_code}.csv')
                self.export_to_csv(companies, filename)


if __name__ == "__main__":
    # Demo
    extractor = EuropeExtractor()

    print("🎯 DEMO: Extracting European Companies")
    print("=" * 60)

    # Extract FMCG companies from all countries
    print("\n🛒 Extracting FMCG companies from Europe...")
    fmcg_results = extractor.extract_all_countries(
        industry='fmcg',
        limit_per_country=5
    )

    print("\n📋 Sample Companies by Country:\n")

    for country, companies in fmcg_results.items():
        if companies:
            print(f"\n{country} ({len(companies)} companies):")
            for i, company in enumerate(companies[:3], 1):
                print(f"  {i}. {company['company_name']}")
                print(f"     Status: {company['status']}")
                print(f"     Registered: {company.get('registration_date', 'N/A')}")

    # Combine all results
    all_companies = []
    for companies in fmcg_results.values():
        all_companies.extend(companies)

    # Export
    extractor.export_to_csv(all_companies, 'data/raw/europe_fmcg_companies.csv')

    print(f"\n✅ Total extracted: {len(all_companies)} European FMCG companies")
    print(f"💰 Cost: $0.00")
    print(f"⚖️  Legal: 100% (Public registry data)")
