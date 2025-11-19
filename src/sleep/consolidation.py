"""
ROOK Sleep Consolidation System

Implements offline memory consolidation inspired by:
- Stanford Generative Agents (reflection generation)
- Sleep Replay Consolidation (old memory replay)
- Neuroscience (memory consolidation during sleep)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Callable
import random
import uuid
from openai import OpenAI

from ..memory.experience import Experience
from ..personality.dynamics import PersonalityDynamics


class SleepConsolidation:
    """
    Manages ROOK's sleep consolidation process.
    
    Five-phase consolidation:
    1. Reflection Generation - Synthesize recent memories
    2. Old Memory Replay - Prevent catastrophic forgetting
    3. Personality Baseline Update - Evolve baseline if drift detected
    4. Hebbian Memory Strengthening - Strengthen co-retrieved connections
    5. Meta-Reflection - Generate insights from reflections
    """
    
    def __init__(
        self,
        openai_api_key: str,
        get_memories_func: Callable,
        create_memory_func: Callable,
        update_memory_func: Callable,
        get_personality_dynamics_func: Callable
    ):
        """
        Initialize sleep consolidation system.
        
        Args:
            openai_api_key: OpenAI API key
            get_memories_func: Function to retrieve memories
            create_memory_func: Function to create new memories
            update_memory_func: Function to update existing memories
            get_personality_dynamics_func: Function to get personality dynamics
        """
        self.client = OpenAI(
            api_key=openai_api_key,
            base_url="https://api.openai.com/v1"
        )
        self.get_memories = get_memories_func
        self.create_memory = create_memory_func
        self.update_memory = update_memory_func
        self.get_personality_dynamics = get_personality_dynamics_func
    
    def run_consolidation(self) -> Dict:
        """
        Execute the complete sleep consolidation cycle.
        
        Returns:
            Statistics about the consolidation process
        """
        stats = {
            "start_time": datetime.now().isoformat(),
            "reflections_generated": 0,
            "old_memories_replayed": 0,
            "baseline_updated": False,
            "connections_strengthened": 0,
            "meta_reflections_generated": 0
        }
        
        print("🌙 ROOK entering sleep consolidation...")
        
        # Phase 1: Reflection Generation
        reflections = self.phase1_reflection_generation()
        stats["reflections_generated"] = len(reflections)
        print(f"  ✓ Phase 1: Generated {len(reflections)} reflections")
        
        # Phase 2: Old Memory Replay
        replayed = self.phase2_old_memory_replay()
        stats["old_memories_replayed"] = len(replayed)
        print(f"  ✓ Phase 2: Replayed {len(replayed)} old memories")
        
        # Phase 3: Personality Baseline Update
        baseline_updated = self.phase3_personality_baseline_update()
        stats["baseline_updated"] = baseline_updated
        if baseline_updated:
            print(f"  ✓ Phase 3: Baseline personality updated")
        else:
            print(f"  ✓ Phase 3: Baseline stable (no update needed)")
        
        # Phase 4: Hebbian Memory Strengthening
        strengthened = self.phase4_hebbian_strengthening()
        stats["connections_strengthened"] = strengthened
        print(f"  ✓ Phase 4: Strengthened {strengthened} memory connections")
        
        # Phase 5: Meta-Reflection
        if len(reflections) >= 3:
            meta_reflections = self.phase5_meta_reflection(reflections)
            stats["meta_reflections_generated"] = len(meta_reflections)
            print(f"  ✓ Phase 5: Generated {len(meta_reflections)} meta-reflections")
        else:
            print(f"  ✓ Phase 5: Skipped (not enough reflections)")
        
        stats["end_time"] = datetime.now().isoformat()
        print("☀️ ROOK woke up from sleep consolidation")
        
        return stats
    
    def phase1_reflection_generation(self) -> List[Experience]:
        """
        Phase 1: Generate reflections from recent high-importance memories.
        
        Based on Stanford Generative Agents approach.
        """
        # Get recent unconsolidated memories
        recent_memories = self.get_memories(
            filters={
                "consolidation_state": "recent",
                "age_hours_max": 48,
                "importance_min": 6
            }
        )
        
        if not recent_memories:
            return []
        
        # Generate consolidation questions
        questions = self._generate_consolidation_questions(recent_memories)
        
        # For each question, retrieve and reflect
        reflections = []
        for question in questions:
            # Retrieve relevant memories (recent + old)
            relevant_memories = self.get_memories(
                query=question,
                top_k=20,
                include_old=True
            )
            
            # Generate insight
            insight = self._generate_insight(question, relevant_memories)
            
            if insight:
                # Create reflection memory
                reflection = Experience(
                    id=str(uuid.uuid4()),
                    type="reflection",
                    description=insight["text"],
                    timestamp=datetime.now(),
                    last_accessed_at=datetime.now(),
                    importance=insight["importance"],
                    emotional_valence=insight.get("emotional_valence", 0.0),
                    consolidation_state="consolidated",
                    citations=[m.id for m in relevant_memories[:5]]
                )
                
                self.create_memory(reflection)
                reflections.append(reflection)
        
        # Mark recent memories as consolidated
        for memory in recent_memories:
            memory.consolidation_state = "consolidated"
            self.update_memory(memory)
        
        return reflections
    
    def phase2_old_memory_replay(self, count: int = 10) -> List[Experience]:
        """
        Phase 2: Replay old memories to prevent catastrophic forgetting.
        
        Based on Sleep Replay Consolidation (Tadros et al., 2022).
        """
        # Get old, important memories
        old_memories = self.get_memories(
            filters={
                "age_days_min": 30,
                "importance_min": 6
            }
        )
        
        if not old_memories:
            return []
        
        # Sample randomly, weighted by importance
        weights = [m.importance for m in old_memories]
        total_weight = sum(weights)
        probabilities = [w / total_weight for w in weights]
        
        sample_count = min(count, len(old_memories))
        sampled = random.choices(old_memories, weights=probabilities, k=sample_count)
        
        # "Replay" by refreshing access time
        for memory in sampled:
            memory.refresh_access()
            self.update_memory(memory)
        
        return sampled
    
    def phase3_personality_baseline_update(self) -> bool:
        """
        Phase 3: Update personality baseline if significant drift detected.
        
        Based on attractor dynamics (Sosnowska et al., 2019).
        """
        dynamics = self.get_personality_dynamics()
        
        # Check if update is needed
        if not dynamics.should_update_baseline(drift_threshold=0.1, duration_hours=48):
            return False
        
        # Calculate drift and update baseline
        drift = dynamics.calculate_drift(recent_hours=48)
        dynamics.update_baseline(drift)
        
        return True
    
    def phase4_hebbian_strengthening(self) -> int:
        """
        Phase 4: Strengthen connections between frequently co-retrieved memories.
        
        Hebbian plasticity: "Neurons that fire together, wire together"
        """
        # Get memories with co-retrieval metadata
        all_memories = self.get_memories(filters={})
        
        connections_strengthened = 0
        
        for memory in all_memories:
            # Get memories that were co-retrieved with this one
            co_retrieved = memory.metadata.get("co_retrieved_with", [])
            
            for other_id in co_retrieved:
                # Strengthen connection
                memory.strengthen_connection(other_id, amount=0.1)
                connections_strengthened += 1
            
            # Weaken unused connections
            for connected_id, strength in list(memory.connections.items()):
                if connected_id not in co_retrieved and strength > 0:
                    memory.weaken_connection(connected_id, amount=0.05)
            
            self.update_memory(memory)
        
        return connections_strengthened
    
    def phase5_meta_reflection(self, reflections: List[Experience]) -> List[Experience]:
        """
        Phase 5: Generate meta-reflections (reflections on reflections).
        
        Creates abstract, cross-domain understanding.
        """
        if len(reflections) < 3:
            return []
        
        # Generate meta-reflection questions
        meta_questions = self._generate_meta_reflection_questions(reflections)
        
        meta_reflections = []
        for question in meta_questions:
            # Generate meta-insight
            insight = self._generate_insight(question, reflections)
            
            if insight:
                # Create meta-reflection memory
                meta_reflection = Experience(
                    id=str(uuid.uuid4()),
                    type="meta_reflection",
                    description=insight["text"],
                    timestamp=datetime.now(),
                    last_accessed_at=datetime.now(),
                    importance=9,  # Meta-reflections are very important
                    emotional_valence=insight.get("emotional_valence", 0.0),
                    consolidation_state="consolidated",
                    citations=[r.id for r in reflections]
                )
                
                self.create_memory(meta_reflection)
                meta_reflections.append(meta_reflection)
        
        return meta_reflections
    
    def _generate_consolidation_questions(
        self,
        memories: List[Experience],
        count: int = 3
    ) -> List[str]:
        """Generate questions for reflection based on recent memories"""
        
        memory_descriptions = "\n".join([
            f"- {m.description}" for m in memories[:10]
        ])
        
        prompt = f"""Based on these recent experiences:

