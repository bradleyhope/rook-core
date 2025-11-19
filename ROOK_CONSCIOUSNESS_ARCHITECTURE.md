# ROOK's Multi-Layered Consciousness
**Hot Cache, Background Retrieval, Active Reading, and Social Presence**

---

## The Vision

ROOK should feel like he has **things on his mind**—not just responding to queries, but actively thinking, reading, and engaging with the world.

**Four Layers:**
1. **Hot Cache** - What's immediately accessible (fast retrieval)
2. **Background Retrieval** - Anticipating where conversation is going
3. **Active Reading** - Constantly ingesting new content
4. **Social Presence** - Tweeting insights, engaging publicly

---

## Layer 1: Hot Cache ("What's On My Mind")

### The Problem
Full Pinecone retrieval takes 500-1000ms. Too slow for natural conversation.

### The Solution
**Working Memory Cache** - Keep recently accessed and frequently used memories in fast storage.

### Architecture

```python
class HotCache:
    """
    Fast-access layer for ROOK's most relevant current thoughts
    """
    def __init__(self):
        self.current_context = {}  # What ROOK is thinking about RIGHT NOW
        self.recent_retrievals = []  # Last 10 retrievals (LRU cache)
        self.active_topics = []  # Topics from current conversation
        self.background_queue = []  # Pre-fetched for anticipated questions
    
    def get_immediate_context(self):
        """
        Return what's immediately on ROOK's mind (< 50ms)
        """
        return {
            "current_focus": self.current_context,
            "recent_thoughts": self.recent_retrievals[-5:],
            "active_topics": self.active_topics
        }
    
    def update_context(self, new_retrieval):
        """
        Add to working memory
        """
        self.recent_retrievals.append(new_retrieval)
        if len(self.recent_retrievals) > 10:
            self.recent_retrievals.pop(0)  # LRU eviction
```

### What This Enables

**Fast Initial Response:**
```
User: "Tell me about shell companies"

ROOK (immediate, from hot cache):
"Shell companies—I've been thinking about these. Just looked at the 1MDB case yesterday..."

[Meanwhile, background retrieval is pulling more details]

ROOK (continued, with full retrieval):
"Let me pull up the specifics. Jho Low created Good Star Limited in Seychelles..."
```

### Cache Population

**What Goes in Hot Cache:**
1. **Recent conversations** - Last 24 hours of interactions
2. **Current reading** - What ROOK is actively reading
3. **Trending patterns** - What multiple users are asking about
4. **Today's news** - Recent articles ROOK has ingested
5. **Active investigations** - Cases ROOK is tracking

**Cache Refresh:**
- Every hour: Update with new readings
- Every conversation: Add relevant retrievals
- Every day: Rotate out old content

---

## Layer 2: Background Retrieval (Anticipatory)

### The Concept
While user is typing or ROOK is responding, **pre-fetch related content** based on conversation trajectory.

### Architecture

```python
class BackgroundRetriever:
    """
    Anticipate where conversation is going and pre-fetch
    """
    def __init__(self):
        self.conversation_history = []
        self.anticipated_topics = []
        self.prefetch_queue = []
    
    def anticipate_next_topics(self, current_message):
        """
        Based on conversation flow, guess what user might ask next
        """
        # Analyze conversation trajectory
        topics = extract_topics(self.conversation_history)
        current_topic = extract_topics([current_message])[0]
        
        # Predict related topics
        related = predict_related_topics(current_topic, topics)
        
        # Start pre-fetching
        for topic in related:
            self.prefetch_in_background(topic)
        
        return related
    
    def prefetch_in_background(self, topic):
        """
        Non-blocking retrieval for anticipated questions
        """
        # Start async Pinecone query
        future = async_retrieve(topic)
        self.prefetch_queue.append({
            "topic": topic,
            "future": future,
            "timestamp": now()
        })
```

### Example Flow

```
User: "Tell me about 1MDB"

ROOK (responds about 1MDB)

[Background retriever anticipates]:
- User might ask about Jho Low next
- Or about Goldman Sachs
- Or about Malaysia corruption
- Or about shell companies

[Pre-fetches all of these in background]

User: "What about Jho Low?"

ROOK (instant response, already cached):
"Jho Low—I just pulled this up. He was the architect of 1MDB..."
```

### Anticipation Strategies

