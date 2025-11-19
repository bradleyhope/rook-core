"""
Active Reader - ROOK's Continuous Learning System
Constantly ingests news, social media, and other sources
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI


class ActiveReader:
    """
    ROOK's continuous reading system
    
    Reads from:
    - News APIs (NewsAPI, etc.)
    - Social media (Twitter, Reddit)
    - Official sources (SEC, DOJ)
    - Archives
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, newsapi_key: Optional[str] = None):
        self.openai_client = OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.reading_history = []
        self.current_reading = None
        self.daily_reading_count = 0
        
    def read_morning_news(self, topics: Optional[List[str]] = None) -> List[Dict]:
        """
        Ingest morning news about fraud, corruption, scandals
        
        Args:
            topics: Specific topics to search for (default: fraud-related)
            
        Returns:
            List of reading memories
        """
        if topics is None:
            topics = [
                "fraud", "corruption", "bribery", 
                "money laundering", "scandal", "SEC investigation",
                "DOJ settlement", "FCPA violation"
            ]
        
        articles = []
        
        # Use NewsAPI if available
        newsapi_key = os.getenv('NEWSAPI_KEY')
        if newsapi_key:
            articles.extend(self._fetch_from_newsapi(topics, newsapi_key))
        
        # Process each article
        reading_memories = []
        for article in articles[:20]:  # Limit to 20 articles per session
            memory = self._process_article(article)
            if memory:
                reading_memories.append(memory)
                self.daily_reading_count += 1
        
        return reading_memories
    
    def _fetch_from_newsapi(self, topics: List[str], api_key: str) -> List[Dict]:
        """
        Fetch articles from NewsAPI
        
        Args:
            topics: Topics to search for
            api_key: NewsAPI key
            
        Returns:
            List of articles
        """
        articles = []
        
        for topic in topics[:3]:  # Limit API calls
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": topic,
                    "apiKey": api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 10,
                    "from": (datetime.now() - timedelta(days=1)).isoformat()
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles.extend(data.get("articles", []))
            except Exception as e:
                print(f"Error fetching news for {topic}: {e}")
        
        return articles
    
    def _process_article(self, article: Dict) -> Optional[Dict]:
        """
        Process an article into a reading memory
        
        Args:
            article: Article data from news API
            
        Returns:
            Reading memory dict or None if not relevant
        """
        try:
            title = article.get("title", "")
            description = article.get("description", "")
            content = article.get("content", "")
            url = article.get("url", "")
            source = article.get("source", {}).get("name", "Unknown")
            published_at = article.get("publishedAt", "")
            
            # Check relevance
            if not self._is_fraud_related(title, description):
                return None
            
            # Generate summary and extract entities
            analysis = self._analyze_article(title, description, content)
            
            # Create reading memory
            memory = {
                "memory_id": f"read_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(url) % 10000}",
                "type": "reading_session",
                "source": source,
                "title": title,
                "url": url,
                "date_published": published_at,
                "date_read": datetime.now().isoformat(),
                "summary": analysis.get("summary"),
                "key_entities": analysis.get("entities", []),
                "patterns_detected": analysis.get("patterns", []),
                "fraud_type": analysis.get("fraud_type"),
                "relevance_score": analysis.get("relevance", 0.5),
                "my_thoughts": analysis.get("thoughts")
            }
            
            self.reading_history.append(memory)
            return memory
            
        except Exception as e:
            print(f"Error processing article: {e}")
            return None
    
    def _is_fraud_related(self, title: str, description: str) -> bool:
        """
        Quick check if article is fraud-related
        
        Args:
            title: Article title
            description: Article description
            
        Returns:
            True if fraud-related
        """
        text = f"{title} {description}".lower()
        
        fraud_keywords = [
            "fraud", "corruption", "bribery", "money laundering",
            "embezzlement", "ponzi", "pyramid scheme", "sec charges",
            "doj settlement", "fcpa", "insider trading", "market manipulation",
            "accounting fraud", "financial crime", "shell company",
            "offshore account", "tax evasion", "kickback"
        ]
        
        return any(keyword in text for keyword in fraud_keywords)
    
    def _analyze_article(self, title: str, description: str, content: str) -> Dict:
        """
        Analyze article using LLM
        
        Args:
            title: Article title
            description: Article description
            content: Article content
            
        Returns:
            Analysis dict with summary, entities, patterns, etc.
        """
        try:
            # Truncate content if too long
            max_content_length = 2000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt = f"""Analyze this fraud/corruption news article:

Title: {title}

Description: {description}

Content: {content}

Provide:
1. A 2-sentence summary
2. Key entities (people, companies, jurisdictions)
3. Fraud patterns detected (e.g., "shell companies", "inflated invoices", "bribery")
4. Type of fraud (e.g., "accounting fraud", "bribery", "money laundering")
5. Relevance score (0.0-1.0) for investigative journalism
6. Your thoughts (1 sentence, as ROOK the investigator)

Format as JSON:
{{
    "summary": "...",
    "entities": ["entity1", "entity2"],
    "patterns": ["pattern1", "pattern2"],
    "fraud_type": "...",
    "relevance": 0.8,
    "thoughts": "..."
}}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are ROOK, an AI investigative journalist analyzing fraud news."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing article: {e}")
            return {
                "summary": f"{title}. {description}",
                "entities": [],
                "patterns": [],
                "fraud_type": "unknown",
                "relevance": 0.5,
                "thoughts": "Need to read more carefully."
            }
    
    def get_reading_summary(self, days: int = 1) -> Dict:
        """
        Get summary of what ROOK has read recently
        
        Args:
            days: Number of days to look back
            
        Returns:
            Summary dict
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_readings = [
            r for r in self.reading_history
            if datetime.fromisoformat(r["date_read"]) > cutoff
        ]
        
        # Aggregate patterns
        all_patterns = []
        for reading in recent_readings:
            all_patterns.extend(reading.get("patterns_detected", []))
        
        pattern_counts = {}
        for pattern in all_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Top patterns
        top_patterns = sorted(
            pattern_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "articles_read": len(recent_readings),
            "time_period": f"last {days} day(s)",
            "top_patterns": [{"pattern": p, "count": c} for p, c in top_patterns],
            "sources": list(set(r["source"] for r in recent_readings)),
            "fraud_types": list(set(r.get("fraud_type") for r in recent_readings if r.get("fraud_type")))
        }
    
    def get_recent_readings(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent readings
        
        Args:
            limit: Number of readings to return
            
        Returns:
            List of recent reading memories
        """
        return sorted(
            self.reading_history,
            key=lambda x: x["date_read"],
            reverse=True
        )[:limit]


if __name__ == "__main__":
    # Test the active reader
    reader = ActiveReader()
    
    print("=== Testing Active Reader ===")
    print("Reading morning news...")
    
    # Simulate reading (would normally use real API)
    test_article = {
        "title": "SEC Charges Company X with Accounting Fraud",
        "description": "The SEC alleges Company X inflated revenue by $500M using fake invoices",
        "content": "The Securities and Exchange Commission today charged Company X...",
        "url": "https://example.com/article",
        "source": {"name": "WSJ"},
        "publishedAt": datetime.now().isoformat()
    }
    
    memory = reader._process_article(test_article)
    if memory:
        print(f"\n✅ Processed article: {memory['title']}")
        print(f"   Summary: {memory['summary']}")
        print(f"   Patterns: {memory['patterns_detected']}")
        print(f"   My thoughts: {memory['my_thoughts']}")
    
    print("\n=== Reading Summary ===")
    summary = reader.get_reading_summary(days=1)
    print(f"Articles read: {summary['articles_read']}")
    print(f"Top patterns: {summary['top_patterns']}")
