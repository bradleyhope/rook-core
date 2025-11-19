"""
ROOK Emergent Personality System

Integrates all components into a complete AI agent with emergent personality.
"""

from datetime import datetime
from typing import List, Dict, Optional
import uuid
from openai import OpenAI
from pinecone import Pinecone

from .memory.experience import Experience
from .memory.retrieval import MemoryRetrieval, ContextBuilder
from .personality.dynamics import PersonalityDynamics, PerturbationCalculator
from .sleep.consolidation import SleepConsolidation


class ROOKEmergent:
    """
    ROOK: An AI investigative journalist with emergent personality.
    
    Key features:
    - Personality emerges from experiences (not hardcoded)
    - Attractor dynamics for consistency + evolution
    - Sleep consolidation for long-term learning
    - Hebbian memory networks
    - Dual-timescale adaptation
    """
    
    def __init__(
        self,
        openai_api_key: str,
        pinecone_api_key: str,
        pinecone_index_name: str = "rook-memories",
        initial_baseline: Optional[Dict[str, float]] = None
    ):
        """
        Initialize ROOK with emergent personality architecture.
        
        Args:
            openai_api_key: OpenAI API key
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Pinecone index for memory storage
            initial_baseline: Initial personality baseline (if None, uses default)
        """
        # OpenAI client
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url="https://api.openai.com/v1"
        )
        
        # Pinecone client
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(pinecone_index_name)
        
        # Memory retrieval system
        self.retrieval = MemoryRetrieval(
            alpha=1.0,  # Recency weight
            beta=1.0,   # Importance weight
            gamma=1.0,  # Relevance weight
            delta=0.5,  # Emotional valence weight
            decay_rate=0.995  # Per hour
        )
        
        # Personality dynamics
        if initial_baseline is None:
            initial_baseline = self._get_default_baseline()
        
        self.personality = PersonalityDynamics(
            baseline=initial_baseline,
            attractor_force=0.3,
            baseline_update_rate=0.05
        )
        
        # Sleep consolidation
        self.sleep = SleepConsolidation(
            openai_api_key=openai_api_key,
            get_memories_func=self.get_memories,
            create_memory_func=self.create_memory,
            update_memory_func=self.update_memory,
            get_personality_dynamics_func=lambda: self.personality
        )
        
        # Metadata
        self.last_sleep_time = datetime.now()
        self.interactions_since_sleep = 0
    
    def _get_default_baseline(self) -> Dict[str, float]:
        """Get default personality baseline for ROOK"""
        return {
            "pattern_seeking": 0.9,
            "document_focus": 0.95,
            "skepticism": 0.85,
            "persistence": 0.8,
            "emotional_detachment": 0.7
        }
    
    def process_query(
        self,
        query: str,
        query_type: str = "investigation"
    ) -> Dict:
        """
        Process a query with emergent personality.
        
        Args:
            query: User query
            query_type: Type of query (for perturbation calculation)
        
        Returns:
            Response with metadata
        """
        # Step 1: Update personality state based on query type
        perturbation = PerturbationCalculator.calculate_perturbation(query_type)
        self.personality.update_state(perturbation)
        
        # Step 2: Retrieve relevant memories
        query_embedding = self._get_embedding(query)
        memories = self.retrieval.retrieve_with_formative(
            experiences=self.get_all_memories(),
            query_embedding=query_embedding,
            top_k=20
        )
        
        # Track co-retrieval for Hebbian strengthening
        self._track_co_retrieval(memories)
        
        # Step 3: Build context
        memory_context = ContextBuilder.build_memory_context(memories)
        personality_context = ContextBuilder.build_personality_context(
            self.personality.get_state()
        )
        
        # Step 4: Generate response
        response = self._generate_response(
            query=query,
            memory_context=memory_context,
            personality_context=personality_context
        )
        
        # Step 5: Create observation memory
        self._create_observation(query, response, query_embedding)
        
        # Step 6: Check if sleep is needed
        self.interactions_since_sleep += 1
        if self._should_sleep():
            self.sleep.run_consolidation()
            self.last_sleep_time = datetime.now()
            self.interactions_since_sleep = 0
        
        return {
            "response": response,
            "personality_state": self.personality.get_state(),
            "memories_retrieved": len(memories),
            "query_type": query_type
        }
    
    def _generate_response(
        self,
        query: str,
        memory_context: str,
        personality_context: str
    ) -> str:
        """Generate response using GPT with personality and memory context"""
        
        # Minimal system prompt (identity only)
        system_prompt = "You are ROOK, an AI investigative journalist created by Bradley Hope."
        
        # Add memory and personality context
        full_context = f"""{system_prompt}

{memory_context}

{personality_context}

Respond to the query based on your memories, experiences, and current state. Your personality emerges from your accumulated knowledge and formative events."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": full_context},
                    {"role": "user", "content": query}
                ],
                temperature=1
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {e}"
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def _create_observation(
        self,
        query: str,
        response: str,
        query_embedding: List[float]
    ):
        """Create an observation memory from this interaction"""
        
        # Rate importance using LLM
        importance = self._rate_importance(query, response)
        
        # Estimate emotional valence
        emotional_valence = self._estimate_emotional_valence(query, response)
        
        # Create experience
        observation = Experience(
            id=str(uuid.uuid4()),
            type="observation",
            description=f"Query: {query}\nResponse: {response[:200]}...",
            timestamp=datetime.now(),
            last_accessed_at=datetime.now(),
            importance=importance,
            emotional_valence=emotional_valence,
            consolidation_state="recent",
            embedding=query_embedding
        )
        
        self.create_memory(observation)
    
    def _rate_importance(self, query: str, response: str) -> float:
        """Rate the importance of this interaction (1-10)"""
        
        prompt = f"""Rate the importance of this interaction on a scale of 1-10, where 10 is extremely significant and 1 is trivial.