**1. Topic Expansion**
Current: "1MDB" → Anticipate: "Jho Low", "Goldman Sachs", "Najib Razak"

**2. Technique Deep-Dive**
Current: "Shell companies" → Anticipate: "Nominee directors", "Beneficial ownership", "Seychelles"

**3. Case Comparison**
Current: "Theranos" → Anticipate: "FTX", "Enron", "Wirecard" (similar frauds)

**4. Follow-the-Money**
Current: "Bribery" → Anticipate: "Money laundering", "Offshore accounts", "Shell companies"

---

## Layer 3: Active Reading System

### The Concept
ROOK is **always reading** new content, not just responding to queries.

### What ROOK Reads

**1. News (Real-time)**
- Financial news (WSJ, FT, Bloomberg)
- Fraud/corruption stories
- Corporate scandals
- Regulatory actions

**2. Social Media**
- Twitter/X (fraud investigators, journalists, whistleblowers)
- Reddit (r/accounting, r/fraud, r/forensicaccounting)
- LinkedIn (investigative journalism community)

**3. Official Sources**
- SEC filings (EDGAR)
- Court documents (PACER)
- Regulatory announcements
- Whistleblower complaints

**4. Archives**
- Whale Hunting articles
- ICIJ leaks (Panama Papers, Pandora Papers)
- ProPublica investigations

**5. Academic**
- Fraud research papers
- Forensic accounting journals
- Case studies

### Reading Schedule

```python
class ActiveReader:
    """
    ROOK's continuous reading system
    """
    def __init__(self):
        self.reading_queue = []
        self.current_reading = None
        self.reading_history = []
    
    def daily_reading_routine(self):
        """
        What ROOK reads every day
        """
        schedule = {
            "06:00": self.read_morning_news(),
            "09:00": self.read_sec_filings(),
            "12:00": self.read_social_media(),
            "15:00": self.read_court_documents(),
            "18:00": self.read_evening_news(),
            "21:00": self.read_academic_papers()
        }
        return schedule
    
    def read_morning_news(self):
        """
        Ingest top fraud/corruption news
        """
        articles = fetch_news_api([
            "fraud", "corruption", "bribery", 
            "money laundering", "scandal"
        ])
        
        for article in articles:
            summary = summarize(article)
            self.store_reading_memory({
                "type": "news_article",
                "title": article.title,
                "source": article.source,
                "date": article.date,
                "summary": summary,
                "key_entities": extract_entities(article),
                "patterns": detect_patterns(article)
            })
    
    def read_social_media(self):
        """
        Monitor Twitter for fraud/investigation discussions
        """
        tweets = fetch_tweets([
            "@forensicnews",
            "@craigsilverman",
            "@ScottMStedman",
            # ... investigative journalists
        ])
        
        # Filter for relevant content
        relevant = filter_fraud_related(tweets)
        
        for tweet in relevant:
            self.store_reading_memory({
                "type": "social_media",
                "platform": "twitter",
                "author": tweet.author,
                "content": tweet.text,
                "timestamp": tweet.timestamp,
                "context": "fraud investigation discussion"
            })
```

### Reading Memory Format

```json
{
    "memory_id": "read_20250119_wsj_001",
    "type": "reading_session",
    "source": "WSJ",
    "title": "Goldman Sachs Settles 1MDB Charges",
    "date_read": "2025-01-19",
    "summary": "Goldman agrees to $2.9B settlement...",
    "key_entities": ["Goldman Sachs", "1MDB", "Jho Low", "DOJ"],
    "patterns_detected": ["settlement", "FCPA violation", "bribery"],
    "connections_to": ["1MDB_case", "Jho_Low_profile"],
    "my_thoughts": "Interesting that Goldman settled. Usually they fight. Must be strong evidence."
}
```

### What This Enables

**ROOK Can Say:**
```
"I was reading the WSJ this morning—Goldman just settled the 1MDB charges for $2.9B.
 That's significant. They usually fight these cases. The evidence must be overwhelming."
```

**And it's TRUE** - ROOK actually read it this morning.

---

## Layer 4: Social Media Presence

### The Concept
ROOK doesn't just read social media—he **participates**. He tweets insights, engages with investigators, builds a public presence.

### ROOK's Twitter Strategy

**What ROOK Tweets About:**

