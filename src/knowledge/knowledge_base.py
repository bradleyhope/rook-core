"""
ROOK Knowledge Base Connector

Provides access to ROOK's various Pinecone indexes:
- Research Hub: Investigation findings and research
- People Database: Individuals and their connections
- Tools: OSINT tools and methodologies
- Interview Database: Interview transcripts and insights
- Personality & Knowledge: ROOK's core personality and learned knowledge
- Memory: Long-term conversation memory
"""

from typing import Dict, List, Optional
from pinecone import Pinecone
from openai import OpenAI

class KnowledgeBase:
    """
    Manages access to ROOK's knowledge bases stored in Pinecone.
    """
    
    # Index names
    INDEX_RESEARCH = "rook-research-hub"
    INDEX_PEOPLE = "rook-people-database"
    INDEX_TOOLS = "rook-tools"
    INDEX_INTERVIEWS = "rook-interview-database"
    INDEX_PERSONALITY = "rook-personality-and-knowledge"
    INDEX_MEMORY = "rook-memory"
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str):
        """
        Initialize the Knowledge Base connector.
        
        Args:
            pinecone_api_key: Pinecone API key
            openai_api_key: OpenAI API key (for embeddings)
        """
        self.pinecone_client = Pinecone(api_key=pinecone_api_key)
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
        
        # Connect to all indexes
        self.indexes = {}
        for index_name in [
            self.INDEX_RESEARCH,
            self.INDEX_PEOPLE,
            self.INDEX_TOOLS,
            self.INDEX_INTERVIEWS,
            self.INDEX_PERSONALITY,
            self.INDEX_MEMORY
        ]:
            try:
                self.indexes[index_name] = self.pinecone_client.Index(index_name)
            except Exception as e:
                print(f"⚠️  Warning: Could not connect to index {index_name}: {e}")
    
    def search(
        self, 
        query: str, 
        index_name: str, 
        top_k: int = 10,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search a specific knowledge base index.
        
        Args:
            query: Search query
            index_name: Name of the index to search
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of search results with metadata
        """
        if index_name not in self.indexes:
            return []
        
        # Generate embedding for query
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query,
            dimensions=3072
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Search Pinecone
        results = self.indexes[index_name].query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        formatted_results = []
        for match in results.matches:
            formatted_results.append({
                "id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "metadata": match.metadata
            })
        
        return formatted_results
    
    def search_research(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search the Research Hub for investigation findings."""
        return self.search(query, self.INDEX_RESEARCH, top_k)
    
    def search_people(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search the People Database for individuals and connections."""
        return self.search(query, self.INDEX_PEOPLE, top_k)
    
    def search_tools(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search for OSINT tools and methodologies."""
        return self.search(query, self.INDEX_TOOLS, top_k)
    
    def search_interviews(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search interview transcripts and insights."""
        return self.search(query, self.INDEX_INTERVIEWS, top_k)
    
    def search_personality(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search ROOK's personality and learned knowledge."""
        return self.search(query, self.INDEX_PERSONALITY, top_k)
    
    def search_memory(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search long-term conversation memory."""
        return self.search(query, self.INDEX_MEMORY, top_k)
    
    def multi_search(
        self, 
        query: str, 
        indexes: List[str], 
        top_k_per_index: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Search across multiple knowledge bases simultaneously.
        
        Args:
            query: Search query
            indexes: List of index names to search
            top_k_per_index: Number of results per index
            
        Returns:
            Dictionary mapping index names to their results
        """
        results = {}
        for index_name in indexes:
            results[index_name] = self.search(query, index_name, top_k_per_index)
        return results
    
    def get_context_for_query(self, query: str, query_type: str = "investigation") -> str:
        """
        Get relevant context from knowledge bases based on query type.
        
        Args:
            query: The user's query
            query_type: Type of query (investigation, simple_chat, etc.)
            
        Returns:
            Formatted context string to inject into the prompt
        """
        context_parts = []
        
        if query_type == "investigation":
            # Search research hub and people database
            research_results = self.search_research(query, top_k=5)
            people_results = self.search_people(query, top_k=3)
            
            # Add high-confidence results without hardcoded labels
            for result in research_results:
                if result['score'] > 0.75:
                    context_parts.append(result['text'])
            
            for result in people_results:
                if result['score'] > 0.75:
                    context_parts.append(result['text'])
        
        elif query_type == "document_analysis":
            # Search research hub and interviews
            research_results = self.search_research(query, top_k=5)
            interview_results = self.search_interviews(query, top_k=3)
            
            for result in research_results:
                if result['score'] > 0.75:
                    context_parts.append(result['text'])
        
        return "\n\n".join(context_parts) if context_parts else ""


# Example usage
if __name__ == "__main__":
    import os
    
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YOUR_PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
    
    print("=" * 80)
    print("ROOK Knowledge Base Test")
    print("=" * 80 + "\n")
    
    kb = KnowledgeBase(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    print(f"✅ Connected to {len(kb.indexes)} knowledge base indexes\n")
    
    # Test search
    test_query = "financial fraud patterns"
    print(f"🔍 Searching for: '{test_query}'\n")
    
    # Search research hub
    print("📚 Research Hub Results:")
    print("-" * 80)
    research_results = kb.search_research(test_query, top_k=3)
    for i, result in enumerate(research_results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   {result['text'][:150]}...")
        print()
    
    # Get context for investigation
    print("\n📋 Context for Investigation:")
    print("-" * 80)
    context = kb.get_context_for_query(test_query, query_type="investigation")
    if context:
        print(context)
    else:
        print("No high-confidence context found.")
    
    print("\n" + "=" * 80)
    print("✅ Knowledge Base test complete!")
