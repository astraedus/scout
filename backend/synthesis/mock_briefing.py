"""
Mock synthesis for development without Bedrock API access.
Generates realistic briefings from extracted data.
"""
import asyncio
import json
import random
from backend.models.schemas import ExtractedData, Briefing, KeyPerson, NewsItem, TechStack, FundingInfo


MOCK_BRIEFINGS = {
    "stripe": Briefing(
        company_name="Stripe",
        summary="Stripe is a leading financial infrastructure platform powering internet commerce for millions of businesses worldwide. With $14B+ ARR and 8,000+ employees, they provide payment processing, billing, and financial tools through developer-first APIs.",
        business_model="SaaS / Infrastructure — takes 2.9% + $0.30 per transaction, plus subscription fees for premium products (Billing, Connect, Atlas)",
        industry="Financial Technology",
        stage="Late Stage / Pre-IPO",
        founded="2010",
        headquarters="San Francisco, CA",
        size="8,000+ employees",
        website="https://stripe.com",
        products_services=[
            "Stripe Payments",
            "Stripe Billing",
            "Stripe Connect",
            "Stripe Terminal",
            "Stripe Atlas",
            "Stripe Radar (fraud detection)",
            "Stripe Treasury",
        ],
        key_people=[
            KeyPerson(name="Patrick Collison", title="CEO & Co-founder"),
            KeyPerson(name="John Collison", title="President & Co-founder"),
            KeyPerson(name="David Singleton", title="CTO"),
            KeyPerson(name="Dhivya Suryadevara", title="CFO"),
            KeyPerson(name="Will Gaybrick", title="Chief Product Officer"),
        ],
        recent_news=[
            NewsItem(
                headline="Stripe launches new AI-powered fraud detection features",
                date="Feb 2026",
                summary="Enhanced Radar with ML models reducing false declines by 30%",
            ),
            NewsItem(
                headline="Stripe valued at $91B in latest secondary market trading",
                date="Jan 2026",
                summary="Valuation recovery after 2023 markdowns",
            ),
            NewsItem(
                headline="Stripe expands to 5 new African markets",
                date="Feb 2026",
                summary="Continued emerging market expansion",
            ),
            NewsItem(
                headline="Stripe and Anthropic partner on AI billing infrastructure",
                date="Mar 2026",
                summary="New usage-based billing features for AI companies",
            ),
        ],
        tech_stack=TechStack(
            confirmed=["Ruby", "Go", "Java", "TypeScript", "React", "AWS", "Kubernetes", "Terraform"],
            inferred=["PostgreSQL", "Redis", "Kafka", "gRPC"],
        ),
        growth_signals=[
            "Hiring 120+ engineers — aggressive growth in ML/AI and Infrastructure",
            "Expanding to 5 new African markets — geographic growth",
            "Partnering with Anthropic on AI billing — positioned at the center of AI monetization",
            "$91B valuation recovery — strong market confidence",
            "280+ open positions across all departments",
        ],
        competitive_landscape=["Adyen", "Square (Block)", "PayPal/Braintree", "Checkout.com", "Worldpay"],
        talking_points=[
            "I noticed you're hiring heavily in ML/AI — how is the new Radar AI fraud detection performing since launch?",
            "The Anthropic partnership is interesting — are you seeing a lot of AI companies needing usage-based billing?",
            "With the Africa expansion, what's driving the emerging market strategy?",
            "280+ open roles is significant — what's the biggest growth area right now?",
        ],
        funding=FundingInfo(
            total_raised="$8.7B",
            last_round="Series I — $6.5B at $50B valuation (March 2023)",
            investors=["Sequoia Capital", "Andreessen Horowitz", "Tiger Global", "General Catalyst", "Thrive Capital"],
        ),
        confidence=0.92,
    ),
}


async def mock_synthesize_briefing(extracted_data: ExtractedData) -> Briefing:
    """Generate a mock briefing for development."""
    await asyncio.sleep(random.uniform(1.0, 2.0))  # Simulate API call

    key = extracted_data.company_name.lower().strip()
    if key in MOCK_BRIEFINGS:
        return MOCK_BRIEFINGS[key]

    # Generate a basic briefing from whatever mock data we have
    sources_ok = [r.source for r in extracted_data.results if r.success]
    sources_fail = [r.source for r in extracted_data.results if not r.success]

    return Briefing(
        company_name=extracted_data.company_name,
        summary=f"{extracted_data.company_name} is a technology company. Limited data was available from public sources.",
        industry="Technology",
        stage="Unknown",
        growth_signals=["Insufficient data to determine growth signals"],
        talking_points=[
            f"What's the biggest challenge {extracted_data.company_name} is facing right now?",
            "How is your team thinking about AI integration?",
        ],
        confidence=len(sources_ok) / max(len(sources_ok) + len(sources_fail), 1),
    )