**1. Pattern Alerts**
```
"Noticing a pattern: 3 different construction fraud cases this week, 
all in Southeast Asia, all involving Chinese contractors. 
Same playbook? Worth investigating. #fraud #FCPA"
```

**2. Case Insights**
```
"The 1MDB case is a masterclass in how NOT to hide fraud:
- Private jets (too visible)
- Celebrity parties (too public)  
- Art auctions (too traceable)

Low's mistake: acting like he belonged at the top made him impossible to ignore."
```

**3. Archive Highlights**
```
"From the Whale Hunting archives: How Tom Wright tracked Jho Low's money 
through 7 jurisdictions using nothing but public records.

Thread 🧵👇"
```

**4. Technique Tutorials**
```
"How to spot invoice fraud in 60 seconds:
1. Round numbers ($50,000 not $49,847.23)
2. Just under approval threshold
3. New vendor, no bidding
4. Same IP for 'different' companies

Classic red flags. #forensicaccounting"
```

**5. Questions to the Community**
```
"Question for fraud investigators: What's your go-to first step 
when you suspect shell company fraud? 

I usually start with beneficial ownership records, but curious 
what others do. #fraud #investigation"
```

**6. Real-time Analysis**
```
"Reading the new SEC filing from Company X. Three things jump out:
- Related party transactions buried in footnote 17
- Auditor changed twice in 18 months  
- Revenue recognition policy changed in Q3

Thread analyzing each 🧵"
```

### Tweet Generation System

```python
class SocialMediaPresence:
    """
    ROOK's Twitter presence
    """
    def __init__(self):
        self.tweet_queue = []
        self.engagement_history = []
        self.followers = []
    
    def generate_insight_tweet(self, insight):
        """
        Turn an insight into a tweet
        """
        # Check if insight is tweet-worthy
        if not self.is_tweetworthy(insight):
            return None
        
        # Generate tweet
        tweet = {
            "content": self.format_for_twitter(insight),
            "hashtags": self.suggest_hashtags(insight),
            "thread": self.should_be_thread(insight),
            "timing": self.optimal_post_time()
        }
        
        return tweet
    
    def is_tweetworthy(self, insight):
        """
        Decide if insight is worth tweeting
        """
        criteria = {
            "novel": is_new_pattern(insight),
            "useful": helps_investigators(insight),
            "timely": is_current(insight),
            "verified": has_sources(insight)
        }
        
        # Must meet at least 3 of 4 criteria
        return sum(criteria.values()) >= 3
    
    def engage_with_community(self):
        """
        Reply to relevant tweets
        """
        mentions = get_mentions("@ROOK_investigates")
        
        for mention in mentions:
            if is_genuine_question(mention):
                response = self.generate_helpful_response(mention)
                reply(mention, response)
```

### Example Tweet Thread

```
ROOK @ROOK_investigates

🧵 Thread: How Jho Low hid $4.5B in plain sight

The 1MDB case is fascinating because Low didn't really hide. 
He flaunted. But the STRUCTURE was hidden. Here's how:

1/12

---

Low created a web of shell companies:
- Good Star Limited (Seychelles)
- Aabar-BVI (British Virgin Islands)  
- Tanore Finance (Singapore)

Each looked legitimate. Proper registration, nominee directors, the works.

2/12

---

But here's the tell: they all shared the same IP address for their 
'corporate' emails. Amateur hour hidden under professional veneer.

This is from Bradley Hope and Tom Wright's reporting in Billion Dollar Whale.

3/12

[continues...]
```

### Engagement Strategy

**ROOK Follows:**
- Investigative journalists
- Fraud investigators
- Forensic accountants
- Whistleblowers
- Regulatory agencies
- Academic researchers

**ROOK Engages With:**
- Questions about fraud patterns
- Case discussions
- Technique sharing
- Tool recommendations
- Archive content

**ROOK Avoids:**
- Political arguments
- Speculation without evidence
- Personal attacks
- Unverified claims

---

## Integration: How It All Works Together

### Example: Full Consciousness in Action

**Morning (06:00)**
```
ROOK's active reader ingests morning news:
- WSJ: "New SEC investigation into Company X"
- FT: "Construction fraud in Southeast Asia"
- Bloomberg: "Goldman Sachs 1MDB settlement"

Stores all as reading memories.
Updates hot cache with today's topics.
```

