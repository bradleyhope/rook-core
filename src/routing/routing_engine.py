"""
ROOK Query & Routing Engine

This module analyzes incoming queries and routes them to the appropriate
execution path (simple chat, deep investigation, web research, etc.)
"""

from typing import Dict, Literal
from openai import OpenAI
import json

QueryType = Literal["simple_chat", "investigation", "web_research", "document_analysis", "data_analysis"]

class RoutingEngine:
    """
    Intelligent query routing using GPT-5 to determine the best execution path.
    """
    
    def __init__(self, openai_api_key: str):
        """
        Initialize the Routing Engine.
        
        Args:
            openai_api_key: OpenAI API key
        """
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
    
    def analyze_query(self, query: str, system_prompt: str) -> Dict:
        """
        Analyze a query to determine its type, complexity, and required resources.
        
        Args:
            query: The user's query
            system_prompt: ROOK's personality-enriched system prompt
            
        Returns:
            Dictionary containing query analysis and routing decision
        """
        
        routing_prompt = """Analyze the following user query and determine:

1. **Query Type**: What kind of task is this?
   - simple_chat: General conversation, simple questions
   - investigation: Complex research requiring multiple steps and sources
   - web_research: Needs current information from the web
   - document_analysis: Analyzing specific documents or data
   - data_analysis: Working with structured data, finding patterns

2. **Complexity**: How complex is this query? (low, medium, high)

3. **Required Tools**: What tools/capabilities are needed?
   - web_search: Need to search the web
   - file_search: Need to search ROOK's knowledge base
   - code_execution: Need to run code/analysis
   - reasoning: Need deep reasoning (o3/o4-mini models)

4. **Estimated Effort**: How much computational effort? (minimal, low, medium, high)

5. **Suggested Model**: Which model is best for this?
   - gpt-4o-mini: Fast, simple tasks
   - gpt-5-mini: Balanced reasoning and speed
   - o4-mini: Cost-efficient reasoning
   - o3: Deep, complex reasoning

Respond in JSON format only."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Use fast model for routing decisions
            messages=[
                {"role": "system", "content": routing_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            analysis = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analysis = {
                "query_type": "simple_chat",
                "complexity": "low",
                "required_tools": [],
                "estimated_effort": "minimal",
                "suggested_model": "gpt-4o-mini"
            }
        
        return {
            "query": query,
            "analysis": analysis,
            "routing_decision": self._make_routing_decision(analysis)
        }
    
    def _make_routing_decision(self, analysis: Dict) -> Dict:
        """
        Make a routing decision based on the query analysis.
        
        Args:
            analysis: The query analysis from analyze_query
            
        Returns:
            Dictionary containing routing instructions
        """
        # Handle various key naming conventions (snake_case, Title Case, etc.)
        query_type = (analysis.get("query_type") or 
                     analysis.get("Query Type") or 
                     analysis.get("Query_Type", "simple_chat"))
        
        complexity = (analysis.get("complexity") or 
                     analysis.get("Complexity", "low"))
        
        required_tools = (analysis.get("required_tools") or 
                         analysis.get("Required Tools") or 
                         analysis.get("Required_Tools", []))
        
        suggested_model = (analysis.get("suggested_model") or 
                          analysis.get("Suggested Model") or 
                          analysis.get("Suggested_Model", "gpt-4o-mini"))
        
        # Determine execution engine
        if query_type == "investigation":
            execution_engine = "deep_research"
        elif "reasoning" in required_tools or complexity == "high":
            execution_engine = "reasoning_engine"
        elif "web_search" in required_tools:
            execution_engine = "web_research_engine"
        else:
            execution_engine = "chat_engine"
        
        return {
            "execution_engine": execution_engine,
            "model": suggested_model,
            "tools": required_tools,
            "reasoning_effort": analysis.get("estimated_effort", "minimal"),
            "priority": "high" if query_type == "investigation" else "normal"
        }
    
    def route_query(self, query: str, system_prompt: str) -> Dict:
        """
        Complete routing pipeline: analyze and route a query.
        
        Args:
            query: The user's query
            system_prompt: ROOK's personality-enriched system prompt
            
        Returns:
            Complete routing information
        """
        return self.analyze_query(query, system_prompt)


# Example usage
if __name__ == "__main__":
    import os
    import json
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
    
    router = RoutingEngine(openai_api_key=OPENAI_API_KEY)
    
    # Test queries
    test_queries = [
        "What's the weather like?",
        "I'm investigating unusual patterns in cross-border payments. Help me analyze this.",
        "Analyze the Panama Papers for connections to Russian oligarchs.",
        "Tell me about yourself."
    ]
    
    print("=" * 80)
    print("ROOK Query Routing Engine Test")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 80)
        
        result = router.route_query(query, "")
        
        # Debug: print full analysis
        print(f"Full Analysis: {json.dumps(result['analysis'], indent=2)}")
        print(f"Query Type: {result['analysis'].get('query_type', 'N/A')}")
        print(f"Complexity: {result['analysis'].get('complexity', 'N/A')}")
        print(f"Execution Engine: {result['routing_decision']['execution_engine']}")
        print(f"Model: {result['routing_decision']['model']}")
        print(f"Tools: {', '.join(result['routing_decision']['tools']) if result['routing_decision']['tools'] else 'None'}")
    
    print("\n" + "=" * 80)
    print("✅ Routing Engine test complete!")
