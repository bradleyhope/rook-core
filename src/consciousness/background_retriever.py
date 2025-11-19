"""
Background Retriever - Anticipatory Intelligence
Pre-fetches content based on conversation trajectory
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
import os


class BackgroundRetriever:
    """
    Anticipates where conversation is going and pre-fetches related content
    
    While user is typing or ROOK is responding, this system:
    1. Analyzes conversation trajectory
    2. Predicts what user might ask next
    3. Pre-fetches related content from Pinecone
    4. Caches results for instant retrieval
    """
    
    def __init__(self, personality_layer, hot_cache, openai_api_key: Optional[str] = None):
        self.personality_layer = personality_layer
        self.hot_cache = hot_cache
        self.openai_client = OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
        self.anticipated_topics = []
        self.prefetch_queue = []
        self.hit_count = 0
        self.miss_count = 0
    
    def anticipate_next_topics(self, current_message: str, conversation_context: List[Dict]) -> List[str]:
        """
        Predict what user might ask next based on conversation flow
        
        Args:
            current_message: User's current message
            conversation_context: Recent conversation history
            
        Returns:
            List of anticipated topics to pre-fetch
        """
        try:
            # Build conversation summary
            recent_topics = self._extract_topics_from_history(conversation_context)
            
            # Use LLM to predict next topics
            prompt = f"""Given this conversation about fraud investigation:

Recent topics discussed: {', '.join(recent_topics[-5:])}

Current user message: "{current_message}"

What are the 3 most likely topics the user will ask about next?

Consider:
- Natural conversation flow (if discussing 1MDB, might ask about Jho Low, Goldman Sachs, or shell companies)
- Technique deep-dives (if discussing shell companies, might ask about beneficial ownership or nominee directors)
- Case comparisons (if discussing Theranos, might ask about FTX or Enron)
- Follow-the-money (if discussing bribery, might ask about money laundering or offshore accounts)

Respond with JSON array of topics:
["topic1", "topic2", "topic3"]"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at predicting conversation flow in fraud investigations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            anticipated = result.get("topics", [])
            
            self.anticipated_topics = anticipated
            return anticipated
            
        except Exception as e:
            print(f"Error anticipating topics: {e}")
            # Fallback: use simple keyword expansion
            return self._simple_topic_expansion(current_message)
    
    def _extract_topics_from_history(self, conversation_context: List[Dict]) -> List[str]:
        """Extract topics from conversation history"""
        topics = []
        for msg in conversation_context[-10:]:  # Last 10 messages
            content = msg.get("content", "")
            # Simple extraction: look for capitalized words and key terms
            words = content.split()
            topics.extend([w for w in words if len(w) > 3 and (w[0].isupper() or w.lower() in [
                "fraud", "corruption", "bribery", "shell", "company", "offshore"
            ])])
        return topics
    
    def _simple_topic_expansion(self, message: str) -> List[str]:
        """
        Simple fallback for topic anticipation
        
        Args:
            message: Current message
            
        Returns:
            List of related topics
        """
        # Predefined expansions
        expansions = {
            "1mdb": ["jho low", "goldman sachs", "najib razak", "shell companies"],
            "theranos": ["elizabeth holmes", "fraud detection", "whistleblower"],
            "shell companies": ["nominee directors", "beneficial ownership", "seychelles"],
            "bribery": ["fcpa", "money laundering", "offshore accounts"],
            "fraud": ["detection techniques", "red flags", "forensic accounting"]
        }
        
        message_lower = message.lower()
        for key, topics in expansions.items():
            if key in message_lower:
                return topics[:3]
        
        return []
    
    async def prefetch_topics(self, topics: List[str]):
        """
        Pre-fetch topics in background (async)
        
        Args:
            topics: Topics to pre-fetch
        """
        tasks = []
        for topic in topics:
            task = self._async_retrieve(topic)
            tasks.append(task)
        
        # Execute all pre-fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Add to hot cache
        for topic, result in zip(topics, results):
            if not isinstance(result, Exception) and result:
                self.hot_cache.add_to_background_queue(topic, result)
    
    async def _async_retrieve(self, topic: str) -> Optional[Dict]:
        """
        Async retrieval from Pinecone
        
        Args:
            topic: Topic to retrieve
            
        Returns:
            Retrieved content or None
        """
        try:
            # Check if already in cache
            cached = self.hot_cache.get_cached(topic)
            if cached:
                return cached
            
            # Retrieve from Pinecone
            # Note: This would normally be async, but Pinecone client is sync
            # In production, wrap in asyncio.to_thread()
            result = await asyncio.to_thread(
                self.personality_layer.retrieve_relevant_context,
                topic
            )
            
            return {
                "topic": topic,
                "content": result,
                "timestamp": datetime.now().isoformat(),
                "prefetched": True
            }
            
        except Exception as e:
            print(f"Error pre-fetching {topic}: {e}")
            return None
    
    def check_anticipation_accuracy(self, actual_next_query: str) -> bool:
        """
        Check if we correctly anticipated the next query
        
        Args:
            actual_next_query: What user actually asked
            
        Returns:
            True if we anticipated correctly
        """
        actual_lower = actual_next_query.lower()
        
        for anticipated in self.anticipated_topics:
            if anticipated.lower() in actual_lower or actual_lower in anticipated.lower():
                self.hit_count += 1
                return True
        
        self.miss_count += 1
        return False
    
    def get_anticipation_stats(self) -> Dict:
        """
        Get anticipation accuracy statistics
        
        Returns:
            Stats dict with hit rate, etc.
        """
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        
        return {
            "total_predictions": total,
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": hit_rate,
            "current_anticipated": self.anticipated_topics
        }
    
    def start_background_prefetch(self, current_message: str, conversation_context: List[Dict]):
        """
        Start background pre-fetching (non-blocking)
        
        Args:
            current_message: Current user message
            conversation_context: Conversation history
        """
        # Anticipate topics
        topics = self.anticipate_next_topics(current_message, conversation_context)
        
        # Start async pre-fetch
        asyncio.create_task(self.prefetch_topics(topics))


