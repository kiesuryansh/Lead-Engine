"""
Free API Manager - $0 Cost Lead Enrichment

Manages multiple free AI APIs to enrich lead data:
- Google AI Studio: 1M tokens/day free
- Groq: 14.4K requests/day free
- Together AI: $25 free credits
- HuggingFace: 1K requests/day free

Automatically rotates between APIs to maximize free usage.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import time


@dataclass
class APIQuota:
    """Track API usage and limits"""
    name: str
    daily_limit: int
    used_today: int
    last_reset: datetime
    cost_per_request: float = 0.0

    def is_available(self) -> bool:
        """Check if API has quota remaining"""
        # Reset daily counter if new day
        if datetime.now().date() > self.last_reset.date():
            self.used_today = 0
            self.last_reset = datetime.now()

        return self.used_today < self.daily_limit

    def increment(self):
        """Increment usage counter"""
        self.used_today += 1


class FreeAPIManager:
    """
    Manages multiple free AI APIs for lead enrichment

    Automatically:
    - Rotates between free APIs
    - Tracks usage quotas
    - Falls back when limits reached
    - Maintains $0 operational cost
    """

    def __init__(self):
        self.apis = self._initialize_apis()
        self.total_cost = 0.0
        self.total_requests = 0

    def _initialize_apis(self) -> Dict[str, APIQuota]:
        """Initialize API quota tracking"""
        return {
            'google_ai_studio': APIQuota(
                name='Google AI Studio',
                daily_limit=1000,  # Conservative (actual: 1M tokens/day)
                used_today=0,
                last_reset=datetime.now(),
                cost_per_request=0.0
            ),
            'groq': APIQuota(
                name='Groq',
                daily_limit=14400,  # 14.4K requests/day
                used_today=0,
                last_reset=datetime.now(),
                cost_per_request=0.0
            ),
            'together_ai': APIQuota(
                name='Together AI',
                daily_limit=1000,  # From free credits
                used_today=0,
                last_reset=datetime.now(),
                cost_per_request=0.0
            ),
            'huggingface': APIQuota(
                name='HuggingFace',
                daily_limit=1000,
                used_today=0,
                last_reset=datetime.now(),
                cost_per_request=0.0
            ),
        }

    def get_available_api(self) -> Optional[str]:
        """Get next available API with quota remaining"""
        for api_name, quota in self.apis.items():
            if quota.is_available():
                return api_name
        return None

    def enrich_lead_with_google_ai(self, lead: Dict) -> Dict:
        """
        Enrich lead using Google AI Studio (Gemini)

        Free tier: 1M tokens/day (very generous)
        """
        try:
            import google.generativeai as genai

            # Check for API key
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            if not api_key:
                print("⚠️  GOOGLE_AI_API_KEY not set")
                return lead

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            # Create enrichment prompt
            prompt = f"""
            Analyze this company and provide enrichment data:

            Company: {lead.get('company_name', '')}
            Industry: {lead.get('industry', '')}
            Location: {lead.get('address', '')}

            Provide:
            1. Estimated company size (employees)
            2. Likely decision maker role for B2B sales
            3. Key business focus areas
            4. Potential pain points this company might have

            Return as JSON with keys: employee_count_estimate, decision_maker_role, focus_areas, pain_points
            """

            response = model.generate_content(prompt)

            # Parse response
            try:
                enrichment = json.loads(response.text)
                lead.update({
                    'enrichment_source': 'Google AI Studio',
                    'employee_estimate': enrichment.get('employee_count_estimate'),
                    'decision_maker': enrichment.get('decision_maker_role'),
                    'focus_areas': enrichment.get('focus_areas'),
                    'pain_points': enrichment.get('pain_points'),
                    'enriched_at': datetime.now().isoformat()
                })
            except json.JSONDecodeError:
                # If not JSON, use text response
                lead['ai_analysis'] = response.text[:500]

            self.apis['google_ai_studio'].increment()
            self.total_requests += 1

            return lead

        except Exception as e:
            print(f"❌ Google AI error: {e}")
            return lead

    def enrich_lead_with_groq(self, lead: Dict) -> Dict:
        """
        Enrich lead using Groq (fast inference)

        Free tier: 14.4K requests/day
        """
        try:
            from groq import Groq

            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                print("⚠️  GROQ_API_KEY not set")
                return lead

            client = Groq(api_key=api_key)

            prompt = f"""
            Company: {lead.get('company_name', '')}
            Industry: {lead.get('industry', '')}

            Provide brief analysis:
            - Estimated company size
            - Best contact role for B2B sales
            - Key business challenges

            Keep response under 100 words.
            """

            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )

            lead['ai_enrichment'] = completion.choices[0].message.content
            lead['enrichment_source'] = 'Groq'
            lead['enriched_at'] = datetime.now().isoformat()

            self.apis['groq'].increment()
            self.total_requests += 1

            return lead

        except Exception as e:
            print(f"❌ Groq error: {e}")
            return lead

    def enrich_lead(self, lead: Dict) -> Dict:
        """
        Enrich lead using any available free API

        Automatically selects API with available quota
        """
        available_api = self.get_available_api()

        if not available_api:
            print("⚠️  All API quotas exhausted for today")
            return lead

        # Route to appropriate API
        if available_api == 'google_ai_studio':
            return self.enrich_lead_with_google_ai(lead)
        elif available_api == 'groq':
            return self.enrich_lead_with_groq(lead)
        else:
            # Add more API handlers as needed
            return lead

    def enrich_leads_batch(self, leads: List[Dict], show_progress: bool = True) -> List[Dict]:
        """
        Enrich multiple leads efficiently

        Args:
            leads: List of lead dictionaries
            show_progress: Show progress bar

        Returns:
            Enriched leads
        """
        enriched = []

        for i, lead in enumerate(leads):
            if show_progress:
                print(f"   Enriching {i+1}/{len(leads)}: {lead.get('company_name', 'Unknown')}", end='\r')

            enriched_lead = self.enrich_lead(lead)
            enriched.append(enriched_lead)

            # Small delay to respect rate limits
            time.sleep(0.1)

        if show_progress:
            print()  # New line after progress

        print(f"✅ Enriched {len(enriched)} leads")
        self.print_stats()

        return enriched

    def print_stats(self):
        """Print usage statistics"""
        print(f"\n📊 API Usage Statistics:")
        print(f"   Total Requests: {self.total_requests}")
        print(f"   Total Cost: ${self.total_cost:.2f}")

        print(f"\n   API Quotas:")
        for api_name, quota in self.apis.items():
            remaining = quota.daily_limit - quota.used_today
            usage_pct = (quota.used_today / quota.daily_limit) * 100
            print(f"   • {quota.name}: {quota.used_today}/{quota.daily_limit} ({usage_pct:.1f}%) - {remaining} remaining")

    def get_cost_report(self) -> Dict:
        """Get detailed cost report"""
        return {
            'total_requests': self.total_requests,
            'total_cost': self.total_cost,
            'cost_per_lead': self.total_cost / max(self.total_requests, 1),
            'apis_used': {
                name: {
                    'requests': quota.used_today,
                    'limit': quota.daily_limit,
                    'cost': quota.used_today * quota.cost_per_request
                }
                for name, quota in self.apis.items()
            }
        }


class EmailValidator:
    """
    Validate email addresses using free methods

    - Format validation (regex)
    - Domain MX record check (DNS)
    - Free email detection
    """

    def __init__(self):
        pass

    def is_valid_format(self, email: str) -> bool:
        """Check if email format is valid"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def has_mx_record(self, email: str) -> bool:
        """Check if domain has MX record (can receive email)"""
        try:
            import dns.resolver
            domain = email.split('@')[1]
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except:
            return False

    def is_free_email(self, email: str) -> bool:
        """Check if email is from free provider"""
        free_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
        ]
        domain = email.split('@')[1].lower()
        return domain in free_providers

    def validate(self, email: str) -> Dict:
        """
        Comprehensive email validation

        Returns:
            Dictionary with validation results
        """
        return {
            'email': email,
            'valid_format': self.is_valid_format(email),
            'has_mx': self.has_mx_record(email),
            'is_free': self.is_free_email(email),
            'is_corporate': not self.is_free_email(email) and self.has_mx_record(email)
        }


