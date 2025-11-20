"""
Singapore Company Extractor - Legal Public Data

Extracts company information from Singapore public sources:
1. OpenCorporates (Singapore companies)
2. ACRA (Accounting and Corporate Regulatory Authority) public data

All data from legal, public sources.
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SingaporeCompany:
    """Singapore company information"""
    name: str
    uen: Optional[str]  # Unique Entity Number
    entity_type: Optional[str]
    industry: Optional[str]
    registration_date: Optional[str]
    status: Optional[str]
    address: Optional[str]

    def to_dict(self):
        return {
            'company_name': self.name,
            'uen': self.uen,
            'entity_type': self.entity_type,
            'industry': self.industry,
            'registration_date': self.registration_date,
            'status': self.status,
            'address': self.address,
            'country': 'Singapore',
            'source': 'Singapore Extractor',
            'extracted_at': datetime.now().isoformat()
        }


class SingaporeExtractor:
    """
    Extract company data from Singapore public sources

    Data Source: OpenCorporates (Singapore companies)
    Legal Basis: Publicly available company registry data
    Cost: $0 (free tier)

    Note: ACRA provides public data but requires registration for bulk access.
    This uses OpenCorporates which aggregates ACRA data.
    """

    def __init__(self):
        from extractors.opencorporates_extractor import OpenCorporatesExtractor
        self.opencorp = OpenCorporatesExtractor()

    def search_companies_by_industry(self,
                                     industry_keywords: List[str],
                                     limit: int = 100) -> List[SingaporeCompany]:
        """
        Search Singapore companies by industry

        Args:
            industry_keywords: List of keywords
            limit: Maximum results

        Returns:
            List of Singapore companies

        Example:
            >>> extractor = SingaporeExtractor()
            >>> ecommerce = extractor.search_companies_by_industry(
            ...     industry_keywords=["ecommerce", "online retail"],
            ...     limit=50
            ... )
        """
        print(f"🇸🇬 Searching Singapore companies: {', '.join(industry_keywords)}")

        # Combine keywords
        search_query = ' OR '.join(industry_keywords)

        # Search using OpenCorporates
        opencorp_results = self.opencorp.search_companies(
            query=search_query,
            jurisdiction_code="sg",
            max_results=limit
        )

        companies = []

        for result in opencorp_results:
            company = SingaporeCompany(
                name=result.get('company_name', ''),
                uen=result.get('company_number'),
                entity_type=result.get('company_type'),
                industry=None,
                registration_date=result.get('incorporation_date'),
                status=result.get('status'),
                address=result.get('address')
            )

            companies.append(company)

        print(f"✅ Found {len(companies)} Singapore companies")
        return companies

    def extract_fmcg_companies(self, limit: int = 50) -> List[Dict]:
        """Extract FMCG companies from Singapore"""
        keywords = [
            "FMCG", "consumer goods", "food products",
            "beverages", "personal care"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_ecommerce_companies(self, limit: int = 50) -> List[Dict]:
        """Extract E-commerce companies from Singapore"""
        keywords = [
            "ecommerce", "e-commerce", "online retail",
            "marketplace", "digital commerce"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_retail_companies(self, limit: int = 50) -> List[Dict]:
        """Extract retail companies from Singapore"""
        keywords = [
            "retail", "supermarket", "stores",
            "shopping", "mall"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_qcommerce_companies(self, limit: int = 50) -> List[Dict]:
        """Extract Quick Commerce companies from Singapore"""
        keywords = [
            "quick commerce", "delivery", "logistics",
            "instant delivery", "grocery delivery"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_cpg_companies(self, limit: int = 50) -> List[Dict]:
        """Extract CPG companies from Singapore"""
        keywords = [
            "consumer packaged goods", "CPG",
            "packaged foods", "household products"
        ]

        companies = self.search_companies_by_industry(keywords, limit=limit)
        return [c.to_dict() for c in companies]

    def extract_all_target_industries(self, limit_per_industry: int = 25) -> Dict[str, List[Dict]]:
        """
        Extract companies from all target industries

        Returns:
            Dictionary with industry as key and companies as value
        """
        results = {
            'FMCG': self.extract_fmcg_companies(limit_per_industry),
            'E-commerce': self.extract_ecommerce_companies(limit_per_industry),
            'Q-commerce': self.extract_qcommerce_companies(limit_per_industry),
            'CPG': self.extract_cpg_companies(limit_per_industry),
            'Retail': self.extract_retail_companies(limit_per_industry)
        }

        total = sum(len(companies) for companies in results.values())
        print(f"\n✅ Total extracted: {total} Singapore companies across {len(results)} industries")

        return results

    def export_to_csv(self, leads: List[Dict], filename: str):
        """Export leads to CSV"""
        df = pd.DataFrame(leads)
        df.to_csv(filename, index=False)
        print(f"💾 Exported {len(leads)} Singapore companies to {filename}")


if __name__ == "__main__":
    # Demo
    extractor = SingaporeExtractor()

    print("🎯 DEMO: Extracting Singapore Companies")
    print("=" * 60)

    # Extract from all industries
    results = extractor.extract_all_target_industries(limit_per_industry=5)

    print("\n📋 Sample Companies by Industry:\n")

    for industry, companies in results.items():
        print(f"\n{industry} ({len(companies)} companies):")
        for i, company in enumerate(companies[:3], 1):
            print(f"  {i}. {company['company_name']}")
            print(f"     Status: {company['status']}")

    # Combine and export
    all_companies = []
    for companies in results.values():
        all_companies.extend(companies)

    extractor.export_to_csv(all_companies, 'data/raw/singapore_companies.csv')

    print(f"\n✅ Total extracted: {len(all_companies)} Singapore companies")
    print(f"💰 Cost: $0.00")
    print(f"⚖️  Legal: 100% (Public registry data via OpenCorporates)")
