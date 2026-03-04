"""
Minimal Nova Act test script.
Usage: python scripts/hello_nova_act.py
Requires NOVA_ACT_API_KEY in .env or environment.
"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NOVA_ACT_API_KEY")
if not api_key:
    print("ERROR: NOVA_ACT_API_KEY not set. Copy .env.example to .env and fill in your key.")
    exit(1)

print("Testing Nova Act connection...")

try:
    from nova_act import NovaAct

    with NovaAct(starting_url="https://www.example.com", api_key=api_key) as nova:
        result = nova.act(
            "What is the title of this webpage? Return JSON with a 'title' field.",
            schema={
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
            },
        )
        print(f"Nova Act response: {result.parsed_response}")
        print("Nova Act test PASSED.")

except ImportError:
    print("ERROR: nova-act package not installed. Run: pip install nova-act")
except Exception as e:
    print(f"ERROR: Nova Act test failed: {e}")
