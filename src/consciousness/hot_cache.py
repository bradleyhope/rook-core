"""
Hot Cache - ROOK's Working Memory
Fast-access layer for immediate context (< 50ms retrieval)
"""

import time
from typing import Dict, List, Any, Optional
from collections import OrderedDict
from datetime import datetime, timedelta


class HotCache:
    """
    Fast-access working memory for ROOK
    
    Maintains:
    - Current context (what ROOK is thinking about RIGHT NOW)
    - Recent retrievals (last 10 Pinecone queries, LRU cache)
    - Active topics (from current conversation)
    - Background queue (pre-fetched for anticipated questions)
    """
    
    def __init__(self, max_recent=10, max_topics=5):
        self.current_context = {}
        self.recent_retrievals = OrderedDict()  # LRU cache
        self.active_topics = []
        self.background_queue = OrderedDict()
        self.max_recent = max_recent
        self.max_topics = max_topics
        self.last_refresh = datetime.now()
        
    def get_immediate_context(self) -> Dict[str, Any]:
        """
        Return what's immediately on ROOK's mind (< 50ms)
        
        Returns:
            dict: Current focus, recent thoughts, active topics
        """
        return {
            "current_focus": self.current_context,
            "recent_thoughts": list(self.recent_retrievals.values())[-5:],
            "active_topics": self.active_topics,
            "last_updated": self.last_refresh.isoformat()
        }
    
    def update_context(self, topic: str, content: Any, metadata: Optional[Dict] = None):
        """
        Add to working memory
        
        Args:
            topic: Topic key (e.g., "1MDB", "shell_companies")
            content: Retrieved content
            metadata: Additional metadata (scores, sources, etc.)
        """
        timestamp = datetime.now()
        
        # Update current context
        self.current_context[topic] = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "access_count": self.current_context.get(topic, {}).get("access_count", 0) + 1
        }
        
        # Add to recent retrievals (LRU)
        self.recent_retrievals[topic] = {
            "content": content,
            "timestamp": timestamp,
            "metadata": metadata
        }
        
        # Maintain LRU size
        if len(self.recent_retrievals) > self.max_recent:
            self.recent_retrievals.popitem(last=False)  # Remove oldest
        
        # Update active topics
        if topic not in self.active_topics:
            self.active_topics.append(topic)
            if len(self.active_topics) > self.max_topics:
                self.active_topics.pop(0)  # Remove oldest topic
    
    def get_cached(self, topic: str) -> Optional[Dict]:
        """
        Get from cache if available (fast path)
        
        Args:
            topic: Topic to retrieve
            
        Returns:
            Cached content if available, None otherwise
        """
        # Check current context first
        if topic in self.current_context:
            self.current_context[topic]["access_count"] += 1
            return self.current_context[topic]
        
        # Check recent retrievals
        if topic in self.recent_retrievals:
            # Move to end (most recently used)
            self.recent_retrievals.move_to_end(topic)
            return self.recent_retrievals[topic]
        
        # Check background queue
        if topic in self.background_queue:
            return self.background_queue[topic]
        
        return None
    
    def add_to_background_queue(self, topic: str, future_result: Any):
        """
        Add pre-fetched result to background queue
        
        Args:
            topic: Topic that was pre-fetched
            future_result: Result from async retrieval
        """
        self.background_queue[topic] = {
            "content": future_result,
            "timestamp": datetime.now(),
            "prefetched": True
        }
        
        # Limit queue size
        if len(self.background_queue) > 20:
            self.background_queue.popitem(last=False)
    
    def refresh_cache(self, new_readings: List[Dict]):
        """
        Refresh cache with new readings (hourly update)
        
        Args:
            new_readings: List of recent reading memories
        """
        for reading in new_readings:
            topic = reading.get("topic") or reading.get("title")
            if topic:
                self.update_context(
                    topic=topic,
                    content=reading.get("summary") or reading.get("content"),
                    metadata={
                        "source": reading.get("source"),
                        "date": reading.get("date"),
                        "type": "reading"
                    }
                )
        
        self.last_refresh = datetime.now()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            dict: Hit rates, sizes, access patterns
        """
        total_accesses = sum(
            ctx.get("access_count", 0) 
            for ctx in self.current_context.values()
        )
        
        return {
            "current_context_size": len(self.current_context),
            "recent_retrievals_size": len(self.recent_retrievals),
            "active_topics": self.active_topics,
            "background_queue_size": len(self.background_queue),
            "total_accesses": total_accesses,
            "last_refresh": self.last_refresh.isoformat(),
            "cache_age_minutes": (datetime.now() - self.last_refresh).total_seconds() / 60
        }
    
    def clear_old_entries(self, max_age_hours: int = 24):
        """
        Clear entries older than max_age_hours
        
        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        # Clear old context
        self.current_context = {
            k: v for k, v in self.current_context.items()
            if v.get("timestamp", datetime.min) > cutoff
        }
        
        # Clear old retrievals
        self.recent_retrievals = OrderedDict({
            k: v for k, v in self.recent_retrievals.items()
            if v.get("timestamp", datetime.min) > cutoff
        })
        
        # Clear old background queue
        self.background_queue = OrderedDict({
            k: v for k, v in self.background_queue.items()
            if v.get("timestamp", datetime.min) > cutoff
        })


# Global hot cache instance
_hot_cache = None

def get_hot_cache() -> HotCache:
    """Get or create global hot cache instance"""
    global _hot_cache
    if _hot_cache is None:
        _hot_cache = HotCache()
    return _hot_cache


def reset_hot_cache():
    """Reset global hot cache (for testing)"""
    global _hot_cache
    _hot_cache = HotCache()


if __name__ == "__main__":
    # Test the hot cache
    cache = HotCache()
    
    # Add some context
    cache.update_context(
        topic="1MDB",
        content="Jho Low created Good Star Limited in Seychelles...",
        metadata={"source": "Billion Dollar Whale", "score": 0.95}
    )
    
    cache.update_context(
        topic="shell_companies",
        content="Shell companies are entities with no active business...",
        metadata={"source": "archive", "score": 0.87}
    )
    
    # Test retrieval
    print("=== Immediate Context ===")
    context = cache.get_immediate_context()
    print(f"Active topics: {context['active_topics']}")
    print(f"Recent thoughts: {len(context['recent_thoughts'])} items")
    
    # Test cache hit
    print("\n=== Cache Hit Test ===")
    start = time.time()
    result = cache.get_cached("1MDB")
    elapsed_ms = (time.time() - start) * 1000
    print(f"Retrieved '1MDB' in {elapsed_ms:.2f}ms")
    print(f"Access count: {result['access_count']}")
    
    # Test cache stats
    print("\n=== Cache Stats ===")
    stats = cache.get_cache_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
