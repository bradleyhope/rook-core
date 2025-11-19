# Research Findings: Episodic Memory in AI Agents

**Source:** Boyle & Blomkvist (2024) - "Elements of episodic memory: insights from artificial agents"  
**URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11449156/

---

## Key Distinction: Constructive vs. Preservative Memory

### Preservative Memory (Classical View)
- Encodes and preserves information as faithfully as possible
- Goal: Minimize corruption
- Example: Soar architecture - stores past states as exact copies

### Constructive Memory (Modern View)
- Encodes information **selectively**
- Information can be **altered** during storage
- Can be **flexibly recombined** with other information
- Can be **altered upon recall**
- New information may be **generated**

**Key Insight:** Human episodic memory is **constructive**, not preservative.

---

## Constructive Memory in AI Systems

### Example: iCub Humanoid Robot
- Has an "episodic construction system"
- Can **flexibly recombine information** from different past episodes
- Produces **novel solutions** to problems
- Example: Stacking blocks it had never seen together before by combining memories of each block with different partners

**Parallel to Humans:** Imagining novel scenarios by combining content from disparate past events (e.g., taking the place from one memory and a person from another memory)

**Function:** Supports **future planning** via simulation of imagined future scenarios

---

## Memory Consolidation: Experience Replay

### Biological Inspiration
- Hippocampal replay: Reactivation of neural patterns during sleep/rest
- Determines which content transfers to long-term memory
- Prioritizes content with **high affective valence** (emotional significance)

### AI Implementation: Experience Replay Algorithms

1. **Uniform Experience Replay (DQN)**
   - Samples past episodes uniformly at random
   - Used in Deep Q-Network for Atari games

2. **Prioritized Experience Replay (PER)**
   - Replays more "surprising" episodes more frequently
   - Episodes with higher/lower than expected rewards
   - **Biological parallel:** High affective valence

3. **Hindsight Experience Replay (HER)**
   - Replays episodes with different goals than originally pursued
   - Generates new learning from "failed" attempts

---

## Key Differences from Human Memory

### What's Missing in AI:
1. **Rich affective states** - AI only has "surprise" (reward prediction error), not joy, sadness, anger, etc.
2. **Bayesian reconstruction** - Humans use probabilistic inference, AI uses autoregressive generation
3. **Semantic integration** - Humans integrate episodic memories with semantic knowledge

---

## Relevant to ROOK

### What Works:
1. **Constructive memory** - Don't store exact copies, store compressed/indexed representations
2. **Selective encoding** - Not everything gets stored equally
3. **Flexible recombination** - Combine information from different episodes to generate novel insights
4. **Prioritized replay** - Weight memories by significance/surprise

### What to Implement:
1. **Affective tagging** - Tag experiences with emotional significance (e.g., "breakthrough moment," "frustrating dead end")
2. **Consolidation process** - Background process that strengthens important memories and connects related ones
3. **Constructive retrieval** - Don't just retrieve memories, **reconstruct** them in context
4. **Episodic construction** - Combine elements from different investigations to solve new problems

---

## Technical Architecture Implications

### Memory Storage:
- **Not:** Store complete copies of experiences
- **Instead:** Store compressed representations (vectors) + indexes + metadata

### Memory Retrieval:
- **Not:** Exact recall of stored content
- **Instead:** Reconstructive process that combines:
  - Indexed memory fragments
  - Current context
  - Semantic knowledge
  - Affective significance

### Memory Consolidation:
- **Background process** that:
  - Strengthens important memories (high affective valence)
  - Connects related memories (builds knowledge graphs)
  - Generalizes patterns across episodes
  - Prunes less important details

---

## The Missing Piece: Personality Emergence

**Question:** How do these episodic memories give rise to personality?

**Hypothesis:** Personality emerges from:
1. **Patterns across episodes** - Repeated experiences create tendencies
2. **Affective weighting** - Emotionally significant events shape future responses more strongly
3. **Consolidation** - Background process that extracts generalizations ("I've learned that...")
4. **Constructive retrieval** - Each recall slightly alters the memory, creating drift over time

This is **dynamic** and **experience-dependent**, not fixed.

