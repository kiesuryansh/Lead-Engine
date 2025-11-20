#!/usr/bin/env python3
"""
Targeted Lead Extraction with Progress Monitoring

Enhanced version with real-time progress tracking for dashboard monitoring.

Usage:
    python src/targeted_extraction_monitored.py --geography india --industry fmcg --count 100
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import pandas as pd
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from extractors.india_extractor import IndiaExtractor
from extractors.singapore_extractor import SingaporeExtractor
from extractors.europe_extractor import EuropeExtractor
from extractors.sec_edgar_extractor import SECEdgarExtractor
from extractors.datagov_extractor import DataGovExtractor
from processors.free_api_manager import FreeAPIManager
from core.progress_tracker import get_tracker, ExtractionJob, ExtractionProgress

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
        description='Targeted Lead Generation with Progress Monitoring'
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
        help='Total leads to extract'
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


class MonitoredExtractor:
    """Extraction with progress monitoring"""

    def __init__(self, config):
        self.config = config
        self.tracker = get_tracker()

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

    def extract_with_progress(self, geography: str, industry: str, count: int, job_id: str) -> List[Dict]:
        """Extract leads with progress tracking"""

        # Start job tracking
        job = ExtractionJob(
            job_id=job_id,
            geography=geography,
            industry=industry,
            target_count=count,
            status='running',
            extracted_count=0,
            started_at=datetime.now().isoformat()
        )

        self.tracker.start_job(job)

        leads = []

        try:
            # Extract based on geography
            if geography == 'india':
                leads = self._extract_india(industry, count, job_id)
            elif geography == 'singapore':
                leads = self._extract_singapore(industry, count, job_id)
            elif geography == 'europe':
                leads = self._extract_europe(industry, count, job_id)
            elif geography == 'us':
                leads = self._extract_us(industry, count, job_id)

            # Mark as completed
            self.tracker.complete_job(job_id, len(leads), 'completed')

        except Exception as e:
            self.tracker.complete_job(job_id, len(leads), 'failed', str(e))
            raise

        return leads

    def _extract_india(self, industry: str, count: int, job_id: str) -> List[Dict]:
        """Extract from India with progress"""
        console.print(f"\n[bold cyan]🇮🇳 Extracting from INDIA - {industry.upper()}[/bold cyan]")

        extractor = self.extractors['india']

        # Progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task(f"Extracting India {industry}", total=count)

            if industry == 'fmcg':
                leads = extractor.extract_fmcg_companies(limit=count)
            elif industry == 'ecommerce':
                leads = extractor.extract_ecommerce_companies(limit=count)
            elif industry == 'retail':
                leads = extractor.extract_retail_companies(limit=count)
            else:
                keywords = self.industry_keywords.get(industry, [industry])
                companies = extractor.search_companies_by_industry(keywords, limit=count)
                leads = [c.to_dict() for c in companies]

            # Update progress
            for i, lead in enumerate(leads, 1):
                progress.update(task, completed=i)

                # Log to tracker
                prog = ExtractionProgress(
                    job_id=job_id,
                    geography='india',
                    industry=industry,
                    current_count=i,
                    target_count=count,
                    percentage=(i / count) * 100,
                    status='running',
                    current_company=lead.get('company_name', ''),
                    timestamp=datetime.now().isoformat()
                )
                self.tracker.update_progress(prog)

                # Add to summary
                self.tracker.add_lead_summary(
                    job_id=job_id,
                    geography='india',
                    industry=industry,
                    company_name=lead.get('company_name', ''),
                    company_country=lead.get('country', 'India')
                )

        return leads

    def _extract_singapore(self, industry: str, count: int, job_id: str) -> List[Dict]:
        """Extract from Singapore with progress"""
        console.print(f"\n[bold cyan]🇸🇬 Extracting from SINGAPORE - {industry.upper()}[/bold cyan]")

        extractor = self.extractors['singapore']

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task(f"Extracting Singapore {industry}", total=count)

            if industry == 'fmcg':
                leads = extractor.extract_fmcg_companies(limit=count)
            elif industry == 'ecommerce':
                leads = extractor.extract_ecommerce_companies(limit=count)
            elif industry == 'qcommerce':
                leads = extractor.extract_qcommerce_companies(limit=count)
            elif industry == 'cpg':
                leads = extractor.extract_cpg_companies(limit=count)
            elif industry == 'retail':
                leads = extractor.extract_retail_companies(limit=count)
            else:
                keywords = self.industry_keywords.get(industry, [industry])
                companies = extractor.search_companies_by_industry(keywords, limit=count)
                leads = [c.to_dict() for c in companies]

            # Update progress
            for i, lead in enumerate(leads, 1):
                progress.update(task, completed=i)

                prog = ExtractionProgress(
                    job_id=job_id,
                    geography='singapore',
                    industry=industry,
                    current_count=i,
                    target_count=count,
                    percentage=(i / count) * 100,
                    status='running',
                    current_company=lead.get('company_name', ''),
                    timestamp=datetime.now().isoformat()
                )
                self.tracker.update_progress(prog)

                self.tracker.add_lead_summary(
                    job_id=job_id,
                    geography='singapore',
                    industry=industry,
                    company_name=lead.get('company_name', ''),
                    company_country=lead.get('country', 'Singapore')
                )

        return leads

    def _extract_europe(self, industry: str, count: int, job_id: str) -> List[Dict]:
        """Extract from Europe with progress"""
        console.print(f"\n[bold cyan]🇪🇺 Extracting from EUROPE - {industry.upper()}[/bold cyan]")

        extractor = self.extractors['europe']

        # Distribute across countries
        countries_count = 5
        per_country = max(count // countries_count, 5)

        results = extractor.extract_all_countries(
            industry=industry,
            limit_per_country=per_country
        )

        # Flatten and track progress
        all_companies = []
        for companies in results.values():
            all_companies.extend(companies)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task(f"Processing Europe {industry}", total=len(all_companies))

            for i, lead in enumerate(all_companies[:count], 1):
                progress.update(task, completed=i)

                prog = ExtractionProgress(
                    job_id=job_id,
                    geography='europe',
                    industry=industry,
                    current_count=i,
                    target_count=count,
                    percentage=(i / count) * 100,
                    status='running',
                    current_company=lead.get('company_name', ''),
                    timestamp=datetime.now().isoformat()
                )
                self.tracker.update_progress(prog)

                self.tracker.add_lead_summary(
                    job_id=job_id,
                    geography='europe',
                    industry=industry,
                    company_name=lead.get('company_name', ''),
                    company_country=lead.get('country', 'Europe')
                )

        return all_companies[:count]

    def _extract_us(self, industry: str, count: int, job_id: str) -> List[Dict]:
        """Extract from US with progress"""
        console.print(f"\n[bold cyan]🇺🇸 Extracting from USA - {industry.upper()}[/bold cyan]")

        sec_count = int(count * 0.7)
        federal_count = count - sec_count

        all_companies = []

        # SEC EDGAR
        console.print("   📊 Extracting from SEC EDGAR...")
        sec_extractor = self.extractors['us_sec']
        sic_codes = self.sic_codes.get(industry)

        if sic_codes:
            sec_companies = sec_extractor.extract_leads(count=sec_count, sic_codes=sic_codes)
            all_companies.extend(sec_companies)

        # USASpending
        console.print("   🏛️  Extracting from USASpending...")
        federal_extractor = self.extractors['us_federal']

        naics_map = {
            'fmcg': '311',
            'ecommerce': '4541',
            'qcommerce': '4541',
            'cpg': '311',
            'retail': '445'
        }

        naics_code = naics_map.get(industry)
        if naics_code:
            federal_companies = federal_extractor.extract_leads(industry=naics_code, count=federal_count)
            all_companies.extend(federal_companies)

        # Track progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:

            task = progress.add_task(f"Processing US {industry}", total=len(all_companies))

            for i, lead in enumerate(all_companies[:count], 1):
                progress.update(task, completed=i)

                prog = ExtractionProgress(
                    job_id=job_id,
                    geography='us',
                    industry=industry,
                    current_count=i,
                    target_count=count,
                    percentage=(i / count) * 100,
                    status='running',
                    current_company=lead.get('company_name', ''),
                    timestamp=datetime.now().isoformat()
                )
                self.tracker.update_progress(prog)

                self.tracker.add_lead_summary(
                    job_id=job_id,
                    geography='us',
                    industry=industry,
                    company_name=lead.get('company_name', ''),
                    company_country='United States'
                )

        return all_companies[:count]

    def export_results(self, results: Dict, output_dir: str, format: str):
        """Export results to files"""
        console.print(f"\n[bold cyan]💾 Exporting results to {output_dir}/[/bold cyan]")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Export combined file
        all_leads = []
        for geography, industries in results.items():
            for industry, leads in industries.items():
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


def main():
    """Main execution"""
    args = parse_arguments()

    console.print("\n[bold green]🎯 Targeted Lead Generation with Monitoring[/bold green]")
    console.print("Real-time progress tracking enabled for dashboard\n")

    # Load config
    config = load_config()
    if not config:
        console.print("[red]❌ Could not load configuration[/red]")
        return

    # Initialize extractor
    extractor = MonitoredExtractor(config)

    # Determine geographies and industries
    geographies = ['india', 'us', 'europe', 'singapore'] if args.geography == 'all' else [args.geography]
    industries = ['fmcg', 'ecommerce', 'qcommerce', 'cpg', 'retail'] if args.industry == 'all' else [args.industry]

    # Calculate distribution
    geo_count = len(geographies)
    ind_count = len(industries)
    per_combination = max(args.count // (geo_count * ind_count), 10)

    console.print(f"[bold]Extraction Plan:[/bold]")
    console.print(f"  Geographies: {', '.join(geographies)}")
    console.print(f"  Industries: {', '.join(industries)}")
    console.print(f"  Per combination: ~{per_combination} leads")
    console.print(f"  📊 View live progress: http://localhost:8501\n")

    results = {}

    try:
        for geography in geographies:
            results[geography] = {}

            for industry in industries:
                # Generate unique job ID
                job_id = f"{geography}_{industry}_{uuid.uuid4().hex[:8]}"

                console.print(f"\n🚀 Starting: {geography.upper()} - {industry.upper()}")
                console.print(f"   Job ID: {job_id}")

                try:
                    leads = extractor.extract_with_progress(geography, industry, per_combination, job_id)
                    results[geography][industry] = leads

                    console.print(f"  ✅ Extracted {len(leads)} leads")

                except Exception as e:
                    console.print(f"  ❌ Error: {e}")
                    results[geography][industry] = []

        # Export results
        all_leads = extractor.export_results(results, args.output_dir, args.format)

        # Summary
        console.print("\n[bold green]✅ Extraction Complete![/bold green]")
        console.print(f"Total leads: {len(all_leads)}")
        console.print(f"Cost: $0.00")
        console.print(f"\n📊 View results in dashboard: http://localhost:8501\n")

    except KeyboardInterrupt:
        console.print("\n\n⏹️  Stopped by user")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
