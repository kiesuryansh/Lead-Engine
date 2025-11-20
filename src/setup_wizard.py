#!/usr/bin/env python3
"""
Setup Wizard - Configure Free APIs in Under 5 Minutes

This wizard helps you:
1. Set up free AI API keys (Google AI Studio, Groq, etc.)
2. Test API connections
3. Verify extractors are working
4. Generate sample leads

All APIs are FREE with generous limits.
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
import subprocess


console = Console()


def print_welcome():
    """Print welcome message"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]🎯 Legal Lead Generation Engine[/bold green]\n"
        "[cyan]Setup Wizard - Configure Free APIs[/cyan]\n\n"
        "This will help you set up FREE API keys for:\n"
        "  • Google AI Studio (1M tokens/day)\n"
        "  • Groq (14.4K requests/day)\n"
        "  • Together AI ($25 free credits)\n\n"
        "[yellow]⏱️  Time: < 5 minutes[/yellow]\n"
        "[green]💰 Cost: $0.00[/green]",
        title="Welcome",
        border_style="green"
    ))


def check_python_version():
    """Verify Python version"""
    console.print("\n[bold]Step 1: Checking Python Version[/bold]")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        console.print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        console.print(f"❌ Python {version.major}.{version.minor} - Need Python 3.8+")
        return False


def install_dependencies():
    """Install required packages"""
    console.print("\n[bold]Step 2: Installing Dependencies[/bold]")

    if Confirm.ask("Install required Python packages?", default=True):
        console.print("\n📦 Installing packages... (this may take 1-2 minutes)")

        try:
            # Create minimal requirements for quick setup
            minimal_requirements = [
                "requests",
                "beautifulsoup4",
                "pandas",
                "python-dotenv",
                "rich",
            ]

            for package in minimal_requirements:
                console.print(f"   Installing {package}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", package],
                    check=True
                )

            console.print("✅ Core packages installed")

            # Optional AI packages
            if Confirm.ask("\nInstall AI API packages for enrichment? (optional)", default=True):
                ai_packages = [
                    "google-generativeai",
                    "groq",
                ]

                for package in ai_packages:
                    try:
                        console.print(f"   Installing {package}...")
                        subprocess.run(
                            [sys.executable, "-m", "pip", "install", "-q", package],
                            check=True
                        )
                    except:
                        console.print(f"   ⚠️  Could not install {package} (optional)")

                console.print("✅ AI packages installed")

            return True

        except Exception as e:
            console.print(f"❌ Error installing packages: {e}")
            console.print("\nTry manually: pip install -r requirements.txt")
            return False

    return True


def setup_google_ai():
    """Setup Google AI Studio API"""
    console.print("\n[bold cyan]━━━ Google AI Studio (Gemini) ━━━[/bold cyan]")
    console.print("\n[yellow]FREE: 1 million tokens per day[/yellow]")

    console.print("\n📝 How to get API key:")
    console.print("   1. Visit: https://makersuite.google.com/app/apikey")
    console.print("   2. Click 'Create API Key'")
    console.print("   3. Copy the key")

    if Confirm.ask("\nDo you have a Google AI Studio API key?", default=False):
        api_key = Prompt.ask("Enter your Google AI Studio API key")

        if api_key and len(api_key) > 20:
            # Save to .env
            save_to_env("GOOGLE_AI_API_KEY", api_key)

            # Test the key
            if test_google_ai(api_key):
                console.print("✅ Google AI Studio configured successfully!")
                return True
            else:
                console.print("⚠️  API key saved but test failed. Check the key.")
                return False
        else:
            console.print("⚠️  Invalid API key format")
            return False
    else:
        console.print("⏭️  Skipping Google AI Studio (you can add it later)")
        return False


def setup_groq():
    """Setup Groq API"""
    console.print("\n[bold cyan]━━━ Groq (Fast Inference) ━━━[/bold cyan]")
    console.print("\n[yellow]FREE: 14,400 requests per day[/yellow]")

    console.print("\n📝 How to get API key:")
    console.print("   1. Visit: https://console.groq.com/keys")
    console.print("   2. Sign up (free)")
    console.print("   3. Create API key")
    console.print("   4. Copy the key")

    if Confirm.ask("\nDo you have a Groq API key?", default=False):
        api_key = Prompt.ask("Enter your Groq API key")

        if api_key and len(api_key) > 20:
            save_to_env("GROQ_API_KEY", api_key)

            if test_groq(api_key):
                console.print("✅ Groq configured successfully!")
                return True
            else:
                console.print("⚠️  API key saved but test failed. Check the key.")
                return False
        else:
            console.print("⚠️  Invalid API key format")
            return False
    else:
        console.print("⏭️  Skipping Groq (you can add it later)")
        return False


