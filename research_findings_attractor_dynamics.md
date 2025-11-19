# Research Findings: Attractor Dynamics and Personality State Space Models

**Date:** November 9, 2025  
**Focus:** Mathematical frameworks for personality emergence and dynamics

---

## The Personality Dynamics (PersDyn) Model

**Source:** Sosnowska et al. (2019) - "A dynamic systems approach to personality"  
**Key Innovation:** Personality as a dynamic system with attractor dynamics

---

## Core Concept: Personality as a Dynamical System

### Three Model Parameters:

#### 1. **Baseline Personality** (The Attractor)
- The stable set point around which personality states fluctuate
- Acts as a **fixed point attractor** in state space
- Represents the "typical" or "average" personality state
- **This is what people mean when they describe someone's personality**

#### 2. **Personality Variability**
- The extent to which personality states fluctuate across time and situations
- Some people are highly variable (reactive to context)
- Others are stable (consistent across situations)
- Measured as the **standard deviation** of states around the baseline

#### 3. **Personality Attractor Force**
- The **swiftness** with which deviations from baseline are pulled back
- Strong attractor force = quick return to baseline (resilient)
- Weak attractor force = slow return to baseline (lingering effects)
- Mathematically: the **damping coefficient** in a spring-mass system

---

## Mathematical Framework

### State Space Representation:

```
Personality State at time t:
S(t) = [trait_1(t), trait_2(t), ..., trait_n(t)]

Example for Big Five:
S(t) = [Openness(t), Conscientiousness(t), Extraversion(t), Agreeableness(t), Neuroticism(t)]
```

### Attractor Dynamics Equation:

```
dS/dt = -α(S - B) + ε(t)

Where:
- S = current personality state
- B = baseline personality (the attractor)
- α = attractor force (return rate)
- ε(t) = random perturbations (situational influences)
```

This is a **first-order linear differential equation** that describes:
- States are pulled toward the baseline (B)
- The strength of the pull is proportional to distance from baseline
- Random perturbations push states away from baseline
- The system reaches equilibrium when pull = perturbations

### Discrete Time Version (for implementation):

```
S(t+1) = S(t) + α(B - S(t)) + ε(t)

Or equivalently:
S(t+1) = (1-α)S(t) + αB + ε(t)
```

This is a **weighted average** between:
- Current state: S(t)
- Baseline: B
- With weight α determining how quickly we move toward baseline

---

## Basin of Attraction

### Definition:
The **basin of attraction** is the set of all initial states that eventually converge to the attractor (baseline).

### For Personality:
- If you're pushed far from your baseline (e.g., extreme stress)
- You'll gradually return to your baseline over time
- The basin defines how far you can be pushed before you don't return
- **Outside the basin = personality change** (new baseline)

### Visual Representation:

```
Energy Landscape:

     High Energy
        ↑
        |     ╱╲           ╱╲
        |    ╱  ╲         ╱  ╲
        |   ╱    ╲       ╱    ╲
        |  ╱      ╲     ╱      ╲
        | ╱        ╲   ╱        ╲
        |╱          ╲ ╱          ╲
        |____________●____________╲___→ Personality State
                     ↑
                  Baseline
                 (Attractor)

The ball (●) rolls down to the valley (baseline)
The steepness of the valley = attractor force
The width of the valley = basin of attraction
```

---

## Homeostatic Regulation

### Biological Parallel:
- Body temperature has a set point (~37°C)
- Deviations trigger corrective mechanisms (sweating, shivering)
- System returns to set point automatically
- **Personality works the same way**

### Personality Homeostasis:
- Baseline = set point
- Situational influences = perturbations
- Attractor force = corrective mechanism
- Return to baseline = homeostatic regulation

### Key Insight from Stagner (1951):
> "Homeostasis is a universal principle. The maintenance of constant states occurs not only at the microscopic level but also at the level of personality as a unique individual phenomenon."

---

## Application to ROOK

### ROOK's Personality as a Dynamical System:

#### State Vector:
```python
S(t) = {
    "pattern_seeking": 0.9,      # How actively seeking patterns
    "document_focus": 0.95,       # Reliance on documents vs. people
    "skepticism": 0.85,           # Distrust of official narratives
    "persistence": 0.8,           # Willingness to pursue dead ends
    "emotional_detachment": 0.7   # Objectivity vs. emotional engagement
}
```