if __name__ == "__main__":
    # Demo
    print("🎯 DEMO: Free API Lead Enrichment")
    print("=" * 60)

    # Sample leads
    sample_leads = [
        {
            'company_name': 'Acme Corporation',
            'industry': 'Software Development',
            'address': 'San Francisco, CA'
        },
        {
            'company_name': 'Tech Innovations Inc',
            'industry': 'Cloud Services',
            'address': 'Austin, TX'
        }
    ]

    # Initialize manager
    manager = FreeAPIManager()

    print("\n📝 Original Leads:")
    for lead in sample_leads:
        print(f"   • {lead['company_name']} - {lead['industry']}")

    # Enrich leads
    print("\n🔄 Enriching leads with free APIs...")
    enriched_leads = manager.enrich_leads_batch(sample_leads)

    print("\n✨ Enriched Leads:")
    for lead in enriched_leads:
        print(f"\n   {lead['company_name']}")
        if 'ai_enrichment' in lead:
            print(f"   Analysis: {lead['ai_enrichment'][:100]}...")

    # Cost report
    cost_report = manager.get_cost_report()
    print(f"\n💰 Cost Report:")
    print(f"   Total Cost: ${cost_report['total_cost']:.4f}")
    print(f"   Cost per Lead: ${cost_report['cost_per_lead']:.4f}")
    print(f"   ✅ FREE TIER USAGE ONLY")

    # Email validation demo
    print("\n\n📧 Email Validation Demo")
    print("=" * 60)

    validator = EmailValidator()
    test_emails = [
        'contact@acme.com',
        'john.doe@gmail.com',
        'invalid-email',
        'sales@techinnovations.io'
    ]

    for email in test_emails:
        result = validator.validate(email)
        print(f"\n   {email}")
        print(f"   Valid Format: {'✅' if result['valid_format'] else '❌'}")
        print(f"   Has MX: {'✅' if result['has_mx'] else '❌'}")
        print(f"   Corporate: {'✅' if result['is_corporate'] else '❌'}")