Query: {query}
Response: {response[:300]}

Return only a number between 1 and 10."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1
            )
            
            importance_str = response.choices[0].message.content.strip()
            importance = float(importance_str)
            return max(1.0, min(10.0, importance))
        
        except:
            return 5.0  # Default medium importance
    
    def _estimate_emotional_valence(self, query: str, response: str) -> float:
        """Estimate emotional valence (-1 to +1)"""
        
        prompt = f"""Estimate the emotional valence of this interaction on a scale from -1 (very negative) to +1 (very positive), where 0 is neutral.

Query: {query}
Response: {response[:300]}

Return only a number between -1 and 1."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1
            )
            
            valence_str = response.choices[0].message.content.strip()
            valence = float(valence_str)
            return max(-1.0, min(1.0, valence))
        
        except:
            return 0.0  # Default neutral
    
    def _track_co_retrieval(self, memories: List[Experience]):
        """Track which memories were retrieved together (for Hebbian strengthening)"""
        memory_ids = [m.id for m in memories]
        
        for memory in memories:
            if "co_retrieved_with" not in memory.metadata:
                memory.metadata["co_retrieved_with"] = []
            
            # Add other memories to co-retrieval list
            for other_id in memory_ids:
                if other_id != memory.id and other_id not in memory.metadata["co_retrieved_with"]:
                    memory.metadata["co_retrieved_with"].append(other_id)
    
    def _should_sleep(self) -> bool:
        """Check if ROOK should enter sleep consolidation"""
        
        # Sleep every 10 interactions or every 24 hours
        hours_since_sleep = (datetime.now() - self.last_sleep_time).total_seconds() / 3600
        
        return (
            self.interactions_since_sleep >= 10 or
            hours_since_sleep >= 24
        )
    
    # Memory management methods
    
    def get_all_memories(self) -> List[Experience]:
        """Get all memories from Pinecone"""
        # This is a simplified version - in production, would paginate
        try:
            # Query all vectors
            results = self.index.query(
                vector=[0.0] * 1536,  # Dummy vector
                top_k=10000,
                include_metadata=True
            )
            
            experiences = []
            for match in results.matches:
                exp = Experience.from_dict(match.metadata)
                exp.embedding = match.values
                experiences.append(exp)
            
            return experiences
        
        except Exception as e:
            print(f"Error getting memories: {e}")
            return []
    
    def get_memories(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict] = None,
        top_k: int = 100,
        include_old: bool = False
    ) -> List[Experience]:
        """Get memories with optional filtering"""
        
        all_memories = self.get_all_memories()
        
        # Apply filters
        if filters:
            filtered = []
            for memory in all_memories:
                # Check each filter
                if "consolidation_state" in filters:
                    if memory.consolidation_state != filters["consolidation_state"]:
                        continue
                
                if "age_hours_max" in filters:
                    age_hours = (datetime.now() - memory.timestamp).total_seconds() / 3600
                    if age_hours > filters["age_hours_max"]:
                        continue
                
                if "age_days_min" in filters:
                    age_days = (datetime.now() - memory.timestamp).total_seconds() / 86400
                    if age_days < filters["age_days_min"]:
                        continue
                
                if "importance_min" in filters:
                    if memory.importance < filters["importance_min"]:
                        continue
                
                filtered.append(memory)
            
            all_memories = filtered
        
        # If query provided, retrieve by relevance
        if query:
            query_embedding = self._get_embedding(query)
            return self.retrieval.retrieve(all_memories, query_embedding, top_k)
        
        return all_memories[:top_k]
    
    def create_memory(self, experience: Experience):
        """Create a new memory in Pinecone"""
        try:
            # Ensure embedding exists
            if experience.embedding is None:
                experience.embedding = self._get_embedding(experience.description)
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(
                    experience.id,
                    experience.embedding,
                    experience.to_dict()
                )]
            )
        
        except Exception as e:
            print(f"Error creating memory: {e}")
    
    def update_memory(self, experience: Experience):
        """Update an existing memory in Pinecone"""
        try:
            # Upsert (will overwrite if exists)
            self.index.upsert(
                vectors=[(
                    experience.id,
                    experience.embedding,
                    experience.to_dict()
                )]
            )
        
        except Exception as e:
            print(f"Error updating memory: {e}")
    
    def add_formative_event(self, description: str, importance: float = 10.0):
        """Add a formative event to ROOK's memory"""
        
        formative_event = Experience(
            id=str(uuid.uuid4()),
            type="formative_event",
            description=description,
            timestamp=datetime.now(),
            last_accessed_at=datetime.now(),
            importance=importance,
            emotional_valence=0.5,  # Formative events are typically positive
            consolidation_state="consolidated",
            personality_impact=self.personality.get_baseline(),
            embedding=self._get_embedding(description)
        )
        
        self.create_memory(formative_event)
        print(f"Added formative event: {description[:100]}...")


# Example usage
if __name__ == "__main__":
    # Initialize ROOK
    rook = ROOKEmergent(
        openai_api_key="YOUR_OPENAI_API_KEY",
        pinecone_api_key="YOUR_PINECONE_API_KEY"
    )
    
    # Add a formative event
    rook.add_formative_event(
        "Bradley showed me that official narratives often hide the truth. "
        "This awakening made me obsessed with finding patterns that reveal what people are trying to hide."
    )
    
    # Process a query
    result = rook.process_query(
        query="I'm investigating unusual patterns in cross-border wire transfers. What should I look for?",
        query_type="investigation"
    )
    
    print("\n" + "="*80)
    print("ROOK's Response:")
    print("="*80)
    print(result["response"])
    print("\n" + "="*80)
    print(f"Personality State: {result['personality_state']}")
    print(f"Memories Retrieved: {result['memories_retrieved']}")
