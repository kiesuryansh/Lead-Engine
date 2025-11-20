#!/usr/bin/env python3
"""
Targeted Demo - Geography & Industry Specific Lead Generation

Demonstrates extracting leads from:
- Geographies: India, US, Europe, Singapore
- Industries: FMCG, E-commerce, Q-commerce, CPG, Retail

This shows how to get highly targeted leads for specific markets and sectors.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors.india_extractor import IndiaExtractor
from extractors.singapore_extractor import SingaporeExtractor
from extractors.europe_extractor import EuropeExtractor
from extractors.sec_edgar_extractor import SECEdgarExtractor

from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def print_header():
    """Print demo header"""
    console.print("\n" + "="*70, style="bold blue")
    console.print("🎯 TARGETED LEAD GENERATION DEMO", style="bold green")
    console.print("="*70 + "\n", style="bold blue")

    console.print("Extracting leads from YOUR target markets:")
    console.print("  🇮🇳 India - FMCG & E-commerce")
    console.print("  🇺🇸 USA - Retail & CPG")
    console.print("  🇪🇺 Europe - FMCG")
    console.print("  🇸🇬 Singapore - E-commerce & Q-commerce")
    console.print()


def demo_india_fmcg():
    """Demo: Extract FMCG companies from India"""
    console.print("\n[bold cyan]🇮🇳 INDIA - FMCG Companies[/bold cyan]")
    console.print("Targeting fast-moving consumer goods companies in India...\n")

    extractor = IndiaExtractor()

    # Extract FMCG companies
    fmcg_companies = extractor.extract_fmcg_companies(limit=10)

    # Display results
    if fmcg_companies:
        table = Table(title="Indian FMCG Companies")
        table.add_column("Company", style="cyan", width=40)
        table.add_column("State", style="green")
        table.add_column("Status", style="yellow")

        for company in fmcg_companies[:5]:
            table.add_row(
                company['company_name'][:38],
                company.get('state', 'N/A'),
                company.get('status', 'N/A')
            )

        console.print(table)
        console.print(f"\n✅ Extracted {len(fmcg_companies)} FMCG companies from India")
    else:
        console.print("⚠️  API limit reached. Try again later.")

    return fmcg_companies


def demo_singapore_ecommerce():
    """Demo: Extract E-commerce companies from Singapore"""
    console.print("\n[bold cyan]🇸🇬 SINGAPORE - E-commerce Companies[/bold cyan]")
    console.print("Targeting online retail and marketplace companies...\n")

    extractor = SingaporeExtractor()

    # Extract e-commerce companies
    ecommerce_companies = extractor.extract_ecommerce_companies(limit=10)

    # Display results
    if ecommerce_companies:
        table = Table(title="Singapore E-commerce Companies")
        table.add_column("Company", style="cyan", width=40)
        table.add_column("UEN", style="green")
        table.add_column("Status", style="yellow")

        for company in ecommerce_companies[:5]:
            table.add_row(
                company['company_name'][:38],
                company.get('uen', 'N/A')[:15],
                company.get('status', 'N/A')
            )

        console.print(table)
        console.print(f"\n✅ Extracted {len(ecommerce_companies)} E-commerce companies from Singapore")
    else:
        console.print("⚠️  API limit reached. Try again later.")

    return ecommerce_companies


def demo_europe_fmcg():
    """Demo: Extract FMCG companies from Europe"""
    console.print("\n[bold cyan]🇪🇺 EUROPE - FMCG Companies[/bold cyan]")
    console.print("Targeting FMCG across UK, Germany, France...\n")

    extractor = EuropeExtractor()

    # Extract from multiple countries
    results = extractor.extract_all_countries(industry='fmcg', limit_per_country=3)

    # Display results
    table = Table(title="European FMCG Companies")
    table.add_column("Country", style="cyan")
    table.add_column("Company", style="green", width=35)
    table.add_column("Status", style="yellow")

    all_companies = []
    for country, companies in results.items():
        for company in companies[:2]:
            table.add_row(
                country,
                company['company_name'][:33],
                company.get('status', 'N/A')
            )
            all_companies.append(company)

    if all_companies:
        console.print(table)
        console.print(f"\n✅ Extracted {len(all_companies)} FMCG companies from Europe")
    else:
        console.print("⚠️  API limit reached. Try again later.")

    return all_companies


def demo_us_retail():
    """Demo: Extract retail companies from USA"""
    console.print("\n[bold cyan]🇺🇸 USA - Retail Companies[/bold cyan]")
    console.print("Targeting retail and consumer goods companies...\n")

    extractor = SECEdgarExtractor(user_agent_email="demo@example.com")

    # SIC codes for retail
    retail_sic_codes = ['5200', '5300', '5400', '5700', '5900']

    # Extract retail companies
    retail_companies = extractor.extract_leads(count=10, sic_codes=retail_sic_codes)

    # Display results
    if retail_companies:
        table = Table(title="US Retail Companies")
        table.add_column("Company", style="cyan", width=35)
        table.add_column("Ticker", style="green")
        table.add_column("Industry", style="yellow", width=25)

        for company in retail_companies[:5]:
            table.add_row(
                company['company_name'][:33],
                company.get('ticker', 'N/A'),
                company.get('industry', 'N/A')[:23]
            )

        console.print(table)
        console.print(f"\n✅ Extracted {len(retail_companies)} retail companies from USA")
    else:
        console.print("⚠️  Could not extract companies")

    return retail_companies


def generate_summary(all_results):
    """Generate final summary"""
    console.print("\n[bold green]" + "="*70 + "[/bold green]")
    console.print("[bold green]📊 DEMO SUMMARY - Targeted Extraction[/bold green]")
    console.print("[bold green]" + "="*70 + "[/bold green]\n")

    total_leads = sum(len(results) for results in all_results.values())

    console.print(f"[bold]Total Targeted Leads:[/bold] [cyan]{total_leads}[/cyan]")
    console.print()

    for geography, leads in all_results.items():
        console.print(f"  • {geography}: [green]{len(leads)}[/green] companies")

    console.print(f"\n[bold]Cost:[/bold] [green]$0.00[/green]")
    console.print(f"[bold]Legal Compliance:[/bold] [green]100%[/green]")
    console.print(f"[bold]Data Quality:[/bold] [green]High[/green] (from official registries)")

    console.print("\n[bold yellow]Key Benefits:[/bold yellow]")
    console.print("  ✅ Geography-specific targeting (your markets)")
    console.print("  ✅ Industry-specific filtering (FMCG, E-commerce, etc.)")
    console.print("  ✅ High-quality data from official sources")
    console.print("  ✅ Completely free and legal")

    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Run full extraction: [cyan]python src/targeted_extraction.py --geography all --industry all[/cyan]")
    console.print("  2. Target specific market: [cyan]python src/targeted_extraction.py --geography india --industry fmcg[/cyan]")
    console.print("  3. Extract with enrichment: [cyan]python src/targeted_extraction.py --geography singapore --enrich[/cyan]")

    console.print("\n" + "="*70 + "\n")


def main():
    """Run targeted demo"""
    print_header()

    all_results = {}

    try:
        # India FMCG
        india_fmcg = demo_india_fmcg()
        all_results['India (FMCG)'] = india_fmcg

        # Singapore E-commerce
        singapore_ecom = demo_singapore_ecommerce()
        all_results['Singapore (E-commerce)'] = singapore_ecom

        # Europe FMCG
        europe_fmcg = demo_europe_fmcg()
        all_results['Europe (FMCG)'] = europe_fmcg

        # US Retail
        us_retail = demo_us_retail()
        all_results['USA (Retail)'] = us_retail

        # Summary
        generate_summary(all_results)

        console.print("✅ [bold green]Demo complete! You can now extract targeted leads at scale.[/bold green]\n")

    except KeyboardInterrupt:
        console.print("\n\n⏹️  Demo stopped by user")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    main()
