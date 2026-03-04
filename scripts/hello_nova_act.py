"""
Minimal Nova Act test script.
Usage: NOVA_ACT_API_KEY=xxx python scripts/hello_nova_act.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NOVA_ACT_API_KEY")
if not api_key:
    print("ERROR: NOVA_ACT_API_KEY not set. Set it in .env or environment.")
    exit(1)

print("Testing Nova Act connection...")

try:
    from nova_act import NovaAct

    with NovaAct(starting_page="https://www.example.com") as nova:
        result = nova.act_get(
            "What is the title of this webpage? Return the page title."
        )
        print(f"Nova Act response: {result.response}")
        print("Nova Act test PASSED.")

except ImportError:
    print("ERROR: nova-act package not installed. Run: pip install nova-act")
except Exception as e:
    print(f"ERROR: Nova Act test failed: {e}")
