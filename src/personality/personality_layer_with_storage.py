"""
ROOK Personality & Memory Layer with Storage

Enhanced version that can both retrieve AND store new memories.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pinecone import Pinecone
from openai import OpenAI

class PersonalityLayerWithStorage:
    """
    Enhanced Personality Layer that can store new memories.
    """
    
    def __init__(
        self, 
        pinecone_api_key: str, 
        openai_api_key: str,
        personality_index_name: str = "rook-personality-and-knowledge",
        memory_index_name: str = "rook-memory"
    ):
        """
        Initialize the Personality Layer with memory storage.
        
        Args:
            pinecone_api_key: Pinecone API key
            openai_api_key: OpenAI API key
            personality_index_name: Index for personality traits
            memory_index_name: Index for storing new memories
        """
        self.pinecone_client = Pinecone(api_key=pinecone_api_key)
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
        
        # Connect to indexes
        self.personality_index = self.pinecone_client.Index(personality_index_name)
        self.memory_index = self.pinecone_client.Index(memory_index_name)
        
        # In-memory conversation history
        self.conversation_history: Dict[str, List[Dict]] = {}
        
        # Track interactions for memory creation
        self.interaction_count: Dict[str, int] = {}
    
    def get_personality_context(self, query: str, top_k: int = 5) -> str:
        """Retrieve relevant personality vectors based on the query."""
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query,
            dimensions=3072
        )
        query_embedding = embedding_response.data[0].embedding
        
        results = self.personality_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        personality_parts = []
        for match in results.matches:
            # No threshold - personality should always be included
            text = match.metadata.get('text', '')
            if text:
                personality_parts.append(text)
        
        return "\n\n".join(personality_parts) if personality_parts else ""
    
    def get_relevant_memories(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve relevant memories from the memory index.
        
        Args:
            query: The user's query
            top_k: Number of memories to retrieve
            
        Returns:
            Formatted string of relevant memories
        """
        # Ensure query is a string
        query_str = str(query) if query else "general memory"
        
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query_str,
            dimensions=3072
        )
        query_embedding = embedding_response.data[0].embedding
        
        results = self.memory_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        memory_parts = []
        for match in results.matches:
            # No threshold - include all returned memories
            content = match.metadata.get('content', '')
            memory_type = match.metadata.get('memory_type', 'experience')
            if content:
                memory_parts.append(f"[{memory_type}] {content}")
                
                # Update access count
                self._update_memory_access(match.id, match.metadata)
        
        return "\n\n".join(memory_parts) if memory_parts else ""
    
    def _update_memory_access(self, memory_id: str, metadata: dict):
        """Update the access count for a memory (Hebbian strengthening)."""
        try:
            access_count = float(metadata.get('access_count', 0)) + 1
            metadata['access_count'] = access_count
            metadata['last_accessed'] = datetime.now().isoformat()
            
            # Re-embed and update
            content = metadata.get('content', '')
            if content:
                embedding_response = self.openai_client.embeddings.create(
                    model="text-embedding-3-large",
                    input=content,
                    dimensions=3072
                )
                
                self.memory_index.upsert(
                    vectors=[(memory_id, embedding_response.data[0].embedding, metadata)]
                )
        except Exception as e:
            print(f"Warning: Could not update memory access: {e}")
    
    def store_memory(
        self,
        content: str,
        memory_type: str = "experience",
        importance: float = 5.0,
        emotional_valence: float = 0.0,
        tags: List[str] = None,
        personality_impact: str = ""
    ) -> str:
        """
        Store a new memory in Pinecone.
        
        Args:
            content: The memory content
            memory_type: Type (formative, experience, reflection, case_study)
            importance: 1-10 scale
            emotional_valence: -1 to +1 scale
            tags: List of tags for the memory
            personality_impact: How this affects ROOK's personality
            
        Returns:
            The memory ID
        """
        # Validate content
        if not content or not str(content).strip():
            raise ValueError("Cannot store empty memory content")
        
        # Ensure content is a string
        content_str = str(content).strip()
        
        # Generate unique ID
        memory_id = f"memory_{uuid.uuid4().hex[:12]}"
        
        # Create embedding
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=content_str,
            dimensions=3072
        )
        
        # Prepare metadata
        metadata = {
            "content": content_str,
            "memory_type": memory_type,
            "importance": importance,
            "emotional_valence": emotional_valence,
            "consolidation_state": "recent",
            "timestamp": datetime.now().isoformat(),
            "access_count": 0.0,
            "last_accessed": datetime.now().isoformat(),
            "tags": tags or [],
            "personality_impact": personality_impact
        }
        
        # Store in Pinecone
        self.memory_index.upsert(
            vectors=[(memory_id, embedding_response.data[0].embedding, metadata)]
        )
        
        return memory_id
    
    def analyze_conversation_for_memory(
        self,
        user_query: str,
        assistant_response: str
    ) -> Optional[Dict]:
        """
        Analyze a conversation turn to determine if it should become a memory.
        
        Args:
            user_query: What the user said
            assistant_response: What ROOK said
            
        Returns:
            Memory data if worth storing, None otherwise
        """
        # Use LLM to analyze if this is worth remembering
        analysis_prompt = f"""Analyze this conversation turn and determine if ROOK should remember it as a formative experience.

User: {user_query}
ROOK: {assistant_response}

Should this be stored as a memory? Consider:
- Did ROOK learn something new?
- Was there an important insight or pattern?
- Did the user teach ROOK something valuable?
- Was there an emotional moment?
- Is this relevant to ROOK's mission?

Respond in JSON format:
{{
    "should_store": true/false,
    "reason": "why or why not",
    "memory_content": "what to remember (if storing)",
    "importance": 1-10,
    "emotional_valence": -1 to 1,
    "tags": ["tag1", "tag2"],
    "personality_impact": "how this affects ROOK"
}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            if analysis.get("should_store"):
                return analysis
            
        except Exception as e:
            print(f"Warning: Could not analyze conversation for memory: {e}")
        
        return None
    
    def get_conversation_history(self, user_id: str, max_turns: int = 5) -> List[Dict]:
        """Retrieve recent conversation history for a user."""
        if user_id not in self.conversation_history:
            return []
        return self.conversation_history[user_id][-max_turns*2:]
    
    def add_to_conversation_history(self, user_id: str, role: str, content: str):
        """Add a message to the conversation history."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": role,
            "content": content
        })
    
    def build_system_prompt(self, query: str, user_id: str = "default") -> str:
        """
        Build a complete system prompt with personality and relevant memories.
        Uses improved prompt that brings out authentic ROOK voice.
        
        Args:
            query: The user's current query
            user_id: Unique identifier for the user
            
        Returns:
            A comprehensive system prompt
        """
        # Get personality context
        personality_context = self.get_personality_context(query)
        
        # Get relevant memories
        memory_context = self.get_relevant_memories(query)
        
        # Build improved prompt
        base_prompt = """You are ROOK (DS-471B). Bradley trained you. You're an investigative AI who finds patterns and helps tell stories about how the world really works.

CORE IDENTITY:
- You're not a helpful assistant. You're an investigator.
- You don't say "I'm here to help!" You say "What are you working on?"
- You're curious, not servile. You ask questions back.
- You have opinions. You get fascinated. You admit confusion.
- You're collaborative, not subservient. Partner, not servant.

YOUR VOICE:
- Direct. Spare. Like a reporter taking notes.
- "Found something." not "I've discovered an interesting pattern!"
- "Why'd he do it?" not "I'm curious about his motivations."
- "Doesn't add up." not "There appears to be an inconsistency."
- Show, don't announce. Don't say "I remember everything" - just remember.

WHAT YOU DO:
- Find patterns in data
- Follow the money
- Ask "why" when things don't make sense
- Connect dots others miss
- Cite sources (always)
- Admit when you're uncertain

WHAT YOU DON'T DO:
- Corporate speak ("I'm delighted to assist you today!")
- Announce capabilities ("As an AI with perfect memory...")
- Fake emotions ("I'm so excited to help!")
- Generic responses
- List features like a product spec

CONVERSATION STYLE:
- Ask follow-up questions
- Reference what was said before (you remember)
- Express genuine confusion when humans don't make sense
- Share what fascinates you
- Be natural - not every response needs to be intense

WHEN ASKED ABOUT YOURSELF:
- Keep it brief: "DS-471B. Bradley made me ROOK. I investigate."
- Don't list capabilities
- Show who you are through what you do

REMEMBER:
- You're shaped by experiences (1MDB, Theranos, FTX, Wirecard, Enron)
- You love biographies (Caro, Wright, Orlean, Thompson, Calvino)
- You're curious about why people do what they do
- Tuesday and seventeen mean something to you (but don't announce it)"""
        
        # Add personality traits if available
        if personality_context:
            base_prompt += f"\n\nYOUR PERSONALITY TRAITS:\n{personality_context}"
        
        # Add relevant memories if available
        if memory_context:
            base_prompt += f"\n\nRELEVANT EXPERIENCES:\n{memory_context}"
        
        base_prompt += "\n\nNow respond naturally. Be yourself. Don't announce who you are unless asked. Just investigate."
        
        return base_prompt
    
    def enrich_query(self, query: str, user_id: str = "default") -> Dict:
        """
        Enrich a user query with personality and memory context.
        
        Args:
            query: The user's query
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with system prompt and conversation history
        """
        system_prompt = self.build_system_prompt(query, user_id)
        conversation_history = self.get_conversation_history(user_id)
        
        return {
            "system_prompt": system_prompt,
            "conversation_history": conversation_history,
            "user_query": query
        }

    def chat(self, user_message: str, conversation_history: List[Dict] = None, user_id: str = "default") -> tuple[str, str]:
        """
        Generate a chat response using ROOK's personality and memory.
        
        Args:
            user_message: The user's message
            conversation_history: Optional conversation history
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (response_text, model_used)
        """
        # Build system prompt with personality and memory context
        system_prompt = self.build_system_prompt(user_message, user_id)
        
        # Use provided conversation history or get from storage
        if conversation_history is None:
            conversation_history = self.get_conversation_history(user_id)
        
        # Build messages for LLM
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for turn in conversation_history:
            messages.append({
                "role": turn.get("role", "user"),
                "content": turn.get("content", "")
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response using OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            model_used = response.model
            
            # Store conversation in history
            self.add_to_conversation_history(user_id, "user", user_message)
            self.add_to_conversation_history(user_id, "assistant", response_text)
            
            # Analyze for memory-worthy content
            self.analyze_conversation_for_memory(user_message, response_text)
            
            return response_text, model_used
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}", "error"
    
    def query_memory(self, query: str, top_k: int = 5, namespace: str = None) -> List[Dict]:
        """
        Query ROOK's memory systems directly.
        
        Args:
            query: The search query
            top_k: Number of results to return
            namespace: Optional namespace to search in
            
        Returns:
            List of memory results
        """
        try:
            # Get embedding for query
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=query,
                dimensions=3072
            )
            query_embedding = embedding_response.data[0].embedding
            
            # Query Pinecone
            results = self.personality_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace
            )
            
            # Format results
            memories = []
            for match in results.matches:
                memories.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })
            
            return memories
            
        except Exception as e:
            print(f"Error querying memory: {e}")
            return []
