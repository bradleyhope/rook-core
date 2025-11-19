"""
ROOK Experience Memory Schema

Implements the rich memory structure for ROOK's emergent personality.
Based on research findings from Stanford Generative Agents, Mem0, and neuroscience.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Experience:
    """
    A single unit of memory representing a lived experience.
    
    This is the fundamental building block of ROOK's memory system.
    Unlike simple fact storage, Experiences capture the full context
    of an event including its emotional and personality impact.
    """
    
    # Core Identity
    id: str
    type: str  # "observation", "reflection", "meta_reflection", "formative_event"
    description: str
    
    # Temporal Information
    timestamp: datetime
    last_accessed_at: datetime
    
    # Weighting Factors (for retrieval)
    importance: float  # 1-10, LLM-rated cognitive significance
    emotional_valence: float  # -1 to +1, emotional charge
    
    # State & Organization
    consolidation_state: str = "recent"  # "recent", "consolidated", "archived"
    personality_impact: Dict[str, float] = field(default_factory=dict)
    
    # Connections & Citations
    citations: List[str] = field(default_factory=list)  # Referenced memories
    connections: Dict[str, float] = field(default_factory=dict)  # Hebbian links
    
    # Vector Embedding (for semantic search)
    embedding: Optional[List[float]] = None
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "importance": self.importance,
            "emotional_valence": self.emotional_valence,
            "consolidation_state": self.consolidation_state,
            "personality_impact": self.personality_impact,
            "citations": self.citations,
            "connections": self.connections,
            "embedding": self.embedding,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Experience':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            type=data["type"],
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            last_accessed_at=datetime.fromisoformat(data["last_accessed_at"]),
            importance=data["importance"],
            emotional_valence=data["emotional_valence"],
            consolidation_state=data.get("consolidation_state", "recent"),
            personality_impact=data.get("personality_impact", {}),
            citations=data.get("citations", []),
            connections=data.get("connections", {}),
            embedding=data.get("embedding"),
            metadata=data.get("metadata", {})
        )
    
    def refresh_access(self):
        """Update last_accessed_at to now (for recency scoring)"""
        self.last_accessed_at = datetime.now()
    
    def strengthen_connection(self, other_id: str, amount: float = 0.1):
        """Strengthen Hebbian connection to another memory"""
        current = self.connections.get(other_id, 0.0)
        self.connections[other_id] = min(1.0, current + amount)
    
    def weaken_connection(self, other_id: str, amount: float = 0.05):
        """Weaken Hebbian connection to another memory"""
        current = self.connections.get(other_id, 0.0)
        self.connections[other_id] = max(0.0, current - amount)
    
    def is_formative(self) -> bool:
        """Check if this is a formative event"""
        return self.type == "formative_event"
    
    def is_reflection(self) -> bool:
        """Check if this is any type of reflection"""
        return self.type in ["reflection", "meta_reflection"]
    
    def __repr__(self):
        return f"Experience(id={self.id}, type={self.type}, importance={self.importance})"
