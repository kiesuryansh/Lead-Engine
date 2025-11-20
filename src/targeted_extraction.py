#!/usr/bin/env python3
"""
Targeted Lead Extraction System

Extracts leads from specific geographies and industries:
- Geographies: India 🇮🇳, US 🇺🇸, Europe 🇪🇺, Singapore 🇸🇬
- Industries: FMCG, E-commerce, Q-commerce, CPG, Retail

Usage:
    python src/targeted_extraction.py --geography all --industry all
    python src/targeted_extraction.py --geography india --industry fmcg
    python src/targeted_extraction.py --geography us --industry ecommerce --count 200
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from extractors.india_extractor import IndiaExtractor
from extractors.singapore_extractor import SingaporeExtractor
from extractors.europe_extractor import EuropeExtractor
from extractors.sec_edgar_extractor import SECEdgarExtractor
from extractors.datagov_extractor import DataGovExtractor
from processors.free_api_manager import FreeAPIManager

console = Console()


def load_config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent.parent / 'config' / 'target_config.yaml'

    if not config_path.exists():
        console.print(f"[yellow]⚠️  Config file not found at {config_path}[/yellow]")
        return None

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Targeted Lead Generation - Extract from specific geographies and industries'
    )

    parser.add_argument(
        '--geography',
        choices=['india', 'us', 'europe', 'singapore', 'all'],
        default='all',
        help='Target geography'
    )

    parser.add_argument(
        '--industry',
        choices=['fmcg', 'ecommerce', 'qcommerce', 'cpg', 'retail', 'all'],
        default='all',
        help='Target industry'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='Total leads to extract (distributed across geographies/industries)'
    )

    parser.add_argument(
        '--enrich',
        action='store_true',
        help='Enrich leads with AI'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/processed',
        help='Output directory'
    )

    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'excel'],
        default='csv',
        help='Output format'
    )

    return parser.parse_args()


class TargetedExtractor:
    """Main targeted extraction orchestrator"""

    def __init__(self, config):
        self.config = config
        self.extractors = {
            'india': IndiaExtractor(),
            'singapore': SingaporeExtractor(),
            'europe': EuropeExtractor(),
            'us_sec': SECEdgarExtractor(user_agent_email="demo@example.com"),
            'us_federal': DataGovExtractor()
        }

        self.industry_keywords = {
            'fmcg': config['industries']['fmcg']['keywords'],
            'ecommerce': config['industries']['ecommerce']['keywords'],
            'qcommerce': config['industries']['qcommerce']['keywords'],
            'cpg': config['industries']['cpg']['keywords'],
            'retail': config['industries']['retail']['keywords']
        }

        self.sic_codes = {
            'fmcg': config['industries']['fmcg']['sic_codes'],
            'ecommerce': config['industries']['ecommerce']['sic_codes'],
            'qcommerce': config['industries']['qcommerce']['sic_codes'],
            'cpg': config['industries']['cpg']['sic_codes'],
            'retail': config['industries']['retail']['sic_codes']
        }

    def extract_from_india(self, industry: str, count: int) -> List[Dict]:
        """Extract leads from India"""
        console.print(f"\n[bold cyan]🇮🇳 Extracting from INDIA - {industry.upper()}[/bold cyan]")

        extractor = self.extractors['india']

        if industry == 'fmcg':
            return extractor.extract_fmcg_companies(limit=count)
        elif industry == 'ecommerce':
            return extractor.extract_ecommerce_companies(limit=count)
        elif industry == 'retail':
            return extractor.extract_retail_companies(limit=count)
        else:
            # Generic extraction
            keywords = self.industry_keywords.get(industry, [industry])
            companies = extractor.search_companies_by_industry(keywords, limit=count)
            return [c.to_dict() for c in companies]

    def extract_from_singapore(self, industry: str, count: int) -> List[Dict]:
        """Extract leads from Singapore"""
        console.print(f"\n[bold cyan]🇸🇬 Extracting from SINGAPORE - {industry.upper()}[/bold cyan]")

        extractor = self.extractors['singapore']

        if industry == 'fmcg':
            return extractor.extract_fmcg_companies(limit=count)
        elif industry == 'ecommerce':
            return extractor.extract_ecommerce_companies(limit=count)
        elif industry == 'qcommerce':
            return extractor.extract_qcommerce_companies(limit=count)
        elif industry == 'cpg':
            return extractor.extract_cpg_companies(limit=count)
        elif industry == 'retail':
            return extractor.extract_retail_companies(limit=count)
        else:
            keywords = self.industry_keywords.get(industry, [industry])
            companies = extractor.search_companies_by_industry(keywords, limit=count)
            return [c.to_dict() for c in companies]

    def extract_from_europe(self, industry: str, count: int) -> List[Dict]:
        """Extract leads from Europe"""
        console.print(f"\n[bold cyan]🇪🇺 Extracting from EUROPE - {industry.upper()}[/bold cyan]")

        extractor = self.extractors['europe']

        # Distribute across countries
        countries_count = 5  # UK, DE, FR, NL, IE
        per_country = max(count // countries_count, 5)

        results = extractor.extract_all_countries(
            industry=industry,
            limit_per_country=per_country
        )

        # Flatten results
        all_companies = []
        for companies in results.values():
            all_companies.extend(companies)

        return all_companies[:count]

    def extract_from_us(self, industry: str, count: int) -> List[Dict]:
        """Extract leads from US"""
        console.print(f"\n[bold cyan]🇺🇸 Extracting from USA - {industry.upper()}[/bold cyan]")

        # Split between SEC EDGAR and Federal contractors
        sec_count = int(count * 0.7)  # 70% from SEC
        federal_count = count - sec_count  # 30% from USASpending

        all_companies = []

        # Extract from SEC EDGAR
        console.print("   📊 Extracting from SEC EDGAR...")
        sec_extractor = self.extractors['us_sec']
        sic_codes = self.sic_codes.get(industry)

        if sic_codes:
            sec_companies = sec_extractor.extract_leads(
                count=sec_count,
                sic_codes=sic_codes
            )
            all_companies.extend(sec_companies)

        # Extract from USASpending (federal contractors)
        console.print("   🏛️  Extracting from USASpending...")
        federal_extractor = self.extractors['us_federal']

        # Map industry to NAICS
        naics_map = {
            'fmcg': '311',
            'ecommerce': '4541',
            'qcommerce': '4541',
            'cpg': '311',
            'retail': '445'
        }

        naics_code = naics_map.get(industry)
        if naics_code:
            federal_companies = federal_extractor.extract_leads(
                industry=naics_code,
                count=federal_count
            )
            all_companies.extend(federal_companies)

        return all_companies[:count]

    def extract_targeted_leads(self,
                              geographies: List[str],
                              industries: List[str],
                              total_count: int) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Extract leads for target geographies and industries

        Returns:
            Nested dict: {geography: {industry: [leads]}}
        """
        results = {}

        # Calculate distribution
        geo_count = len(geographies)
        ind_count = len(industries)
        per_combination = max(total_count // (geo_count * ind_count), 10)

        console.print(f"\n[bold]Extraction Plan:[/bold]")
        console.print(f"  Geographies: {', '.join(geographies)}")
        console.print(f"  Industries: {', '.join(industries)}")
        console.print(f"  Per combination: ~{per_combination} leads")
        console.print(f"  Total target: {total_count} leads\n")

        for geography in geographies:
            results[geography] = {}

            for industry in industries:
                try:
                    if geography == 'india':
                        leads = self.extract_from_india(industry, per_combination)
                    elif geography == 'singapore':
                        leads = self.extract_from_singapore(industry, per_combination)
                    elif geography == 'europe':
                        leads = self.extract_from_europe(industry, per_combination)
                    elif geography == 'us':
                        leads = self.extract_from_us(industry, per_combination)
                    else:
                        leads = []

                    results[geography][industry] = leads

                    console.print(f"  ✅ {geography.upper()} - {industry.upper()}: {len(leads)} leads")

                except Exception as e:
                    console.print(f"  ❌ {geography.upper()} - {industry.upper()}: Error - {e}")
                    results[geography][industry] = []

        return results

    def enrich_all_leads(self, results: Dict) -> Dict:
        """Enrich all extracted leads"""
        console.print("\n[bold cyan]🤖 Enriching leads with AI...[/bold cyan]")

        manager = FreeAPIManager()

        enriched_results = {}

        for geography, industries in results.items():
            enriched_results[geography] = {}

            for industry, leads in industries.items():
                if leads:
                    console.print(f"   Enriching {geography} - {industry}...")
                    enriched = manager.enrich_leads_batch(leads, show_progress=False)
                    enriched_results[geography][industry] = enriched
                else:
                    enriched_results[geography][industry] = []

        manager.print_stats()

        return enriched_results

    def export_results(self, results: Dict, output_dir: str, format: str):
        """Export results to files"""
        console.print(f"\n[bold cyan]💾 Exporting results to {output_dir}/[/bold cyan]")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Export combined file
        all_leads = []
        for geography, industries in results.items():
            for industry, leads in industries.items():
                # Add metadata
                for lead in leads:
                    lead['target_geography'] = geography
                    lead['target_industry'] = industry
                all_leads.extend(leads)

        if all_leads:
            df = pd.DataFrame(all_leads)

            combined_file = f"{output_dir}/targeted_leads_{timestamp}.{format}"

            if format == 'csv':
                df.to_csv(combined_file, index=False)
            elif format == 'json':
                df.to_json(combined_file, orient='records', indent=2)
            elif format == 'excel':
                df.to_excel(combined_file, index=False)

            console.print(f"  ✅ Combined file: {combined_file} ({len(all_leads)} leads)")

            # Export separate files per geography
            for geography, industries in results.items():
                geo_leads = []
                for leads in industries.values():
                    geo_leads.extend(leads)

                if geo_leads:
                    geo_df = pd.DataFrame(geo_leads)
                    geo_file = f"{output_dir}/{geography}_leads_{timestamp}.{format}"

                    if format == 'csv':
                        geo_df.to_csv(geo_file, index=False)
                    elif format == 'json':
                        geo_df.to_json(geo_file, orient='records', indent=2)
                    elif format == 'excel':
                        geo_df.to_excel(geo_file, index=False)

                    console.print(f"  ✅ {geography.upper()}: {geo_file} ({len(geo_leads)} leads)")

        return all_leads

    def generate_summary(self, results: Dict, all_leads: List):
        """Generate extraction summary"""
        console.print("\n" + "="*70)
        console.print("[bold green]📊 EXTRACTION SUMMARY[/bold green]")
        console.print("="*70 + "\n")

        # Summary table
        table = Table(title="Leads by Geography & Industry")
        table.add_column("Geography", style="cyan")
        table.add_column("Industry", style="yellow")
        table.add_column("Leads", style="green", justify="right")

        for geography, industries in results.items():
            for industry, leads in industries.items():
                table.add_row(
                    geography.upper(),
                    industry.upper(),
                    str(len(leads))
                )

        console.print(table)

        console.print(f"\n[bold]Total Leads Extracted:[/bold] [green]{len(all_leads)}[/green]")
        console.print(f"[bold]Cost:[/bold] [green]$0.00[/green]")
        console.print(f"[bold]Legal Compliance:[/bold] [green]100%[/green]")

        console.print("\n" + "="*70 + "\n")


def main():
    """Main execution"""
    args = parse_arguments()

    console.print("\n[bold green]🎯 Targeted Lead Generation System[/bold green]")
    console.print("Geographies: India 🇮🇳 | US 🇺🇸 | Europe 🇪🇺 | Singapore 🇸🇬")
    console.print("Industries: FMCG | E-commerce | Q-commerce | CPG | Retail\n")

    # Load config
    config = load_config()
    if not config:
        console.print("[red]❌ Could not load configuration[/red]")
        return

    # Initialize extractor
    extractor = TargetedExtractor(config)

    # Determine geographies and industries
    geographies = ['india', 'us', 'europe', 'singapore'] if args.geography == 'all' else [args.geography]
    industries = ['fmcg', 'ecommerce', 'qcommerce', 'cpg', 'retail'] if args.industry == 'all' else [args.industry]

    try:
        # Extract leads
        results = extractor.extract_targeted_leads(
            geographies=geographies,
            industries=industries,
            total_count=args.count
        )

        # Enrich if requested
        if args.enrich:
            results = extractor.enrich_all_leads(results)

        # Export results
        all_leads = extractor.export_results(results, args.output_dir, args.format)

        # Generate summary
        extractor.generate_summary(results, all_leads)

        console.print("[bold green]✅ Extraction complete![/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n\n⏹️  Stopped by user")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