# Anticipation strategies
class AnticipationStrategies:
    """
    Different strategies for anticipating next topics
    """
    
    @staticmethod
    def topic_expansion(current_topic: str) -> List[str]:
        """
        Expand current topic to related topics
        
        Examples:
        - "1MDB" → ["Jho Low", "Goldman Sachs", "Najib Razak"]
        - "Shell companies" → ["Nominee directors", "Beneficial ownership"]
        """
        expansions = {
            "1mdb": ["jho low", "goldman sachs", "najib razak", "shell companies", "money laundering"],
            "jho low": ["1mdb", "good star limited", "tanore finance", "fugitive"],
            "theranos": ["elizabeth holmes", "sunny balwani", "fraud detection", "whistleblower", "john carreyrou"],
            "ftx": ["sam bankman-fried", "alameda research", "cryptocurrency fraud", "customer funds"],
            "enron": ["accounting fraud", "mark-to-market", "special purpose entities", "arthur andersen"],
            "shell companies": ["nominee directors", "beneficial ownership", "seychelles", "british virgin islands"],
            "money laundering": ["shell companies", "offshore accounts", "layering", "smurfing"],
            "bribery": ["fcpa", "money laundering", "shell companies", "kickbacks"],
            "fraud detection": ["red flags", "forensic accounting", "data analytics", "whistleblower"]
        }
        
        return expansions.get(current_topic.lower(), [])
    
    @staticmethod
    def technique_deepdive(technique: str) -> List[str]:
        """
        Anticipate deep-dive questions about a technique
        
        Examples:
        - "Shell companies" → ["How to detect", "Legal uses", "Red flags"]
        """
        deepdives = {
            "shell companies": ["how to detect shell companies", "shell company red flags", "beneficial ownership"],
            "invoice fraud": ["inflated invoices", "phantom vendors", "duplicate invoices"],
            "bribery": ["fcpa compliance", "bribery detection", "anti-corruption due diligence"]
        }
        
        return deepdives.get(technique.lower(), [])
    
    @staticmethod
    def case_comparison(case: str) -> List[str]:
        """
        Anticipate comparison to similar cases
        
        Examples:
        - "Theranos" → ["FTX", "Enron", "Wirecard"] (similar frauds)
        """
        comparisons = {
            "theranos": ["ftx", "enron", "wirecard"],
            "ftx": ["theranos", "mt gox", "quadriga"],
            "1mdb": ["petrobras", "siemens bribery", "unaoil"],
            "enron": ["worldcom", "tyco", "adelphia"]
        }
        
        return comparisons.get(case.lower(), [])


if __name__ == "__main__":
    # Test background retriever
    print("=== Testing Background Retriever ===")
    
    # Mock objects for testing
    class MockPersonalityLayer:
        def retrieve_relevant_context(self, query):
            return f"Mock content for {query}"
    
    class MockHotCache:
        def __init__(self):
            self.cache = {}
        
        def get_cached(self, topic):
            return self.cache.get(topic)
        
        def add_to_background_queue(self, topic, result):
            self.cache[topic] = result
    
    mock_personality = MockPersonalityLayer()
    mock_cache = MockHotCache()
    
    retriever = BackgroundRetriever(mock_personality, mock_cache)
    
    # Test anticipation
    conversation = [
        {"role": "user", "content": "Tell me about 1MDB"},
        {"role": "assistant", "content": "1MDB was a massive fraud..."}
    ]
    
    anticipated = retriever.anticipate_next_topics("What about Jho Low?", conversation)
    print(f"Anticipated topics: {anticipated}")
    
    # Test accuracy check
    accuracy = retriever.check_anticipation_accuracy("Tell me about Jho Low's shell companies")
    print(f"Anticipation was correct: {accuracy}")
    
    # Test stats
    stats = retriever.get_anticipation_stats()
    print(f"\nAnticipation stats: {stats}")
