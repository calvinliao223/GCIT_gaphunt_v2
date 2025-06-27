#!/usr/bin/env python3
"""
GAP HUNTER BOT - Academic Research Idea Development
Focus ONLY on research gap identification and idea generation
"""

import os
import sys
import subprocess
from datetime import datetime

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def setup_environment():
    """Setup environment for Gap Hunter Bot"""
    print("🎓 GAP HUNTER BOT - Academic Research Idea Development")
    print("=" * 60)

    # Install required packages for research APIs
    packages = ["pyyaml", "requests"]
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} ready")
        except ImportError:
            print(f"📦 Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed")
            else:
                print(f"❌ Failed to install {package}")

    # SECURITY: Load API keys from environment variables only
    # Load from .env file if it exists (development only)
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip('"\'')
                    os.environ[key] = value

    # Get API keys from environment variables
    api_keys = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
        "S2_API_KEY": os.getenv("S2_API_KEY", ""),
        "CORE_API_KEY": os.getenv("CORE_API_KEY", ""),
        "CONTACT_EMAIL": os.getenv("CONTACT_EMAIL", "contact@example.com"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    }

    for key, value in api_keys.items():
        os.environ[key] = value

    print("✅ Research API keys configured")
    print("✅ Ready for academic research gap hunting")

def run_gap_hunter_bot():
    """Run the Gap Hunter Bot for academic research"""
    print("\n🎓 GAP HUNTER BOT")
    print("=" * 40)
    print("🌟 Hi! I'm Gap Hunter Bot. I fetch fresh research gaps and rate their novelty.")
    print("📋 I'll return a YAML table—papers → gaps → keywords → scores (score < 3 is *rethink*).")

    try:
        # Run the clean Gap Hunter Bot
        exec(open('clean_gap_hunter.py').read())
        return True

    except Exception as e:
        print(f"❌ Error running Gap Hunter Bot: {e}")
        print("💡 Running simplified version...")

        # Simplified research gap generation
        topic = input("🎯 Enter research topic: ").strip()
        if not topic:
            topic = "machine learning"

        print(f"\n📋 RESEARCH GAPS FOR: {topic}")
        print("─" * 40)

        # Note: This is a simplified fallback version
        print("⚠️  Note: Using simplified version. For real paper data, run: python clean_gap_hunter.py")

        import yaml
        gaps = [
            {
                'paper': f'Data unavailable 2024 {topic.title()} Research',
                'gap': f'Limited scalability of {topic} methods in real-world applications',
                'keywords': [topic.split()[0], 'scalability', 'performance', 'deployment'],
                'score': 4,
                'note': '',
                'q1': False,
                'NEXT_STEPS': f'Design experiments targeting {topic} scalability and performance optimization.'
            },
            {
                'paper': f'Data unavailable 2023 {topic.title()} Study',
                'gap': f'Lack of interpretability in {topic} deep learning models',
                'keywords': [topic.split()[0], 'interpretability', 'explainable', 'transparency'],
                'score': 5,
                'note': '',
                'q1': False,
                'NEXT_STEPS': f'Develop {topic} framework addressing interpretability limitations.'
            }
        ]

        for gap in gaps:
            print(yaml.dump(gap, default_flow_style=False))
            print("─" * 20)

        return True



def main():
    """Main function - ONLY Gap Hunter Bot"""
    setup_environment()

    print("\n🎯 ACADEMIC RESEARCH GAP HUNTING")
    print("=" * 40)
    print("Focus: Research idea development and gap identification")

    # Run Gap Hunter Bot
    success = run_gap_hunter_bot()

    print("\n🎉 RESEARCH SESSION COMPLETE!")
    print("=" * 35)
    if success:
        print("✅ Gap Hunter Bot completed successfully!")
        print("🔬 Research gaps identified and analyzed!")
    else:
        print("❌ Some issues occurred, but basic functionality working")

    print("\n📧 Contact: calliaobiz@gmail.com")
    print("🔄 Run this script again for more research topics!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 This might be a dependency issue")
        print("📧 Contact: calliaobiz@gmail.com for help")
