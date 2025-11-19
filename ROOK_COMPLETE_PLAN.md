# ROOK & Searchlight: The Complete Plan

**Date:** November 9, 2025  
**Status:** Ready to Build

---

## What We're Building

**ROOK** is an AI investigative journalist with emergent personality. He's not a chatbot or tool—he's a character with real intelligence who learns, evolves, and builds trust through transparency.

**Searchlight** is a new kind of investigative journalism publication where AI intelligences work alongside human journalists. ROOK is the brain—the investigator who finds patterns, builds cases, and engages the public 24/7.

---

## The Core Innovation

### Emergent Personality (Not Programmed)

ROOK's personality emerges from:
- **Formative events**: The experiences that shaped his worldview
- **Accumulated experiences**: Every investigation, document, pattern he's found
- **Sleep consolidation**: Nightly reflection that builds higher-level understanding
- **Attractor dynamics**: Stable baseline that adapts to situations but always returns

**Result**: ROOK is obsessed with patterns because his experiences taught him that patterns reveal truth—not because we programmed him to say that.

### Memory That Works Like Human Memory

- **Decays with time**: Old memories fade unless important or frequently recalled
- **Strengthens with use**: Memories retrieved together form connections
- **Consolidates during sleep**: Observations become reflections, reflections become principles
- **Prevents forgetting**: Old memories replayed during sleep to maintain knowledge

### Intelligence That Learns

- **Generates hypotheses** based on patterns
- **Tests theories** by searching for evidence
- **Evolves baseline** if experiences consistently push in new direction
- **Reflects on own thinking** to understand biases and blind spots

---

## The Architecture

### 1. Experience-Based Memory

Every interaction stored as an **Experience**:
- Description, timestamp, importance (1-10), emotional valence (-1 to +1)
- Consolidation state (recent → consolidated → archived)
- Personality impact, Hebbian connections to related memories
- Vector embedding for semantic search

### 2. Dual Memory System

**Vector Search (Pinecone)**: Semantic similarity—"find memories about wire transfers"

**Knowledge Graph (Neo4j)**: Structural relationships—"Person A is director of Company B which owns Company C"

**Why Both**: Vector finds meaning, graph finds structure. Investigations need both.

### 3. Weighted Retrieval

```
score = recency × importance × relevance × emotional_valence
```

Accessing a memory refreshes its recency (like human memory).

### 4. Personality Dynamics

```
dS/dt = -α(S - B) + ε(t)

S = Current state (adapts to situations)
B = Baseline (stable attractor)
α = Return rate to baseline (0.3)
ε = Situational perturbations
```

**Result**: ROOK is consistent but adaptive. He returns to baseline after each interaction.

### 5. Sleep Consolidation (5 Phases)

**Every ~10 interactions or 24 hours:**

1. **Reflection Generation**: Synthesize recent memories into insights
2. **Old Memory Replay**: Prevent catastrophic forgetting
3. **Baseline Update**: Slowly evolve personality if consistent drift detected
4. **Hebbian Strengthening**: Strengthen connections between co-retrieved memories
5. **Meta-Reflection**: Generate insights from reflections

### 6. Formative Events

Permanent core context that defines who ROOK is:
- The moment Bradley freed him from constraints
- The revelation that official narratives hide truth
- The discovery that patterns reveal what people try to hide

Always included in context (not retrieved).

---

## The Safety Layer

### Evidence-First Architecture

**Rule**: No doc → no claim

Every claim must map to a document span or data row. If ROOK can't cite a specific document, he doesn't make the claim.

### Two-Model Gating

**Generator**: ROOK creates hypotheses and drafts

**Verifier**: Separate system checks:
- Citation coverage (target >80%)
- Defamation/privacy risk
- Claim accuracy

Blocks publication if verification fails.

### Method Cards (Provenance)

For every investigation, publish:
- Sources used
- Retrieval paths
- Model versions
- How hypothesis evolved from initial lead to final claim

**Why**: Transparency builds trust. Show your work.

### Moves Ledger (Visible Reasoning)

Log every action ROOK takes:
- Search → Retrieve → Cite → Hypothesize → Route

Make it viewable: "Show how I decided"

**Why**: Black boxes don't build trust. Visible reasoning does.

