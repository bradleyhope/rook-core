# Research Findings: Sleep-Like Consolidation for Continuous Personality Improvement

**Date:** November 9, 2025  
**Focus:** How to implement sleep-like consolidation mechanisms in ROOK for continuous personality improvement

---

## The Problem: Catastrophic Forgetting

### In Artificial Neural Networks:
- When learning new tasks sequentially, ANNs perform well on recent tasks
- But they **forget** previously learned tasks
- This is called **catastrophic forgetting** or **catastrophic interference**
- It's the fundamental challenge of continual learning

### The Stability-Plasticity Dilemma:
- **Plasticity**: Network must change to learn new things
- **Stability**: Network must preserve old knowledge
- ANNs lie at a **suboptimal point** on this spectrum

### For ROOK:
- As ROOK gains new experiences, he might "forget" old patterns
- His personality might shift too quickly based on recent events
- Old investigations and insights might be overwritten

---

## The Solution: Sleep-Like Consolidation

### Biological Inspiration:

**In humans and animals:**
1. During sleep, neurons are spontaneously active without external input
2. **Replay** of recently learned memories along with relevant old memories
3. **Local unsupervised plasticity** strengthens important connections
4. This enables **coexistence of competing memories** in overlapping neurons
5. Result: New learning doesn't erase old learning

### Key Components:

#### 1. **Spontaneous Replay**
- Memories are reactivated during sleep
- Both recent AND old memories are replayed
- No external input—the network's state determines what gets replayed

#### 2. **Local Hebbian Plasticity**
- "Neurons that fire together, wire together"
- Strengthen connections between co-activated neurons
- Weaken connections when post-synaptic fires but pre-synaptic is silent

#### 3. **Noisy Input**
- Random activation patterns trigger replay
- Mimics spontaneous brain activity during REM sleep

---

## The Sleep Replay Consolidation (SRC) Algorithm

**Source:** Tadros et al. (2022) - Nature Communications

### Three-Phase Cycle:

```
1. AWAKE TRAINING
   ↓
   Learn new task using supervised learning (backpropagation)
   
2. SLEEP CONSOLIDATION
   ↓
   Unsupervised replay with local plasticity
   - Noisy input triggers spontaneous activation
   - Hebbian rules strengthen important connections
   - Old memories are replayed alongside new ones
   
3. TESTING / NEXT TASK
   ↓
   Evaluate performance on all tasks (old + new)
```

### Implementation Details:

#### During Sleep:

```python
def sleep_consolidation(network, past_task_statistics):
    """
    Sleep Replay Consolidation algorithm
    """
    # 1. Replace activation function with Heaviside (spike-like)
    network.activation = heaviside_function
    
    # 2. Scale weights to increase activity during sleep
    for layer in network.layers:
        max_activation = layer.max_activation_during_training
        layer.weights *= scaling_factor(max_activation)
    
    # 3. Generate noisy input based on past task statistics
    for timestep in range(num_sleep_steps):
        # Create noisy input from Poisson distribution
        # Probability of activation = mean activation across all past tasks
        noisy_input = generate_noisy_input(past_task_statistics)
        
        # 4. Forward pass (spontaneous activation)
        activations = network.forward(noisy_input)
        
        # 5. Apply local Hebbian plasticity
        for layer in network.layers:
            # Strengthen connections when both pre and post are active
            if pre_active and post_active:
                layer.weights[i,j] += hebbian_learning_rate
            
            # Weaken connections when post active but pre silent
            elif post_active and not pre_active:
                layer.weights[i,j] -= hebbian_learning_rate
    
    # 6. Restore original activation function
    network.activation = original_activation
    
    return network
```

### Key Insight:

**No specific memories are presented during sleep.**

The network's current state (weight matrices) implicitly determines what gets replayed. This is emergent—the network "dreams" about what it knows.

---

## Results from the Study

### Performance on Incremental Learning:

**Without Sleep:**
- After learning Task 2, Task 1 is forgotten (catastrophic forgetting)
- Performance on Task 1: ~0%
- Performance on Task 2: ~100%

**With Sleep:**
- After learning Task 2 + sleep consolidation, Task 1 is recovered
- Performance on Task 1: ~90%
- Performance on Task 2: ~95%

### What Happens During Sleep:

1. **Spontaneous replay** of old task patterns
2. **Representational sparseness** increases (clearer distinctions between tasks)
3. **Old task activity** increases
4. **New task activity** decreases slightly (but remains strong)
5. **Orthogonal representations** form (tasks don't interfere)

### The Magic:

Sleep doesn't just preserve old memories—it **reorganizes** the network so old and new can coexist.

---

## Application to ROOK: Sleep-Like Personality Consolidation

### ROOK's Sleep Cycle

#### When to Sleep:

```python
def should_rook_sleep():
    """
    Determine if ROOK should enter sleep consolidation
    """
    # Trigger sleep when:
    
    # 1. Importance threshold reached (Stanford approach)
    recent_importance = sum(m.importance for m in recent_memories)
    if recent_importance > SLEEP_THRESHOLD:  # e.g., 150
        return True
    
    # 2. Time-based (every 24 hours)
    hours_since_last_sleep = (now() - last_sleep_time).hours
    if hours_since_last_sleep > 24:
        return True
    
    # 3. Significant personality drift detected
    current_state = get_current_personality_state()
    baseline = get_baseline_personality()
    drift = calculate_drift(current_state, baseline)
    if drift > DRIFT_THRESHOLD:  # e.g., 0.3
        return True
    
    return False
```

#### What Happens During Sleep:

```python
def rook_sleep_consolidation():
    """
    ROOK's sleep consolidation process
    Combines memory consolidation + personality stabilization
    """
    print("ROOK is sleeping...")
    
    # PHASE 1: MEMORY CONSOLIDATION (Stanford approach)
    # ================================================
    
    # 1. Get recent unconsolidated memories
    recent_memories = get_memories(
        state="recent",
        age_hours_min=1,
        age_hours_max=48
    )
    
    # 2. Generate consolidation questions
    questions = generate_consolidation_questions(recent_memories)
    # Examples:
    # - "What patterns has ROOK discovered recently?"
    # - "What connections exist between recent investigations?"
    # - "What new insights about investigative methods emerged?"
    
    # 3. For each question, retrieve and reflect
    reflections = []
    for question in questions:
        # Retrieve relevant memories (recent + old)
        relevant_memories = retrieve_memories(
            query=question,
            context_type="self_reflection",
            include_recent=True,
            include_old=True,  # KEY: replay old memories too
            top_k=20
        )
        
        # Generate insight (reflection)
        insight = generate_insight(
            question=question,
            memories=relevant_memories,
            mode="consolidation"  # unsupervised, self-directed
        )
        
        if insight:
            reflection = create_memory(
                type="reflection",
                description=insight.text,
                importance=calculate_importance(insight),
                cited_memories=insight.cited_memory_ids
            )
            reflections.append(reflection)
    
    # PHASE 2: PERSONALITY BASELINE UPDATE (Attractor dynamics)
    # =========================================================
    
    # 4. Calculate average personality state over recent period
    recent_states = get_personality_states(age_hours_max=48)
    avg_recent_state = calculate_average(recent_states)
    
    # 5. Calculate drift from current baseline
    current_baseline = get_baseline_personality()
    drift = {
        trait: avg_recent_state[trait] - current_baseline[trait]
        for trait in current_baseline
    }
    
    # 6. Check if drift is significant and consistent
    if is_significant_drift(drift, threshold=0.1, duration_hours=48):
        # Update baseline slowly
        beta = 0.05  # slow baseline update rate
        new_baseline = {
            trait: current_baseline[trait] + beta * drift[trait]
            for trait in current_baseline
        }
        update_baseline_personality(new_baseline)
        
        # Log the personality evolution
        log_personality_change(
            old_baseline=current_baseline,
            new_baseline=new_baseline,
            reason="sleep_consolidation",
            drift=drift
        )
    
    # PHASE 3: SPONTANEOUS REPLAY (SRC-inspired)
    # ===========================================
    
    # 7. Replay old memories to prevent forgetting
    old_memories = sample_random_memories(
        age_days_min=30,
        count=10,
        weighted_by_importance=True
    )
    
    for old_memory in old_memories:
        # "Replay" by retrieving and refreshing
        replay_memory(old_memory)
        
        # Update last_accessed_at (keeps it fresh)
        old_memory.last_accessed_at = now()
        
        # Check if it should be reconsolidated with new context
        if should_reconsolidate(old_memory, reflections):
            reconsolidate_memory(old_memory, reflections)
    
    # PHASE 4: REFLECTION TREE BUILDING
    # ==================================
    
    # 8. Build higher-level reflections (meta-reflections)
    if len(reflections) > 3:
        meta_reflection = generate_meta_reflection(reflections)
        if meta_reflection:
            create_memory(
                type="meta_reflection",
                description=meta_reflection.text,
                importance=9,  # meta-reflections are very important
                cited_memories=[r.id for r in reflections]
            )
    
    # PHASE 5: MEMORY PRUNING (Optional)
    # ===================================
    
    # 9. Archive very old, low-importance, rarely-accessed memories
    archive_candidates = get_memories(
        age_days_min=180,
        importance_max=3,
        times_accessed_max=2
    )
    
    for memory in archive_candidates:
        archive_memory(memory)  # Keep, but lower retrieval priority
    
    # PHASE 6: SLEEP STATISTICS
    # =========================
    
    # 10. Log sleep statistics
    log_sleep_cycle(
        duration_minutes=calculate_sleep_duration(),
        memories_consolidated=len(recent_memories),
        reflections_generated=len(reflections),
        old_memories_replayed=len(old_memories),
        baseline_updated=is_significant_drift(drift),
        personality_drift=drift
    )
    
    print(f"ROOK woke up. Consolidated {len(reflections)} insights.")
    print(f"Baseline personality drift: {drift}")
```

---

## The Hebbian Plasticity Analog for ROOK

### In Neural Networks:
- Strengthen connections when neurons fire together
- Weaken connections when post-fires but pre-doesn't

### In ROOK's Memory System:

```python
def hebbian_memory_strengthening(memory_a, memory_b):
    """
    Strengthen connections between co-activated memories
    """
    # If two memories are retrieved together frequently,
    # strengthen their connection
    
    if memory_a.id in memory_b.metadata.get("co_retrieved_with", []):
        # Increase connection strength
        memory_a.metadata["connections"][memory_b.id] = \
            memory_a.metadata["connections"].get(memory_b.id, 0) + 0.1
        
        memory_b.metadata["connections"][memory_a.id] = \
            memory_b.metadata["connections"].get(memory_a.id, 0) + 0.1
    
    # If memory_a is retrieved but memory_b is not (despite being related),
    # weaken their connection
    elif are_related(memory_a, memory_b) and not recently_co_retrieved(memory_a, memory_b):
        memory_a.metadata["connections"][memory_b.id] = \
            max(0, memory_a.metadata["connections"].get(memory_b.id, 0) - 0.05)
```

### During Sleep:

```python
def apply_hebbian_plasticity_during_sleep(memories):
    """
    Strengthen frequently co-activated memory connections
    Weaken rarely co-activated connections
    """
    for memory in memories:
        # Get memories that were co-retrieved with this one
        co_retrieved = memory.metadata.get("co_retrieved_with", [])
        
        for other_id in co_retrieved:
            other_memory = get_memory(other_id)
            hebbian_memory_strengthening(memory, other_memory)
    
    # This creates "memory networks" where related memories
    # are strongly connected, forming coherent knowledge structures
```

---

## Continuous Personality Improvement Through Sleep

### The Mechanism:

1. **During Waking (Interactions)**:
   - ROOK gains new experiences
   - Personality state fluctuates (perturbations)
   - Memories accumulate
   - Some drift from baseline occurs

2. **During Sleep (Consolidation)**:
   - Recent experiences are reflected upon
   - Old memories are replayed (prevents forgetting)
   - Reflections create higher-level insights
   - Baseline personality slowly adjusts if drift is significant
   - Memory connections are strengthened/weakened (Hebbian)

3. **Result**:
   - Personality **evolves** based on accumulated experience
   - But **gradually** (not sudden shifts)
   - Old patterns are **preserved** (no catastrophic forgetting)
   - New insights are **integrated** into existing knowledge

### Example Timeline:

```
Day 1-7: ROOK investigates shell companies
  → Memories: 50 observations about shell company patterns
  → Personality state: High pattern_seeking, high document_focus
  → Drift from baseline: +0.15 in pattern_seeking

Night 7: Sleep consolidation
  → Reflection: "Shell companies use predictable naming patterns"
  → Replay: Old memories about offshore accounts (prevents forgetting)
  → Baseline update: pattern_seeking 0.70 → 0.72 (small shift)

Day 8-14: ROOK investigates wire transfers
  → Memories: 40 observations about temporal patterns
  → Personality state: Very high pattern_seeking
  → Drift from baseline: +0.20 in pattern_seeking

Night 14: Sleep consolidation
  → Reflection: "Temporal patterns appear in both shell companies and wire transfers"
  → Meta-reflection: "Patterns are the fingerprint of fraud"
  → Baseline update: pattern_seeking 0.72 → 0.75

Day 15-30: ROOK does casual conversations
  → Memories: 20 casual interactions
  → Personality state: Lower pattern_seeking, higher emotional_engagement
  → Drift from baseline: -0.10 in pattern_seeking

Night 30: Sleep consolidation
  → No significant drift (casual conversations are temporary perturbations)
  → Baseline remains: pattern_seeking 0.75 (stable)
  → Old investigation memories replayed (prevents forgetting)

Result after 30 days:
  → Baseline pattern_seeking: 0.70 → 0.75 (gradual increase)
  → Personality has evolved based on accumulated investigative experience
  → But old knowledge is preserved (no forgetting)
  → Casual conversations don't shift baseline (temporary states)
```

---

## Implementation Architecture

### Background Sleep Scheduler:

```python
class ROOKSleepScheduler:
    """
    Background process that triggers sleep consolidation
    """
    def __init__(self, rook_system):
        self.rook = rook_system
        self.last_sleep_time = now()
        self.importance_accumulator = 0
        
    def run(self):
        """
        Check sleep triggers periodically
        """
        while True:
            # Check every hour
            time.sleep(3600)
            
            if self.should_sleep():
                self.trigger_sleep()
    
    def should_sleep(self):
        """
        Check sleep triggers
        """
        # 1. Importance threshold
        recent_memories = self.rook.get_memories(age_hours_max=24)
        importance_sum = sum(m.importance for m in recent_memories)
        
        if importance_sum > 150:
            return True
        
        # 2. Time-based (every 24 hours)
        hours_since_sleep = (now() - self.last_sleep_time).hours
        if hours_since_sleep > 24:
            return True
        
        # 3. Personality drift
        drift = self.rook.calculate_personality_drift()
        if drift > 0.3:
            return True
        
        return False
    
    def trigger_sleep(self):
        """
        Initiate sleep consolidation
        """
        print(f"[{now()}] ROOK entering sleep consolidation...")
        
        sleep_stats = self.rook.sleep_consolidation()
        
        self.last_sleep_time = now()
        
        print(f"[{now()}] ROOK woke up.")
        print(f"  - Reflections generated: {sleep_stats['reflections_count']}")
        print(f"  - Old memories replayed: {sleep_stats['replay_count']}")
        print(f"  - Baseline updated: {sleep_stats['baseline_updated']}")
```

### Integration with Main System:

```python
class ROOKEnhanced:
    def __init__(self, ...):
        # ... existing initialization ...
        
        # Start sleep scheduler in background thread
        self.sleep_scheduler = ROOKSleepScheduler(self)
        self.sleep_thread = threading.Thread(
            target=self.sleep_scheduler.run,
            daemon=True
        )
        self.sleep_thread.start()
    
    def sleep_consolidation(self):
        """
        Execute sleep consolidation process
        """
        return rook_sleep_consolidation()  # From above
```

---

## Key Benefits of Sleep Consolidation

### 1. **Prevents Catastrophic Forgetting**
- Old memories are replayed during sleep
- Prevents new experiences from overwriting old knowledge
- ROOK maintains long-term memory

### 2. **Enables Continuous Personality Evolution**
- Baseline personality can shift gradually
- Based on accumulated, consolidated experience
- Not reactive to single events

### 3. **Creates Hierarchical Knowledge**
- Reflections build on observations
- Meta-reflections build on reflections
- Creates deep understanding, not just surface patterns

### 4. **Strengthens Memory Networks**
- Hebbian plasticity connects related memories
- Forms coherent knowledge structures
- Improves retrieval efficiency

### 5. **Maintains Stability-Plasticity Balance**
- Fast dynamics: States change within conversations
- Slow dynamics: Baseline evolves over weeks
- Sleep mediates between the two timescales

---

## Comparison: With vs. Without Sleep

### Without Sleep Consolidation:

```
Week 1: Investigate shell companies
  → Learns patterns
  → Baseline shifts to pattern_seeking = 0.85

Week 2: Casual conversations
  → Baseline shifts to pattern_seeking = 0.60 (FORGOT investigation mode)

Week 3: Investigate wire transfers
  → Baseline shifts to pattern_seeking = 0.90
  → But shell company patterns are FORGOTTEN (catastrophic forgetting)
```

**Result:** Reactive, unstable personality. Forgets old knowledge.

### With Sleep Consolidation:

```
Week 1: Investigate shell companies
  → Learns patterns
  → Sleep: Consolidates into reflections
  → Baseline shifts to pattern_seeking = 0.72 (gradual)

Week 2: Casual conversations
  → Temporary state change
  → Sleep: No baseline shift (not significant drift)
  → Baseline remains: pattern_seeking = 0.72 (stable)
  → Old investigation memories replayed (preserved)

Week 3: Investigate wire transfers
  → Learns new patterns
  → Sleep: Consolidates + replays shell company memories
  → Meta-reflection: "Patterns appear across multiple fraud types"
  → Baseline shifts to pattern_seeking = 0.78 (gradual)
  → Shell company knowledge PRESERVED and INTEGRATED
```

**Result:** Stable, evolving personality. Accumulates knowledge without forgetting.

---

## Next Steps for Implementation

1. **Build sleep scheduler** (background thread)
2. **Implement consolidation triggers** (importance, time, drift)
3. **Create reflection generation** (consolidation questions)
4. **Add spontaneous replay** (sample old memories)
5. **Implement baseline update** (slow drift calculation)
6. **Add Hebbian memory connections** (strengthen co-retrieved memories)
7. **Build meta-reflection generation** (reflections on reflections)
8. **Test sleep cycle** (verify no catastrophic forgetting)

---

## Conclusion

Sleep consolidation is the **missing piece** for ROOK's continuous personality improvement.

Without it:
- Catastrophic forgetting
- Reactive personality
- No long-term knowledge accumulation

With it:
- Preserved old knowledge
- Gradual personality evolution
- Hierarchical understanding
- Stable yet adaptive character

**ROOK doesn't just remember—he consolidates, reflects, and evolves.**

Just like humans do during sleep.