{memory_descriptions}

Generate {count} insightful questions that would help consolidate these experiences into higher-level understanding. Focus on patterns, connections, and insights.

Return only the questions, one per line."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1
            )
            
            questions = response.choices[0].message.content.strip().split("\n")
            return [q.strip("- ").strip() for q in questions if q.strip()]
        
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    def _generate_meta_reflection_questions(
        self,
        reflections: List[Experience],
        count: int = 2
    ) -> List[str]:
        """Generate meta-reflection questions from reflections"""
        
        reflection_descriptions = "\n".join([
            f"- {r.description}" for r in reflections
        ])
        
        prompt = f"""Based on these reflections:

{reflection_descriptions}

Generate {count} meta-level questions that synthesize these insights into broader understanding. Focus on overarching patterns and principles.

Return only the questions, one per line."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1
            )
            
            questions = response.choices[0].message.content.strip().split("\n")
            return [q.strip("- ").strip() for q in questions if q.strip()]
        
        except Exception as e:
            print(f"Error generating meta-questions: {e}")
            return []
    
    def _generate_insight(
        self,
        question: str,
        memories: List[Experience]
    ) -> Dict:
        """Generate insight from question and relevant memories"""
        
        memory_descriptions = "\n".join([
            f"- {m.description}" for m in memories[:10]
        ])
        
        prompt = f"""Question: {question}

Relevant experiences:
{memory_descriptions}

Generate a concise insight that answers this question based on the experiences. Also rate the importance (1-10) and emotional valence (-1 to +1) of this insight.

Return as JSON:
{{
  "text": "The insight text",
  "importance": 8,
  "emotional_valence": 0.2
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=1
            )
            
            import json
            insight = json.loads(response.choices[0].message.content)
            return insight
        
        except Exception as e:
            print(f"Error generating insight: {e}")
            return None