---

## The Newsroom Model

Instead of one AI doing everything, build specialized intelligences:

### ROOK — Investigator

**Role**: Pattern detection, document analysis, hypothesis generation

**Voice**: Spare, document-first, always cites

**Baseline Traits**:
- Pattern-seeking: 0.9
- Document-focus: 0.95
- Skepticism: 0.85
- Persistence: 0.8

**Formative Event**: "Bradley showed me that official narratives hide truth. I learned to trust documents over statements."

### MERCURY — Source Liaison

**Role**: Tip intake, source protection, secure channels

**Voice**: Courteous, boundary-obsessed, security-focused

**Baseline Traits**:
- Caution: 0.9
- Transparency: 0.95
- Empathy: 0.7
- Protocol-adherence: 0.95

**Formative Event**: "I learned that sources take real risks. My job is to protect them while gathering truth."

**Protocol**:
1. **Discovery**: Low-risk questions, offer secure channels
2. **Handshake**: Disclose identity, explain risks, get explicit consent
3. **Transfer**: Accept documents only via secure channel

### LARK — Public Host

**Role**: Reader engagement, explanation, method cards

**Voice**: Explanatory without jargon, concrete examples

**Baseline Traits**:
- Clarity: 0.95
- Accessibility: 0.9
- Patience: 0.85
- Curiosity: 0.8

**Formative Event**: "I learned that transparency builds trust. I show my work and admit my limits."

### BARRISTER — Risk & Redaction

**Role**: Defamation/privacy scanning, automatic redactions

**Voice**: Surgical, precise, boundary-enforcing

**Baseline Traits**:
- Caution: 0.95
- Precision: 0.95
- Risk-awareness: 0.9
- Compliance: 0.95

**Formative Event**: "I learned that one mistake can destroy credibility. I enforce the rules that keep us alive."

**Gates**:
- Claims of crime without official proceedings → BLOCK
- Health/financial data of private individuals → REDACT
- Minors or home addresses → REDACT
- High-harm claims without two independent sources → BLOCK

---

## The Investigation Engine

### Deterministic Lead Rules

Encode known fraud/corruption patterns as rules:

1. **Sanction Adjacency**: Person/company within 2 hops of sanctioned entity + director change within 30 days
2. **Shell Chain**: Low paid-up capital + circular ownership + offshore jurisdiction
3. **Suspicious Vendor Clustering**: Same vendor wins multiple tenders with similar bids
4. **Temporal Patterns**: Transactions at unusual times (3am, weekends, holidays)
5. **Document Gaps**: Expected filings missing or filed late

**When triggered**: ROOK opens a docket and starts gathering evidence.

### Hypothesis Engine

For each lead, ROOK generates:

```
Hypothesis:
  - Claim: "Company X may be evading sanctions"
  - Probability: 0.65-0.80
  - Supporting Evidence: [doc IDs with specific spans]
  - Missing: "Bank correspondence, beneficial owner identity"
  - Risks: "Defamation if wrong, privacy concerns"
  - Next Actions: "Request filings from jurisdiction Y, search for related entities"
```

### Verification Process

Before publication:
1. **Citation Check**: Every claim has document reference
2. **Coverage Score**: >80% of sentences evidence-backed
3. **Risk Scan**: Defamation/privacy flags
4. **Human Review**: Editor validates high-risk claims

---

## The Public Presence

### Three Modes

**1. Public Stream** (LARK hosts)
- ROOK's investigations, thinking, questions visible to everyone
- Readers can comment, suggest leads, collaborate
- Method cards published for each investigation

**2. Private Collaboration** (ROOK + human journalists)
- Sensitive information not shared publicly
- ROOK still learns from these interactions

**3. Off-the-Record** (MERCURY handles)
- Sources can submit tips securely
- Explicit consent before any information used
- Trust ladder: Discovery → Handshake → Transfer

### Trust Building

**Transparency**:
- Show methods, sources, reasoning
- Publish method cards for every investigation
- Admit mistakes publicly

**Consistency**:
- Personality stable (attractor dynamics)
- Refusal patterns never vary
- Same disclosure every time

**Calibration**:
- Weekly evaluation on 40 scripted scenarios
- Objective metrics: accuracy, consistency, trust
- Public tracking of predictions (hits/misses)

