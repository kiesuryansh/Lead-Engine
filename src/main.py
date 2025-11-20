#!/usr/bin/env python3
"""
Main Entry Point - Legal Lead Generation Engine

Extract leads from multiple free, legal sources.

Usage:
    python src/main.py --count 100 --source sec_edgar
    python src/main.py --count 500 --source all --enrich
    python src/main.py --industry software --count 200
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from extractors.sec_edgar_extractor import SECEdgarExtractor, TECH_SIC_CODES
from extractors.opencorporates_extractor import OpenCorporatesExtractor
from extractors.datagov_extractor import DataGovExtractor, FEDERAL_CONTRACTOR_NAICS
from processors.free_api_manager import FreeAPIManager

console = Console()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Legal Lead Generation Engine - Extract company data from free sources'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='Number of leads to extract (default: 100)'
    )

    parser.add_argument(
        '--source',
        choices=['sec_edgar', 'opencorporates', 'usaspending', 'all'],
        default='sec_edgar',
        help='Data source to use (default: sec_edgar)'
    )

    parser.add_argument(
        '--industry',
        type=str,
        help='Industry filter (SIC code or keyword)'
    )

    parser.add_argument(
        '--country',
        type=str,
        default='us',
        help='Country code for OpenCorporates (default: us)'
    )

    parser.add_argument(
        '--enrich',
        action='store_true',
        help='Enrich leads with AI (requires API keys)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='data/processed/leads.csv',
        help='Output CSV file path'
    )

    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'excel'],
        default='csv',
        help='Output format (default: csv)'
    )

    return parser.parse_args()


def extract_from_sec_edgar(count: int, industry: str = None):
    """Extract leads from SEC EDGAR"""
    console.print("\n[bold cyan]📊 Extracting from SEC EDGAR[/bold cyan]")

    extractor = SECEdgarExtractor(user_agent_email="demo@example.com")

    # Determine SIC codes
    sic_codes = None
    if industry:
        if industry.lower() == 'tech' or industry.lower() == 'technology':
            sic_codes = list(TECH_SIC_CODES.keys())
        elif industry.isdigit():
            sic_codes = [industry]

    leads = extractor.extract_leads(count=count, sic_codes=sic_codes)

    console.print(f"✅ Extracted {len(leads)} companies from SEC EDGAR")
    return leads


def extract_from_opencorporates(count: int, country: str, industry: str = None):
    """Extract leads from OpenCorporates"""
    console.print("\n[bold cyan]🌍 Extracting from OpenCorporates[/bold cyan]")

    extractor = OpenCorporatesExtractor()

    leads = extractor.extract_leads(
        country=country,
        query=industry,
        count=count
    )

    console.print(f"✅ Extracted {len(leads)} companies from OpenCorporates")
    return leads


def extract_from_usaspending(count: int, industry: str = None):
    """Extract leads from USASpending"""
    console.print("\n[bold cyan]🏛️  Extracting from USASpending[/bold cyan]")

    extractor = DataGovExtractor()

    # Determine NAICS code
    naics_code = None
    if industry:
        if industry.lower() == 'tech' or industry.lower() == 'technology':
            naics_code = "541512"  # Computer Systems Design
        elif industry.isdigit() and len(industry) == 6:
            naics_code = industry

    leads = extractor.extract_leads(
        industry=naics_code,
        min_value=0,
        count=count
    )

    console.print(f"✅ Extracted {len(leads)} contractors from USASpending")
    return leads


def enrich_leads(leads):
    """Enrich leads with AI"""
    console.print("\n[bold cyan]🤖 Enriching leads with AI[/bold cyan]")

    manager = FreeAPIManager()
    enriched = manager.enrich_leads_batch(leads, show_progress=True)

    # Print cost report
    cost_report = manager.get_cost_report()
    console.print(f"\n💰 Enrichment cost: ${cost_report['total_cost']:.2f}")

    return enriched


def save_leads(leads, output_path: str, format: str):
    """Save leads to file"""
    console.print(f"\n[bold cyan]💾 Saving to {output_path}[/bold cyan]")

    df = pd.DataFrame(leads)

    # Add metadata
    df['extracted_at'] = datetime.now().isoformat()
    df['tool'] = 'Legal Lead Generation Engine'

    # Save in requested format
    if format == 'csv':
        df.to_csv(output_path, index=False)
    elif format == 'json':
        output_path = output_path.replace('.csv', '.json')
        df.to_json(output_path, orient='records', indent=2)
    elif format == 'excel':
        output_path = output_path.replace('.csv', '.xlsx')
        df.to_excel(output_path, index=False)

    console.print(f"✅ Saved {len(leads)} leads to {output_path}")


def main():
    """Main execution"""
    args = parse_arguments()

    console.print("\n[bold green]🎯 Legal Lead Generation Engine[/bold green]")
    console.print(f"Target: {args.count} leads from {args.source}")
    console.print(f"Industry: {args.industry or 'All'}")
    console.print(f"Enrichment: {'Enabled' if args.enrich else 'Disabled'}")
    console.print()

    all_leads = []

    try:
        # Extract from sources
        if args.source == 'sec_edgar' or args.source == 'all':
            leads = extract_from_sec_edgar(args.count, args.industry)
            all_leads.extend(leads)

        if args.source == 'opencorporates' or args.source == 'all':
            count = args.count if args.source == 'opencorporates' else min(args.count // 3, 50)
            leads = extract_from_opencorporates(count, args.country, args.industry)
            all_leads.extend(leads)

        if args.source == 'usaspending' or args.source == 'all':
            count = args.count if args.source == 'usaspending' else args.count // 3
            leads = extract_from_usaspending(count, args.industry)
            all_leads.extend(leads)

        # Enrich if requested
        if args.enrich and all_leads:
            all_leads = enrich_leads(all_leads)

        # Save results
        if all_leads:
            save_leads(all_leads, args.output, args.format)

            # Summary
            console.print("\n[bold green]✅ Extraction Complete![/bold green]")
            console.print(f"Total leads: {len(all_leads)}")
            console.print(f"Output: {args.output}")
            console.print(f"Cost: $0.00")
        else:
            console.print("\n[yellow]⚠️  No leads extracted[/yellow]")

    except KeyboardInterrupt:
        console.print("\n\n⏹️  Stopped by user")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