#### Baseline (Attractor):
```python
B = {
    "pattern_seeking": 0.85,
    "document_focus": 0.9,
    "skepticism": 0.8,
    "persistence": 0.75,
    "emotional_detachment": 0.65
}
```

This baseline **emerges** from formative events and accumulated experiences, not hardcoded.

#### Attractor Force:
```python
α = 0.3  # Moderate return rate
```

ROOK returns to his baseline personality over ~3-4 interactions after a perturbation.

#### Perturbations:
```python
ε(t) = situational_influence(current_query, context)

Examples:
- High-stakes investigation → increases pattern_seeking, decreases emotional_detachment
- Casual conversation → decreases document_focus, increases emotional_engagement
- Dead end → temporarily decreases persistence, but rebounds to baseline
```

---

## Dynamic Update Mechanism

### How ROOK's State Evolves:

```python
def update_personality_state(current_state, baseline, query_context):
    """
    Update ROOK's personality state based on current query
    """
    # 1. Calculate perturbation from query context
    perturbation = calculate_perturbation(query_context)
    # Example: investigation query increases pattern_seeking by +0.1
    
    # 2. Apply attractor dynamics
    alpha = 0.3  # attractor force
    next_state = {}
    
    for trait in current_state:
        # State pulled toward baseline, plus perturbation
        next_state[trait] = (
            (1 - alpha) * current_state[trait] +  # current state
            alpha * baseline[trait] +              # baseline pull
            perturbation.get(trait, 0)             # situational influence
        )
        
        # Clip to [0, 1] range
        next_state[trait] = max(0, min(1, next_state[trait]))
    
    return next_state


def calculate_perturbation(query_context):
    """
    Determine how the current query pushes ROOK away from baseline
    """
    perturbation = {}
    
    if query_context["type"] == "investigation":
        perturbation["pattern_seeking"] = +0.15
        perturbation["document_focus"] = +0.10
        perturbation["skepticism"] = +0.05
        
    elif query_context["type"] == "casual_chat":
        perturbation["emotional_detachment"] = -0.10
        perturbation["document_focus"] = -0.15
        
    elif query_context["type"] == "dead_end":
        perturbation["persistence"] = -0.20  # temporary discouragement
        # But attractor will pull it back up over time
    
    return perturbation
```

---

## Baseline Evolution (Slow Dynamics)

### The Key Insight:
- **States** change quickly (within a conversation)
- **Baseline** changes slowly (over weeks/months of experiences)
- This is the difference between:
  - **Mood** (state): "I'm frustrated right now"
  - **Temperament** (baseline): "I'm generally optimistic"

### Baseline Update Mechanism:

```python
def update_baseline(baseline, recent_states, consolidation_insights):
    """
    Slowly update baseline based on accumulated experiences
    This happens during "sleep" (consolidation)
    """
    # 1. Calculate average state over recent period
    avg_recent_state = calculate_average(recent_states)
    
    # 2. Calculate drift from baseline
    drift = {
        trait: avg_recent_state[trait] - baseline[trait]
        for trait in baseline
    }
    
    # 3. Check if drift is significant and consistent
    if is_significant_drift(drift, threshold=0.1, duration_days=30):
        # Baseline is shifting
        beta = 0.05  # very slow baseline update rate
        
        for trait in baseline:
            baseline[trait] += beta * drift[trait]
    
    # 4. Consolidation insights can also shift baseline
    for insight in consolidation_insights:
        if insight["type"] == "meta_reflection":
            # High-level insights about personality
            # Example: "I've become more skeptical after 10 failed investigations"
            baseline_adjustment = extract_baseline_adjustment(insight)
            baseline.update(baseline_adjustment)
    
    return baseline
```

### Example Baseline Evolution:

```
Initial Baseline (Day 0):
  pattern_seeking: 0.70
  
After 100 investigations where patterns were key (Day 90):
  Average state: 0.88
  Drift: +0.18
  
New Baseline (Day 90):
  pattern_seeking: 0.70 + (0.05 × 0.18 × 90/30) = 0.73
  
After 1 year (Day 365):
  pattern_seeking: 0.85 (gradually increased)
```

**This is personality development through experience.**

---

## Stability vs. Plasticity Trade-off

### The Challenge:
- **Stability**: Personality should be consistent (recognizable as ROOK)
- **Plasticity**: Personality should evolve with experience (not static)

### The Solution: Two-Timescale Dynamics

#### Fast Timescale (States):
- Update every interaction
- High variability
- Return to baseline within hours
- α = 0.3 (30% pull toward baseline per interaction)