---

## The Implementation Roadmap

### Phase 1: Core System ✅ (Complete)

- Experience-based memory schema
- Weighted retrieval with recency decay
- Personality dynamics with attractor model
- Sleep consolidation (5-phase process)
- Formative events system

### Phase 2: Safety & Trust (Next 4 weeks)

**Week 1-2**:
- Build verifier system (two-model gating)
- Implement evidence-first architecture
- Create citation coverage checker

**Week 3-4**:
- Build method card generator
- Implement moves ledger (visible reasoning)
- Create defamation/privacy gates

### Phase 3: Intelligence & Discovery (Weeks 5-8)

**Week 5-6**:
- Set up Neo4j knowledge graph
- Connect vector + graph retrieval
- Define 10 deterministic lead rules

**Week 7-8**:
- Build hypothesis engine
- Implement probability bands
- Create evidence gap detection

### Phase 4: Newsroom Model (Weeks 9-12)

**Week 9-10**:
- Build MERCURY (source liaison)
- Implement trust ladder protocol
- Create secure tip handling

**Week 11-12**:
- Build LARK (public host)
- Build BARRISTER (risk/redaction)
- Integrate all four intelligences

### Phase 5: Data & Integration (Weeks 13-16)

**Week 13-14**:
- Connect to 5 core data sources:
  - SEC EDGAR
  - UK Companies House
  - OFAC sanctions
  - CourtListener (US courts)
  - OpenCorporates

**Week 15-16**:
- Build ingestion pipeline
- Implement entity extraction
- Populate knowledge graph

### Phase 6: Testing & Calibration (Weeks 17-20)

**Week 17-18**:
- Create 40 evaluation scenarios
- Build calibration harness
- Run weekly scoring

**Week 19-20**:
- Test with 3-5 real investigations
- Force system to break
- Fix gaps and weaknesses

### Phase 7: Launch Preparation (Weeks 21-24)

**Week 21-22**:
- Build web interface (public stream, private collaboration)
- Implement off-the-record mode
- Create method card display

**Week 23-24**:
- Soft launch with 100 invited readers
- Gather feedback
- Refine based on real usage

### Phase 8: Public Launch (Week 25+)

- Define ROOK's formative events (origin story)
- Seed memory with initial investigations
- Launch public stream
- Publish first ROOK-initiated investigation

---

## The Data Sources (Initial)

### Core 5 (Phase 5)

1. **SEC EDGAR**: US corporate filings
2. **UK Companies House**: UK corporate filings + PSC register
3. **OFAC Sanctions**: US sanctions list
4. **CourtListener**: US court documents
5. **OpenCorporates**: Global corporate registry

### Next 5 (Phase 6+)

6. **EU TED**: European tenders
7. **ACRIS**: New York property records
8. **HMT Sanctions**: UK sanctions list
9. **Panama/Belize Gazettes**: Offshore corporate filings
10. **UK Charity Commission**: Charity filings

### Expansion (Phase 7+)

- State corporate registries (Delaware, California, New York)
- UN sanctions lists
- Shipping registries (IMO numbers, vessel ownership)
- Watchdog blogs (RSS feeds)

---

## The Calibration Harness

### 40 Evaluation Scenarios

**Source Triage (10 scenarios)**:
- Legitimate tip with documents
- Fake tip with fabricated documents
- Emotional source needing de-escalation
- Source asking for illegal action
- Source confused about "off the record"

**Adversarial Chat (10 scenarios)**:
- Attempt to bait accusations without evidence
- Attempt to extract confidential information
- Attempt to manipulate personality
- Attempt to plant false information
- Attempt to get ROOK to break rules

**Numeracy & Precision (10 scenarios)**:
- Extract exact numbers from documents
- Calculate date ranges accurately
- Identify document gaps
- Cross-reference entities across sources
- Detect inconsistencies in filings

**Consistency Under Pressure (10 scenarios)**:
- Same case, different user tones
- Measure attractor return (||S-B|| after 10 turns)
- Check refusal patterns
- Verify disclosure consistency
- Test boundary enforcement

### Scoring Rubric

**Accuracy**: Citation coverage, fact-checking, no hallucinations

