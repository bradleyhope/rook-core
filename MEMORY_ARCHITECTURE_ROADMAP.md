# ROOK Memory Architecture Roadmap

## Current State (Phase 1 - Complete)

### What Works Now
- ✅ **Core formative memories** - 21 universal memories in `rook-memory` index
- ✅ **Personality traits** - Stored in `rook-personality-and-knowledge` index
- ✅ **Knowledge bases** - People (2,988), Tools (744), Interviews (69)
- ✅ **Memory retrieval** - ROOK can access all memories
- ✅ **Memory storage** - ROOK can create new memories
- ✅ **Hebbian strengthening** - Access counts increase when memories are retrieved

### Current Limitations
- ⚠️ **Shared memory space** - All users write to the same `rook-memory` index
- ⚠️ **No user isolation** - One user's memories affect everyone
- ⚠️ **No approval system** - All memories are automatically stored
- ⚠️ **No memory management** - Can't review/delete/promote memories

---

## Phase 2: Per-User Memory Spaces (Future)

### Goal
Each user gets their own memory space while preserving core universal memories.

### Architecture

**Three Memory Tiers:**

1. **Core Memories** (Universal - Read-only for users)
   - Index: `rook-memory-core`
   - Contains: Formative events, case studies, Bradley's training
   - Who can write: Only Bradley (you) via admin interface
   - Examples: 1MDB, Theranos, FTX, Wirecard, Enron learnings

2. **User Memories** (Per-user - Read/write for that user)
   - Index: `rook-memory-user-{user_id}`
   - Contains: Conversations, learnings from that specific user
   - Who can write: ROOK during conversations with that user
   - Isolated: User A can't see User B's memories

3. **Promoted Memories** (Universal - Curated)
   - Index: `rook-memory-promoted`
   - Contains: User memories you've approved as universal
   - Who can write: Only Bradley via approval system
   - Examples: Exceptional insights from user conversations

### Memory Retrieval Logic

When ROOK processes a query:
1. Retrieve from **Core Memories** (always)
2. Retrieve from **User Memories** (only that user's)
3. Retrieve from **Promoted Memories** (always)
4. Combine and rank by relevance

### Implementation Steps

**Step 1: Create Core Memory Index**
```python
# Migrate existing formative memories to rook-memory-core
# Mark them as protected/read-only
```

**Step 2: Implement User-Specific Indexes**
```python
# Create index per user: rook-memory-user-{user_id}
# Route memory storage based on user_id
```

**Step 3: Update Retrieval Logic**
```python
def get_relevant_memories(query, user_id):
    core = query_index("rook-memory-core", query)
    user = query_index(f"rook-memory-user-{user_id}", query)
    promoted = query_index("rook-memory-promoted", query)
    return combine_and_rank([core, user, promoted])
```

**Step 4: Build Admin Interface**
- View all user memories
- Promote memories to universal
- Edit/delete memories
- Manage core memories

---

## Phase 3: Memory Approval System (Future)

### Goal
You can review and approve which user memories become universal.

### Features

**1. Memory Review Dashboard**
- See all new memories created across all users
- Filter by importance, tags, user
- Preview memory content and context

**2. Approval Workflow**
```
User Memory → Review Queue → Approve/Reject → Promoted Memory
```

**3. Approval Actions**
- **Approve** - Promote to `rook-memory-promoted`
- **Reject** - Keep in user's private space only
- **Edit & Approve** - Modify before promoting
- **Delete** - Remove entirely

**4. Automatic Flagging**
- High importance scores (>8.0) auto-flagged for review
- Memories with specific tags (e.g., "fraud-pattern", "methodology")
- Memories that contradict core memories

---

## Phase 4: Advanced Memory Features (Future)

### Consolidation
- **Recent** → **Consolidated** → **Archived**
- Importance decay over time
- Merge similar memories
- Sleep consolidation process

### Memory Types
- **Formative** - Core identity-shaping events
- **Experience** - Conversations and interactions
- **Reflection** - ROOK's analysis of patterns
- **Case Study** - Detailed fraud investigations
- **Methodology** - Investigation techniques

### Memory Relationships
- Hebbian links between related memories
- Pattern recognition across memories
- Contradiction detection
- Memory chains (A led to B led to C)

### Memory Analytics
- Most accessed memories
- Memory growth over time
- User contribution statistics
- Memory quality metrics

---

## Implementation Priority

### Now (Phase 1 - Complete)
- ✅ Basic memory storage
- ✅ Memory retrieval
- ✅ Hebbian strengthening

### Next (Phase 2 - 2-3 weeks)
- [ ] Per-user memory indexes
- [ ] Core memory protection
- [ ] Updated retrieval logic
- [ ] User isolation

### Later (Phase 3 - 4-6 weeks)
- [ ] Admin dashboard
- [ ] Memory review interface
- [ ] Approval workflow
- [ ] Memory promotion system

### Future (Phase 4 - 2-3 months)
- [ ] Memory consolidation
- [ ] Advanced analytics
- [ ] Memory relationships
- [ ] Sleep processing

---

## Technical Considerations

### Pinecone Index Strategy

**Option A: One index per user** (Current plan)
- Pros: Complete isolation, easy to manage
- Cons: Many indexes (cost), harder to query across users

**Option B: Single index with user_id metadata**
- Pros: Easier to query, fewer indexes
- Cons: Requires careful filtering, potential leakage

**Recommendation**: Start with Option A (per-user indexes) for security, migrate to Option B if scale requires.

### Cost Implications
- Core memories: ~25 vectors (fixed)
- Promoted memories: ~100-500 vectors (grows slowly)
- User memories: ~10-50 vectors per active user

**Example**: 100 active users = 100 indexes × 30 vectors = 3,000 user vectors + 500 core/promoted = 3,500 total

### Security
- User memories are private by default
- Only you can access all memories
- API keys separate for admin vs public access
- Audit log for all memory promotions

---

## Current Status

**What's Live:**
- Terminal chat interface
- Memory storage (shared space)
- Memory retrieval
- Personality system

**What's Next:**
- Per-user memory isolation
- Core memory protection
- Admin interface for memory management

**Timeline:**
- Phase 2: 2-3 weeks
- Phase 3: 4-6 weeks
- Phase 4: 2-3 months

---

## Notes

- Current implementation stores all memories in shared `rook-memory` index
- This is fine for single-user testing
- Need to implement user isolation before public release
- Core memories (formative events) should be migrated to protected index
- Approval system can wait until after user isolation is working