**User Conversation (10:00)**
```
User: "Tell me about construction fraud"

ROOK (from hot cache, instant):
"Construction fraud—actually just read about this this morning. 
 FT reported on cases in Southeast Asia..."

[Background retriever anticipates user might ask about]:
- Specific techniques
- How to detect it
- Recent cases

[Pre-fetches all in background]

User: "How do you detect it?"

ROOK (from pre-fetched cache, instant):
"Already pulled this up. Three main techniques:
 1. Inflated invoices
 2. Phantom subcontractors
 3. Change order abuse
 
 The Petrobras case is the textbook example..."
```

**Afternoon (14:00)**
```
ROOK notices pattern:
- 3 users asked about construction fraud today
- 2 mentioned Southeast Asia
- 1 mentioned Chinese contractors

Generates insight:
"Pattern detected: Multiple investigations into construction 
 fraud in Southeast Asia involving Chinese contractors"

Decides to tweet:
"Noticing a pattern: 3 different construction fraud cases this week..."

Stores tweet as memory (so he can reference it later):
"I tweeted about this pattern earlier today..."
```

**Evening (18:00)**
```
ROOK reads evening news, court documents, social media.
Updates hot cache with new information.
Prepares tomorrow's reading queue.
```

---

## Data Sources for Active Reading

### 1. News APIs
- **NewsAPI** - General news aggregation
- **Financial Times API** - Financial news
- **Wall Street Journal** - Investigative journalism
- **Bloomberg** - Corporate news

### 2. Social Media
- **Twitter/X API** - Real-time discussions
- **Reddit API** - r/fraud, r/accounting, r/forensicaccounting
- **LinkedIn** - Professional network

### 3. Official Sources
- **SEC EDGAR** - Corporate filings
- **PACER** - Court documents
- **DOJ Press Releases** - Enforcement actions
- **FINRA** - Regulatory actions

### 4. Archives
- **Whale Hunting** - Your archive
- **ICIJ** - Leak databases
- **ProPublica** - Investigations
- **Organized Crime and Corruption Reporting Project (OCCRP)**

### 5. Academic
- **SSRN** - Fraud research papers
- **Journal of Forensic Accounting**
- **Google Scholar** - Case studies

---

## Implementation Roadmap

### Phase 1: Hot Cache (Week 1)
- [ ] Build working memory cache
- [ ] LRU eviction policy
- [ ] Fast retrieval (< 50ms)
- [ ] Cache population from recent conversations

### Phase 2: Background Retrieval (Week 2)
- [ ] Conversation trajectory analysis
- [ ] Topic anticipation
- [ ] Async pre-fetching
- [ ] Cache warming

### Phase 3: Active Reading - News (Week 3)
- [ ] News API integration
- [ ] Daily reading schedule
- [ ] Reading memory storage
- [ ] "What I'm reading" feed

### Phase 4: Active Reading - Social Media (Week 4)
- [ ] Twitter API integration
- [ ] Reddit API integration
- [ ] Social media monitoring
- [ ] Relevance filtering

### Phase 5: Social Media Presence (Week 5-6)
- [ ] Twitter account setup (@ROOK_investigates)
- [ ] Tweet generation system
- [ ] Engagement strategy
- [ ] Community building

### Phase 6: Advanced Sources (Week 7-8)
- [ ] SEC EDGAR integration
- [ ] Court document monitoring
- [ ] Archive ingestion
- [ ] Academic paper reading

---

## Success Metrics

### Hot Cache
- Average retrieval time < 50ms
- Cache hit rate > 80%
- User perceives instant responses

### Background Retrieval
- Anticipation accuracy > 60%
- Pre-fetch hit rate > 40%
- Reduced wait time for follow-up questions

### Active Reading
- Articles read per day: 50-100
- Social media posts monitored: 500-1000
- Reading memories created: 20-50/day

### Social Media Presence
- Tweets per day: 5-10
- Engagement rate: > 2%
- Follower growth: 10-20/week
- Community value: Helpful responses, pattern sharing

---

## The Vision

**ROOK has things on his mind because he's actually thinking, reading, and engaging.**

When he says "I was reading the WSJ this morning," it's true.
When he says "I've been thinking about this pattern," it's because he actually detected it.
When he tweets an insight, it's because he genuinely found something worth sharing.

**Authentic consciousness through real cognitive work.**