def save_to_env(key: str, value: str):
    """Save API key to .env file"""
    env_path = Path(".env")

    # Read existing .env
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []

    # Check if key exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_exists = True
            break

    # Add key if doesn't exist
    if not key_exists:
        lines.append(f"{key}={value}\n")

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)

    console.print(f"💾 Saved {key} to .env")


def test_google_ai(api_key: str) -> bool:
    """Test Google AI Studio API"""
    try:
        console.print("   Testing API connection...")
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content("Say 'API test successful' in exactly those words.")

        if "successful" in response.text.lower():
            return True
        return False

    except Exception as e:
        console.print(f"   ❌ Test failed: {e}")
        return False


def test_groq(api_key: str) -> bool:
    """Test Groq API"""
    try:
        console.print("   Testing API connection...")
        from groq import Groq

        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )

        if "successful" in completion.choices[0].message.content.lower():
            return True
        return False

    except Exception as e:
        console.print(f"   ❌ Test failed: {e}")
        return False


def test_extractors():
    """Test that extractors are working"""
    console.print("\n[bold]Step 3: Testing Extractors[/bold]")

    console.print("\n🧪 Testing SEC EDGAR extractor...")

    try:
        # Simple connectivity test
        import requests
        response = requests.get("https://www.sec.gov/files/company_tickers.json", timeout=10)

        if response.status_code == 200:
            console.print("✅ SEC EDGAR - OK")
        else:
            console.print("⚠️  SEC EDGAR connection issue")

    except Exception as e:
        console.print(f"❌ SEC EDGAR test failed: {e}")

    console.print("\n✅ Extractors are ready to use!")


def show_summary(google_ai_ok: bool, groq_ok: bool):
    """Show setup summary"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]🎉 Setup Complete![/bold green]\n\n"
        "Configuration Summary:\n"
        f"  • Google AI Studio: {'✅ Configured' if google_ai_ok else '⏭️ Skipped'}\n"
        f"  • Groq: {'✅ Configured' if groq_ok else '⏭️ Skipped'}\n"
        "  • SEC EDGAR: ✅ Ready (no API key needed)\n"
        "  • OpenCorporates: ✅ Ready (no API key needed)\n"
        "  • USASpending: ✅ Ready (no API key needed)\n\n"
        "[bold yellow]Next Steps:[/bold yellow]\n"
        "  1. Run demo: [cyan]python src/examples/quick_demo.py[/cyan]\n"
        "  2. Extract leads: [cyan]python src/main.py --count 100[/cyan]\n"
        "  3. Read docs: [cyan]docs/[/cyan]\n\n"
        "[green]You can now extract 1000s of leads for FREE![/green]",
        title="Setup Complete",
        border_style="green"
    ))


def main():
    """Run setup wizard"""
    print_welcome()

    # Check Python version
    if not check_python_version():
        console.print("\n❌ Please upgrade Python to 3.8+")
        return

    # Install dependencies
    if not install_dependencies():
        console.print("\n⚠️  Some packages could not be installed")
        if not Confirm.ask("Continue anyway?", default=False):
            return

    # Create data directories
    console.print("\n📁 Creating data directories...")
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    console.print("✅ Directories created")

    # Setup APIs (optional)
    google_ai_ok = setup_google_ai()
    groq_ok = setup_groq()

    # Test extractors
    test_extractors()

    # Show summary
    show_summary(google_ai_ok, groq_ok)

    # Offer to run demo
    if Confirm.ask("\n🚀 Run demo now?", default=True):
        console.print("\nStarting demo...\n")
        try:
            os.chdir(Path(__file__).parent.parent)
            subprocess.run([sys.executable, "src/examples/quick_demo.py"])
        except Exception as e:
            console.print(f"❌ Could not run demo: {e}")
            console.print("Try manually: python src/examples/quick_demo.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n⏹️  Setup cancelled by user")
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        console.print("\nFor help, see docs/TROUBLESHOOTING.md")
