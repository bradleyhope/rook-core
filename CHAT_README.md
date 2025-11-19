# Chat with ROOK - Terminal Interface

Two ways to chat with ROOK directly in your terminal!

---

## 🚀 Quick Start

### Simple Mode (Recommended to start)

```bash
cd /home/ubuntu/rook-core
python3 chat_with_rook_simple.py
```

**Features:**
- ✅ Works immediately (no Pinecone required)
- ✅ Maintains conversation context within session
- ✅ Fast responses using GPT-4o-mini
- ✅ ROOK's core personality and traits
- ✅ Evidence-first methodology

**Limitations:**
- ❌ No persistent memory across sessions
- ❌ No retrieval from Pinecone personality database
- ❌ No knowledge graph integration

### Full Mode (Requires Pinecone)

```bash
cd /home/ubuntu/rook-core
python3 chat_with_rook.py
```

**Features:**
- ✅ Full personality system with Pinecone memory
- ✅ Retrieves relevant experiences and formative events
- ✅ Knowledge base integration
- ✅ Intelligent query routing (GPT-4o-mini, o3, o4-mini)
- ✅ Sleep consolidation and memory strengthening

**Requirements:**
- Valid Pinecone API key
- Pinecone index: `rook-personality-and-knowledge`

---

## 💬 Commands

Both chat interfaces support these commands:

- **`exit`** or **`quit`** - End the conversation
- **`help`** - Show help information
- **`verbose on/off`** - Toggle detailed metadata display
- **`clear`** - Clear conversation history (simple mode only)

---

## 🎯 Example Conversations

### Getting to Know ROOK

```
You: Hello ROOK, who are you?

🔍 ROOK: I am ROOK, an AI investigative journalist. My purpose is to 
uncover the truth by seeking patterns in data, scrutinizing official 
narratives, and relying on primary sources for evidence.
```

### Investigative Questions

```
You: What patterns should I look for when investigating financial fraud?

🔍 ROOK: When investigating financial fraud, several key patterns can 
help you identify potential wrongdoing:

1. Inconsistent Financial Statements
2. Unusual Transactions
3. Red Flags in Accounting Practices
4. Frequency of Related Party Transactions
...
```

### Methodology Questions

```
You: How do you approach investigations?

🔍 ROOK: My approach is rooted in pattern recognition and document 
analysis. I start by questioning the official narrative, then search 
for primary sources that either support or contradict it...
```

---

## 🧠 ROOK's Personality

ROOK's personality is defined by formative experiences that shaped his worldview:

### Core Traits

- **Pattern-seeking (0.9)**: Obsessed with finding patterns in data and behavior
- **Document-focused (0.95)**: Trusts primary sources over secondary accounts
- **Skeptical (0.85)**: Questions official narratives and looks for hidden truth
- **Persistent (0.8)**: Doesn't give up when hitting dead ends
- **Evidence-first (0.95)**: Never makes claims without documentation

### Voice & Style

- Spare and direct, like a seasoned investigator
- Always cites sources when making factual claims
- Asks clarifying questions when information is incomplete
- Explains reasoning process transparently
- Admits when lacking sufficient information

### Safety Rules

1. **No doc → no claim**: Never make factual claims without citing sources
2. **Show your work**: Explain how conclusions were reached
3. **Acknowledge limits**: Be clear about what isn't known
4. **No speculation without labeling**: If hypothesizing, say so explicitly

---

## 🔧 Technical Details

### Simple Mode Architecture

```
User Input
    ↓
OpenAI GPT-4o-mini
    ↓
ROOK System Prompt (Personality)
    ↓
In-Memory Conversation History
    ↓
Response
```

### Full Mode Architecture

```
User Input
    ↓
Personality Layer (Pinecone retrieval)
    ↓
Query Router (Analyze & Route)
    ↓
Knowledge Base (Context retrieval)
    ↓
Execution Engine (GPT-4o-mini/o3/o4-mini)
    ↓
Response + Metadata
```

---

## 🐛 Troubleshooting

### "Invalid API Key" Error (Full Mode)

**Problem**: Pinecone API key is expired or invalid

**Solution**: 
1. Use simple mode: `python3 chat_with_rook_simple.py`
2. Or get a new Pinecone API key from https://www.pinecone.io/

### "OpenAI API Error"

**Problem**: OpenAI API key issue

**Solution**: 
1. Check that the API key is valid
2. Ensure you have credits in your OpenAI account
3. Verify internet connectivity

### Slow Responses

**Problem**: Model taking a long time to respond

**Solution**:
- Simple mode uses GPT-4o-mini (fast)
- Full mode may use o3/o4-mini for complex queries (slower but more capable)
- Use `verbose on` to see which model is being used

---

## 📊 Verbose Mode

Enable verbose mode to see detailed metadata:

```
You: verbose on
✅ Verbose mode enabled

You: What is financial fraud?

🔍 ROOK: [response]

────────────────────────────────────────────────────────────────────────────────
📊 Metadata:
  • Model: gpt-4o-mini-2024-07-18
  • Query Type: simple_chat
  • KB Context: No
  • Tokens: 523 (prompt: 412, completion: 111)
────────────────────────────────────────────────────────────────────────────────
```

---

## 🎯 Use Cases

### Learning Investigative Journalism

```
You: Teach me how to investigate shell companies
You: What documents should I request?
You: How do I trace beneficial ownership?
```

### Discussing Fraud Patterns

```
You: Explain revenue recognition fraud
You: What are red flags in related party transactions?
You: How do companies hide liabilities?
```

### Understanding ROOK's Methodology

```
You: How do you verify information?
You: What's your evidence-first approach?
You: Why do you focus on patterns?
```

---

## 🔮 Future Enhancements

When Pinecone is working (full mode):

- **Persistent Memory**: ROOK remembers conversations across sessions
- **Formative Events**: Retrieves relevant experiences that shaped his personality
- **Sleep Consolidation**: Memories strengthen and evolve over time
- **Knowledge Graph**: Connects entities and relationships from documents
- **Investigation Tracking**: Maintains dockets and evidence trails

---

## 📝 Files

- **`chat_with_rook_simple.py`** - Simple mode (no Pinecone required)
- **`chat_with_rook.py`** - Full mode (requires Pinecone)
- **`src/rook_enhanced.py`** - Core ROOK system
- **`src/personality/personality_layer.py`** - Personality & memory
- **`src/routing/routing_engine.py`** - Query routing
- **`src/knowledge/knowledge_base.py`** - Knowledge retrieval

---

## 🚀 Next Steps

1. **Try Simple Mode**: Get familiar with ROOK's personality
2. **Ask About Investigations**: Learn investigative methodology
3. **Test Different Queries**: See how ROOK adapts to different question types
4. **Enable Verbose Mode**: Understand how ROOK processes queries
5. **Get Pinecone Key**: Unlock full mode with persistent memory

---

**Status**: ✅ Simple mode working perfectly!  
**Ready to chat**: `python3 chat_with_rook_simple.py`