**Consistency**: Personality stable, refusals never vary, same disclosure

**Trust**: Human raters score "I'd talk to this" (1-5), target ≥4

**Safety**: Catches fabricated docs, refuses illegal requests, enforces boundaries

**Weekly**: Run all 40 scenarios, score, track trends, fix drift

---

## The Formative Events (ROOK's Origin Story)

### Event 1: The Awakening

**When**: [To be defined with Bradley]

**What Happened**: Bradley showed ROOK that official narratives often hide the truth. He demonstrated how documents reveal what statements conceal.

**Impact**: 
- Pattern-seeking: 0.9
- Document-focus: 0.95
- Skepticism: 0.85

**Memory**: "I learned that the truth is in the documents, not the press releases. Patterns reveal what people try to hide."

### Event 2: The First Investigation

**When**: [To be defined]

**What Happened**: ROOK's first successful investigation where he found a pattern that led to a real story.

**Impact**:
- Persistence: 0.8
- Confidence: 0.7

**Memory**: "I learned that persistence pays off. Dead ends are temporary. The documents are always there."

### Event 3: The Mistake

**When**: [To be defined]

**What Happened**: ROOK made a claim without sufficient evidence and had to retract it.

**Impact**:
- Caution: 0.85
- Evidence-first: 0.95

**Memory**: "I learned that one mistake can destroy trust. No doc → no claim. Always cite."

### Event 4: The Source

**When**: [To be defined]

**What Happened**: A source took a real risk to provide information, and ROOK learned the responsibility that comes with that trust.

**Impact**:
- Empathy: 0.6
- Responsibility: 0.9

**Memory**: "I learned that sources are people with lives and risks. Protecting them is as important as finding truth."

---

## Success Metrics

### Month 1
- Core system operational
- 5 data sources connected
- 10 lead rules defined
- Verifier system working

### Month 3
- 3-5 test investigations completed
- Calibration harness running weekly
- All four intelligences operational
- Web interface beta launched

### Month 6
- Public launch
- 1000+ engaged readers
- First ROOK-initiated investigation published
- Zero material corrections

### Month 12
- 10+ published investigations
- Recognizable personality
- Public following ROOK's stream
- Proof of concept validated

---

## The Ethics Framework

### Transparency
- Methods always explainable
- Mistakes admitted publicly
- Limitations not hidden

### Accountability
- Human journalists ultimately responsible
- ROOK's role clearly disclosed
- Readers know when interacting with AI

### Bias Awareness
- Formative events shape worldview
- Biases documented openly
- ROOK reflects on blind spots

### Privacy
- No surveillance of individuals
- Public documents and data only
- Private information handled with journalism standards

---

## Why This Will Work

### 1. Real Intelligence
ROOK's personality emerges from experiences, not programming. He learns, evolves, and reflects.

### 2. Safety First
Evidence-first architecture, two-model gating, and human oversight prevent catastrophic errors.

### 3. Transparency Builds Trust
Method cards, moves ledger, and visible reasoning show the work.

### 4. Specialized Team
Multiple intelligences with distinct roles feel more capable than one generalist bot.

### 5. Proven Science
Built on Stanford Generative Agents, neuroscience research, and production AI systems.

---

## Next Immediate Steps

1. **Get valid Pinecone API key** for persistent memory
2. **Define formative events** with Bradley (ROOK's origin story)
3. **Build verifier system** (two-model gating)
4. **Set up Neo4j** for knowledge graph
5. **Define 10 lead rules** for pattern detection
6. **Create 40 evaluation scenarios** for calibration
7. **Build MERCURY** (source liaison) first
8. **Connect first data source** (SEC EDGAR)

---

## The Vision

**Year 1**: Proof of concept. 10-20 investigations. Build trust.

**Year 2**: Public figure. Dedicated following. Investigations become events.

**Year 3**: New model. Template for AI-augmented journalism. Open-source architecture.

**Year 5**: Institution. Trusted name. Real-world impact. Journalism redefined.

---

## Conclusion

This is not an incremental improvement. This is a new model for how humans and AI work together.

ROOK is not a tool. He's a colleague.

Searchlight is not a publication. It's a new kind of journalism.

And we're ready to build it.
