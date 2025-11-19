#!/usr/bin/env python3
"""
Daily Reader - Scheduled reading for ROOK
Run this via cron at 6am, 12pm, and 6pm
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.consciousness import ActiveReader, get_hot_cache
# from src.personality.personality_layer_with_storage import PersonalityLayerWithStorage


def morning_reading():
    """
    Morning reading routine (6am)
    Focus: Overnight news, fraud/corruption stories
    """
    print(f"☀️  Morning Reading - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    reader = ActiveReader()
    
    topics = [
        "fraud", "corruption", "bribery",
        "money laundering", "SEC investigation",
        "DOJ settlement", "accounting fraud"
    ]
    
    memories = reader.read_morning_news(topics=topics)
    
    print(f"📚 Read {len(memories)} articles")
    
    # Update hot cache
    cache = get_hot_cache()
    cache.refresh_cache(memories)
    
    # Print summary
    summary = reader.get_reading_summary(days=1)
    print(f"📊 Summary:")
    print(f"   - Articles: {summary['articles_read']}")
    print(f"   - Top patterns: {summary['top_patterns'][:3]}")
    print(f"   - Sources: {summary['sources'][:5]}")
    
    return memories


def midday_reading():
    """
    Midday reading routine (12pm)
    Focus: Breaking news, social media, court documents
    """
    print(f"🌤️  Midday Reading - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    reader = ActiveReader()
    
    # Read breaking news
    topics = [
        "breaking fraud news",
        "SEC charges",
        "financial crime",
        "corporate scandal"
    ]
    
    memories = reader.read_morning_news(topics=topics)
    
    print(f"📚 Read {len(memories)} articles")
    
    # TODO: Add social media monitoring here
    # - Twitter/X
    # - Reddit
    
    # Update hot cache
    cache = get_hot_cache()
    cache.refresh_cache(memories)
    
    return memories


def evening_reading():
    """
    Evening reading routine (6pm)
    Focus: Day's summary, analysis pieces, academic papers
    """
    print(f"🌙 Evening Reading - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    reader = ActiveReader()
    
    # Read analysis and deeper pieces
    topics = [
        "fraud analysis",
        "forensic accounting",
        "anti-corruption",
        "financial investigation"
    ]
    
    memories = reader.read_morning_news(topics=topics)
    
    print(f"📚 Read {len(memories)} articles")
    
    # TODO: Add academic paper reading here
    
    # Update hot cache
    cache = get_hot_cache()
    cache.refresh_cache(memories)
    
    # Print daily summary
    summary = reader.get_reading_summary(days=1)
    print(f"\n📊 Daily Summary:")
    print(f"   - Total articles: {summary['articles_read']}")
    print(f"   - Top patterns: {summary['top_patterns']}")
    print(f"   - Fraud types: {summary['fraud_types']}")
    
    return memories


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ROOK Daily Reader")
    parser.add_argument(
        "session",
        choices=["morning", "midday", "evening"],
        help="Reading session to run"
    )
    
    args = parser.parse_args()
    
    if args.session == "morning":
        morning_reading()
    elif args.session == "midday":
        midday_reading()
    elif args.session == "evening":
        evening_reading()