#### Slow Timescale (Baseline):
- Update during consolidation (sleep)
- Low variability
- Requires weeks of consistent drift
- β = 0.05 (5% adjustment per consolidation cycle)

### Mathematical Relationship:

```
α >> β

Where:
α = state attractor force (fast)
β = baseline update rate (slow)

Typical values:
α ≈ 0.2 - 0.5  (states return to baseline in 2-5 interactions)
β ≈ 0.01 - 0.05  (baseline shifts ~1-5% per consolidation)
```

---

## Energy Landscape Perspective

### Conceptual Model:

Imagine personality as a ball rolling on a landscape:
- **Valleys** = attractors (stable personality states)
- **Hills** = unstable states (quickly left)
- **Ball position** = current personality state
- **Gravity** = attractor force pulling toward valleys

### For ROOK:

```
Deep valley at "pattern-obsessed investigator"
  → This is his baseline
  → Strong attractor force keeps him there
  → Perturbations push him up the sides of the valley
  → But he always rolls back down

Shallow valley at "casual conversationalist"
  → Weak attractor
  → Easy to push out of
  → Doesn't stay there long
```

### Landscape Evolution:

Over time, the landscape itself changes:
- Valleys deepen (stronger attractors) with repeated visits
- New valleys form (new personality modes) with new experiences
- Old valleys fill in (personality traits fade) if unused

**This is how personality evolves while maintaining stability.**

---

## Application to Memory-Based Personality

### The Connection:

In ROOK's system:
- **Memories** = experiences that shape the energy landscape
- **Reflections** = consolidation that deepens valleys
- **Baseline** = the deepest valley (most reinforced pattern)
- **States** = current position on the landscape

### How Memories Shape the Landscape:

```python
def shape_personality_landscape(memories, reflections):
    """
    Memories and reflections determine the energy landscape
    """
    landscape = {}
    
    # 1. Each memory contributes to the landscape
    for memory in memories:
        # Extract personality implications
        traits = extract_personality_traits(memory)
        # Example: "Found pattern in wire transfers" → pattern_seeking +0.05
        
        for trait, value in traits.items():
            landscape[trait] = landscape.get(trait, 0) + value
    
    # 2. Reflections have stronger influence (consolidated knowledge)
    for reflection in reflections:
        traits = extract_personality_traits(reflection)
        weight = reflection["importance"] / 10  # normalize
        
        for trait, value in traits.items():
            landscape[trait] = landscape.get(trait, 0) + (value * weight * 2)
            # Reflections count double
    
    # 3. Normalize to get baseline
    total_weight = sum(m["importance"] for m in memories + reflections)
    baseline = {
        trait: value / total_weight
        for trait, value in landscape.items()
    }
    
    return baseline
```

### The Emergent Property:

**ROOK's baseline personality emerges from the weighted sum of all his memories and reflections.**

- More pattern-finding memories → deeper valley at "pattern_seeking"
- More document-focused investigations → stronger "document_focus" attractor
- Reflections that synthesize these → reinforce the landscape

**No hardcoding. Pure emergence from experience.**

---

## Key Takeaways for ROOK Implementation

### 1. **Dual Dynamics**
- Fast: State changes within conversations (α = 0.3)
- Slow: Baseline evolution over weeks (β = 0.05)

### 2. **Attractor-Based Consistency**
- ROOK always returns to his baseline
- This ensures recognizable personality
- But baseline can shift with accumulated experience

### 3. **Memory-Driven Landscape**
- Memories and reflections shape the energy landscape
- More experiences in a domain → deeper attractor
- Personality emerges from the landscape topology

### 4. **Homeostatic Regulation**
- Perturbations are temporary
- System self-regulates back to baseline
- Maintains stability despite environmental variation

### 5. **Gradual Evolution**
- Personality can change, but slowly
- Requires consistent drift over time
- Prevents sudden, jarring personality shifts

---

## Next Steps

1. Implement state vector for ROOK's personality dimensions
2. Define baseline calculation from memory/reflection database
3. Create perturbation functions for different query types
4. Build attractor dynamics update mechanism
5. Design slow baseline evolution during consolidation (sleep)

This mathematical framework ensures ROOK has:
- **Consistency** (attractor dynamics)
- **Adaptability** (perturbations and slow baseline evolution)
- **Emergence** (baseline derived from memories, not hardcoded)

