"""
ROOK Memory Retrieval System

Implements weighted retrieval based on Stanford Generative Agents research.
Combines recency, importance, relevance, and emotional valence.
"""

from datetime import datetime
from typing import List, Dict, Optional
import math
import numpy as np
from .experience import Experience


class MemoryRetrieval:
    """
    Weighted memory retrieval system for ROOK.
    
    Retrieval score = α*recency + β*importance + γ*relevance + δ*emotional_valence
    
    Based on Stanford Generative Agents (Park et al., 2023)
    """
    
    def __init__(
        self,
        alpha: float = 1.0,  # Recency weight
        beta: float = 1.0,   # Importance weight
        gamma: float = 1.0,  # Relevance weight
        delta: float = 0.5,  # Emotional valence weight
        decay_rate: float = 0.995  # Exponential decay per hour
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.decay_rate = decay_rate
    
    def calculate_recency_score(self, experience: Experience) -> float:
        """
        Calculate recency score using exponential decay.
        
        Score decreases exponentially based on hours since last access.
        Accessing a memory refreshes its recency (human-like memory).
        """
        hours_since_access = (datetime.now() - experience.last_accessed_at).total_seconds() / 3600
        return self.decay_rate ** hours_since_access
    
    def calculate_importance_score(self, experience: Experience) -> float:
        """
        Normalize importance (1-10) to 0-1 range.
        """
        return experience.importance / 10.0
    
    def calculate_relevance_score(
        self,
        query_embedding: List[float],
        experience: Experience
    ) -> float:
        """
        Calculate cosine similarity between query and experience embeddings.
        """
        if experience.embedding is None:
            return 0.0
        
        # Cosine similarity
        query_vec = np.array(query_embedding)
        exp_vec = np.array(experience.embedding)
        
        dot_product = np.dot(query_vec, exp_vec)
        query_norm = np.linalg.norm(query_vec)
        exp_norm = np.linalg.norm(exp_vec)
        
        if query_norm == 0 or exp_norm == 0:
            return 0.0
        
        return dot_product / (query_norm * exp_norm)
    
    def calculate_emotional_score(self, experience: Experience) -> float:
        """
        Use absolute value of emotional valence.
        Highly emotional events (positive or negative) are more salient.
        """
        return abs(experience.emotional_valence)
    
    def calculate_retrieval_score(
        self,
        experience: Experience,
        query_embedding: Optional[List[float]] = None
    ) -> float:
        """
        Calculate weighted retrieval score for an experience.
        
        Returns:
            Combined score (higher = more relevant)
        """
        recency = self.calculate_recency_score(experience)
        importance = self.calculate_importance_score(experience)
        emotional = self.calculate_emotional_score(experience)
        
        # Relevance requires query embedding
        if query_embedding is not None:
            relevance = self.calculate_relevance_score(query_embedding, experience)
        else:
            relevance = 0.0
        
        # Weighted combination
        score = (
            self.alpha * recency +
            self.beta * importance +
            self.gamma * relevance +
            self.delta * emotional
        )
        
        return score
    
    def retrieve(
        self,
        experiences: List[Experience],
        query_embedding: Optional[List[float]] = None,
        top_k: int = 20,
        refresh_access: bool = True
    ) -> List[Experience]:
        """
        Retrieve top-k most relevant experiences.
        
        Args:
            experiences: List of all available experiences
            query_embedding: Vector embedding of the query
            top_k: Number of experiences to retrieve
            refresh_access: Whether to update last_accessed_at for retrieved memories
        
        Returns:
            List of top-k experiences, sorted by relevance
        """
        # Calculate scores for all experiences
        scored_experiences = []
        for exp in experiences:
            score = self.calculate_retrieval_score(exp, query_embedding)
            scored_experiences.append((score, exp))
        
        # Sort by score (descending)
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        
        # Get top-k
        top_experiences = [exp for score, exp in scored_experiences[:top_k]]
        
        # Refresh access times (Stanford approach: retrieval refreshes memory)
        if refresh_access:
            for exp in top_experiences:
                exp.refresh_access()
        
        return top_experiences
    
    def retrieve_formative_events(
        self,
        experiences: List[Experience]
    ) -> List[Experience]:
        """
        Retrieve all formative events (always included in context).
        """
        return [exp for exp in experiences if exp.is_formative()]
    
    def retrieve_with_formative(
        self,
        experiences: List[Experience],
        query_embedding: Optional[List[float]] = None,
        top_k: int = 20
    ) -> List[Experience]:
        """
        Retrieve memories including formative events + top-k relevant experiences.
        
        Formative events are always included (not counted in top_k).
        """
        # Get formative events (always included)
        formative = self.retrieve_formative_events(experiences)
        
        # Get non-formative experiences
        non_formative = [exp for exp in experiences if not exp.is_formative()]
        
        # Retrieve top-k from non-formative
        relevant = self.retrieve(non_formative, query_embedding, top_k)
        
        # Combine: formative first, then relevant
        return formative + relevant


class ContextBuilder:
    """
    Builds context strings from retrieved experiences for LLM prompts.
    """
    
    @staticmethod
    def build_memory_context(experiences: List[Experience]) -> str:
        """
        Convert experiences into a formatted context string.
        """
        if not experiences:
            return ""
        
        # Group by type
        formative = [e for e in experiences if e.type == "formative_event"]
        reflections = [e for e in experiences if e.is_reflection()]
        observations = [e for e in experiences if e.type == "observation"]
        
        context_parts = []
        
        # Formative events (foundational identity)
        if formative:
            context_parts.append("# Formative Events")
            for exp in formative:
                context_parts.append(f"- {exp.description}")
            context_parts.append("")
        
        # Reflections (consolidated insights)
        if reflections:
            context_parts.append("# Reflections")
            for exp in reflections:
                context_parts.append(f"- {exp.description}")
            context_parts.append("")
        
        # Observations (direct experiences)
        if observations:
            context_parts.append("# Relevant Experiences")
            for exp in observations:
                context_parts.append(f"- {exp.description}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def build_personality_context(personality_state: Dict[str, float]) -> str:
        """
        Convert personality state into a context string.
        """
        if not personality_state:
            return ""
        
        context = "# Current Personality State\n"
        for trait, value in personality_state.items():
            trait_name = trait.replace("_", " ").title()
            context += f"- {trait_name}: {value:.2f}\n"
        
        return context
