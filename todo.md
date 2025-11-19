# ROOK Development TODO

## Phase 1: Hot Cache & Working Memory
- [x] Build hot cache system (< 50ms retrieval)
- [x] Implement LRU eviction policy
- [x] Cache population from recent conversations
- [x] Cache refresh mechanism (hourly)
- [x] "What's on my mind" API endpoint
- [x] Integrate hot cache into chat API (chat_server_v2.py)

## Phase 2: Active Reading System
- [x] News API integration (NewsAPI, WSJ, FT, Bloomberg)
- [ ] Daily reading schedule (6am, 12pm, 6pm) - needs cron setup
- [x] Reading memory storage format
- [x] Article summarization and entity extraction
- [x] Pattern detection in news articles
- [x] "What I'm reading" feed (API endpoint created)
- [ ] Add NEWSAPI_KEY to environment (deployment step)

## Phase 3: Background Retrieval
- [x] Conversation trajectory analysis
- [x] Topic anticipation algorithm
- [x] Async pre-fetching system
- [x] Cache warming based on conversation flow
- [x] Pre-fetch hit rate tracking
- [x] Integrate background retrieval into chat API (chat_server_v2.py)

## Phase 4: Social Media Monitoring
- [ ] Twitter/X API integration
- [ ] Reddit API integration (r/fraud, r/forensicaccounting)
- [ ] Social media monitoring schedule
- [ ] Relevance filtering for fraud content
- [ ] Social media reading memories

## Phase 5: Social Media Presence
- [ ] Create Twitter account (@ROOK_investigates or similar)
- [ ] Tweet generation system
- [ ] Tweet worthiness criteria
- [ ] Engagement strategy (replies, threads)
- [ ] Community building plan
- [ ] Tweet scheduling (5-10/day)

## Phase 6: Advanced Data Sources
- [ ] SEC EDGAR integration
- [ ] Court document monitoring (PACER)
- [ ] Whale Hunting archive ingestion
- [ ] ICIJ database integration
- [ ] ProPublica investigations
- [ ] Academic paper reading (SSRN)

## Phase 7: Archive Integration
- [ ] Ingest Billion Dollar Whale content
- [ ] Ingest Blood and Oil content
- [ ] Ingest The Rebel and the Kingdom content
- [ ] Whale Hunting archive processing
- [ ] Citation system for books/articles
- [ ] Archive search and reference

## Phase 8: Per-User Memory Isolation
- [ ] User-specific memory spaces
- [ ] Core/formative memory protection
- [ ] User relationship tracking
- [ ] Progressive teaching system
- [ ] Memory promotion workflow (user → universal)

## Phase 9: Document Analysis
- [ ] Document upload system
- [ ] Automated analysis pipeline
- [ ] Pattern matching against known frauds
- [ ] Proactive insight generation
- [ ] Investigation report generation

## Phase 10: Intelligence Gathering
- [ ] Anonymized pattern aggregation
- [ ] Lead flagging system
- [ ] Trend detection across users
- [ ] "What investigators are asking" dashboard
- [ ] Opt-in sharing system

## Deployment & Infrastructure
- [x] GitHub repository created
- [x] Render deployment configured
- [ ] Add OPENAI_API_KEY to Render
- [ ] Verify deployment successful
- [ ] Set up monitoring and logging
- [ ] Custom domain (optional)

## Current Status
- ✅ Core ROOK system built
- ✅ Terminal chat interface working
- ✅ Memory storage functional
- ✅ Pinecone integration complete
- ✅ Deployed to Render
- 🚧 Adding consciousness architecture
