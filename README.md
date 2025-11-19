# ROOK - AI Investigative Journalist

**ROOK** is an AI investigative journalist with emergent personality, memory, and learning capabilities.

## Features

- 🧠 **Emergent Personality** - Shaped by formative events, not hardcoded
- 💾 **Persistent Memory** - 14,641 vectors across 9 knowledge bases
- 🔍 **Investigative Tools** - 744 OSINT tools and methodologies
- 👥 **People Database** - 2,988 individuals for investigations
- 📚 **Interview Knowledge** - 69 interview transcripts
- 🎯 **Pattern Recognition** - Fraud detection and hypothesis generation
- 🖥️ **Terminal Interface** - Old-school hacker aesthetic

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export PINECONE_API_KEY="your-key"
export PINECONE_ENVIRONMENT="us-east-1"

# Run the server
cd api
python chat_server.py
```

Visit `http://localhost:8080` to chat with ROOK.

### Deploy to Render

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for detailed deployment instructions.

## Architecture

- **Backend**: FastAPI + Python 3.11
- **Memory**: Pinecone vector database
- **LLM**: OpenAI GPT-4o-mini
- **Frontend**: Terminal-style HTML/CSS/JS

## Documentation

- [Complete Plan](./ROOK_COMPLETE_PLAN.md) - Vision and architecture
- [Roadmap](./ROOK_ROADMAP_UPDATED.md) - Development timeline
- [Memory Architecture](./MEMORY_ARCHITECTURE_ROADMAP.md) - Memory system design
- [Render Deployment](./RENDER_DEPLOYMENT.md) - Production deployment guide

## Project Structure

```
rook-core/
├── api/
│   ├── chat_server.py      # FastAPI server
│   └── main.py             # Alternative entry point
├── src/
│   ├── personality/        # Personality layer with Pinecone
│   ├── knowledge/          # Knowledge base integration
│   ├── routing/            # Query routing engine
│   ├── memory/             # Experience-based memory
│   ├── safety/             # Evidence-first safety layer
│   └── sleep/              # Consolidation system
├── rook_chat.html          # Terminal web interface
├── requirements.txt        # Python dependencies
└── render.yaml             # Render deployment config
```

## Environment Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_ENVIRONMENT` - Pinecone environment (us-east-1)

## License

Proprietary - All rights reserved

## Contact

Created by Bradley Mauerberger
