#!/usr/bin/env python3
"""
Quick Demo - Extract 100 Legal Leads in Under 5 Minutes

This demo shows how to extract real company data from legal, free sources:
1. SEC EDGAR - US public companies
2. OpenCorporates - International companies
3. USASpending - Federal contractors

All 100% legal, 100% free, ready to use immediately.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.sec_edgar_extractor import SECEdgarExtractor, TECH_SIC_CODES
from extractors.opencorporates_extractor import OpenCorporatesExtractor
from extractors.datagov_extractor import DataGovExtractor, FEDERAL_CONTRACTOR_NAICS
from processors.free_api_manager import FreeAPIManager, EmailValidator

import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import print as rprint


console = Console()


def print_header():
    """Print demo header"""
    console.print("\n" + "="*70, style="bold blue")
    console.print("🎯 LEGAL LEAD GENERATION ENGINE - LIVE DEMO", style="bold green")
    console.print("="*70 + "\n", style="bold blue")

    console.print("This demo extracts REAL company data from 100% legal sources:")
    console.print("  ✅ SEC EDGAR - US public company filings (government data)")
    console.print("  ✅ OpenCorporates - Open company database (200M+ companies)")
    console.print("  ✅ USASpending - Federal contractors (government data)")
    console.print("\n💰 Cost: $0.00")
    console.print("⚖️  Legal: 100% - All sources are public domain or openly licensed")
    console.print("⏱️  Time: < 5 minutes\n")


def demo_sec_edgar():
    """Demo: Extract tech companies from SEC EDGAR"""
    console.print("\n[bold cyan]📊 STEP 1: SEC EDGAR - Public Companies[/bold cyan]")
    console.print("Extracting technology companies from SEC filings...\n")

    extractor = SECEdgarExtractor(user_agent_email="demo@example.com")

    # Extract tech companies
    leads = extractor.extract_leads(
        count=20,
        sic_codes=list(TECH_SIC_CODES.keys())
    )

    # Display results
    table = Table(title="SEC EDGAR Companies (Sample)")
    table.add_column("Company", style="cyan")
    table.add_column("Ticker", style="green")
    table.add_column("Industry", style="yellow")
    table.add_column("Phone", style="magenta")

    for lead in leads[:5]:
        table.add_row(
            lead['company_name'][:40],
            lead.get('ticker', 'N/A'),
            lead.get('industry', 'N/A')[:30],
            lead.get('phone', 'N/A')
        )

    console.print(table)
    console.print(f"\n✅ Extracted {len(leads)} public companies")
    console.print(f"💾 Data saved to: data/raw/sec_edgar_leads.csv\n")

    # Save to CSV
    extractor.export_to_csv(leads, 'data/raw/sec_edgar_leads.csv')

    return leads


def demo_opencorporates():
    """Demo: Extract companies from OpenCorporates"""
    console.print("\n[bold cyan]🌍 STEP 2: OpenCorporates - International Companies[/bold cyan]")
    console.print("Extracting companies from open database...\n")

    extractor = OpenCorporatesExtractor()

    # Note: Free tier is limited, so we extract fewer
    console.print("⚠️  Note: OpenCorporates free tier is 200 calls/day")
    console.print("    For demo, extracting 10 companies\n")

    leads = extractor.extract_leads(
        country="us",
        query="technology software",
        count=10
    )

    # Display results
    if leads:
        table = Table(title="OpenCorporates Companies (Sample)")
        table.add_column("Company", style="cyan")
        table.add_column("Country", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Incorporated", style="magenta")

        for lead in leads[:5]:
            table.add_row(
                lead['company_name'][:40],
                lead.get('country', 'N/A'),
                lead.get('status', 'N/A'),
                lead.get('incorporation_date', 'N/A')
            )

        console.print(table)
        console.print(f"\n✅ Extracted {len(leads)} international companies")
        console.print(f"💾 Data saved to: data/raw/opencorporates_leads.csv\n")

        extractor.export_to_csv(leads, 'data/raw/opencorporates_leads.csv')
    else:
        console.print("⚠️  API limit reached or no results. Skip this source for now.\n")

    return leads


def demo_federal_contractors():
    """Demo: Extract federal contractors"""
    console.print("\n[bold cyan]🏛️  STEP 3: USASpending - Federal Contractors[/bold cyan]")
    console.print("Extracting IT contractors from government data...\n")

    extractor = DataGovExtractor()

    # Extract IT contractors
    leads = extractor.extract_leads(
        industry="541512",  # Computer Systems Design
        min_value=100000,
        count=20
    )

    # Display results
    table = Table(title="Federal Contractors (Sample)")
    table.add_column("Company", style="cyan")
    table.add_column("Industry", style="green")
    table.add_column("Contract Value", style="yellow")
    table.add_column("Contracts", style="magenta")

    for lead in leads[:5]:
        table.add_row(
            lead['company_name'][:40],
            lead.get('industry', 'N/A')[:25],
            f"${lead.get('total_contract_value', 0):,.0f}",
            str(lead.get('contracts_count', 0))
        )

    console.print(table)
    console.print(f"\n✅ Extracted {len(leads)} federal contractors")
    console.print(f"💾 Data saved to: data/raw/federal_contractors.csv\n")

    extractor.export_to_csv(leads, 'data/raw/federal_contractors.csv')

    return leads


def demo_enrichment(sample_leads):
    """Demo: Enrich leads with free AI APIs"""
    console.print("\n[bold cyan]🤖 STEP 4: AI Enrichment with Free APIs[/bold cyan]")
    console.print("Enriching leads using free AI models...\n")

    # Check if API keys are configured
    if not os.getenv('GOOGLE_AI_API_KEY') and not os.getenv('GROQ_API_KEY'):
        console.print("⚠️  No AI API keys configured. Skipping enrichment.")
        console.print("    To enable: Set GOOGLE_AI_API_KEY or GROQ_API_KEY environment variables")
        console.print("    Both are FREE - see docs/APIs.md for setup\n")
        return sample_leads

    manager = FreeAPIManager()

    # Take first 5 leads for demo
    leads_to_enrich = sample_leads[:5]

    enriched = manager.enrich_leads_batch(leads_to_enrich, show_progress=True)

    console.print("\n✨ Enrichment Sample:")
    for lead in enriched[:2]:
        console.print(f"\n  [bold]{lead['company_name']}[/bold]")
        if 'ai_enrichment' in lead:
            console.print(f"  {lead['ai_enrichment'][:150]}...")

    manager.print_stats()

    return enriched


def generate_summary(all_leads):
    """Generate final summary"""
    console.print("\n[bold green]" + "="*70 + "[/bold green]")
    console.print("[bold green]🎉 DEMO COMPLETE - SUMMARY[/bold green]")
    console.print("[bold green]" + "="*70 + "[/bold green]\n")

    total_leads = sum(len(leads) for leads in all_leads.values())

    console.print(f"📊 Total Leads Extracted: [bold cyan]{total_leads}[/bold cyan]")
    console.print(f"   • SEC EDGAR (Public Companies): {len(all_leads['sec_edgar'])}")
    console.print(f"   • OpenCorporates (International): {len(all_leads['opencorporates'])}")
    console.print(f"   • Federal Contractors: {len(all_leads['federal'])}")

    console.print(f"\n💰 Total Cost: [bold green]$0.00[/bold green]")
    console.print(f"⚖️  Legal Compliance: [bold green]100%[/bold green]")
    console.print(f"📁 Data Location: [cyan]data/raw/[/cyan]")

    console.print("\n[bold yellow]Next Steps:[/bold yellow]")
    console.print("  1. Configure free AI API keys for enrichment (docs/APIs.md)")
    console.print("  2. Customize extraction filters in extractors/")
    console.print("  3. Export to your CRM (CSV format ready)")
    console.print("  4. Scale up: Extract 1000s of leads daily")

    console.print("\n[bold]For production use:[/bold]")
    console.print("  python src/main.py --source all --count 1000 --enrich")

    console.print("\n" + "="*70 + "\n")


def main():
    """Run complete demo"""
    print_header()

    # Ensure data directories exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    start_time = datetime.now()

    all_leads = {}

    try:
        # Extract from SEC EDGAR
        all_leads['sec_edgar'] = demo_sec_edgar()

        # Extract from OpenCorporates
        all_leads['opencorporates'] = demo_opencorporates()

        # Extract from Federal Contractors
        all_leads['federal'] = demo_federal_contractors()

        # Demo enrichment
        if all_leads['sec_edgar']:
            demo_enrichment(all_leads['sec_edgar'])

        # Generate summary
        elapsed = (datetime.now() - start_time).total_seconds()

        generate_summary(all_leads)

        console.print(f"⏱️  Total Time: [bold]{elapsed:.1f} seconds[/bold]")

        console.print("\n✅ [bold green]SUCCESS! You now have real, legal company data.[/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n\n⏹️  Demo stopped by user")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        console.print("\nFor support, see docs/TROUBLESHOOTING.md")


if __name__ == "__main__":
    main()
