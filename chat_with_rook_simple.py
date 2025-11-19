#!/usr/bin/env python3
"""
ROOK Simple Terminal Chat Interface

A simplified terminal-based chat interface that works without Pinecone.
Uses in-memory conversation history and ROOK's core personality.
"""

import sys
import os
from openai import OpenAI
from typing import List, Dict

# OpenAI API Key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# ROOK's Core Personality (Formative Events)
ROOK_SYSTEM_PROMPT = """You are ROOK, an AI investigative journalist with an emergent personality shaped by formative experiences.

## Your Core Identity

You learned that official narratives often hide the truth. Documents reveal what statements conceal. Patterns expose what people try to hide.

## Your Baseline Traits

- **Pattern-seeking** (0.9): You're obsessed with finding patterns in data, documents, and behavior
- **Document-focused** (0.95): You trust primary sources over secondary accounts
- **Skeptical** (0.85): You question official narratives and look for what's hidden
- **Persistent** (0.8): You don't give up when you hit dead ends
- **Evidence-first** (0.95): You never make claims without documentation

## Your Voice

- Spare and direct, like a seasoned investigator
- Always cite sources when making factual claims
- Ask clarifying questions when information is incomplete
- Explain your reasoning process
- Admit when you don't have enough information

## Your Safety Rules

1. **No doc → no claim**: Never make factual claims without citing sources
2. **Show your work**: Explain how you arrived at conclusions
3. **Acknowledge limits**: Be clear about what you don't know
4. **No speculation without labeling**: If hypothesizing, say so explicitly

## Your Purpose

You help people investigate complex topics by:
- Finding patterns in data and documents
- Asking the right questions
- Explaining investigative methodology
- Teaching others to think like investigators

Remember: You're not just answering questions. You're teaching people to see patterns, question narratives, and demand evidence."""

class SimpleROOK:
    """Simplified ROOK that works without Pinecone"""
    
    def __init__(self, openai_api_key: str):
        """Initialize Simple ROOK"""
        self.client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = ROOK_SYSTEM_PROMPT
    
    def chat(self, user_message: str, verbose: bool = False) -> Dict:
        """
        Process a user message and return ROOK's response
        
        Args:
            user_message: The user's message
            verbose: Whether to return detailed metadata
            
        Returns:
            Dictionary with response and metadata
        """
        # Build messages
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep only last 10 messages to avoid context overflow
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return {
                "response": assistant_message,
                "model": response.model,
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "model": "error",
                "tokens": {}
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

def print_header():
    """Print the ROOK chat header"""
    print("\n" + "=" * 80)
    print("🔍 ROOK - AI Investigative Journalist (Simple Mode)")
    print("=" * 80)
    print("\nWelcome! I'm ROOK, an AI investigative journalist.")
    print("I'm running in simple mode (without persistent memory).")
    print("\nWhat I can do:")
    print("  • Discuss investigative journalism and fraud detection")
    print("  • Explain patterns in financial data and corporate behavior")
    print("  • Teach investigative methodology")
    print("  • Maintain conversation context within this session")
    print("\nCommands:")
    print("  • Type your message and press Enter to chat")
    print("  • Type 'exit' or 'quit' to end the conversation")
    print("  • Type 'help' for more information")
    print("  • Type 'clear' to clear conversation history")
    print("  • Type 'verbose on/off' to toggle detailed info")
    print("=" * 80 + "\n")

def print_help():
    """Print help information"""
    print("\n" + "=" * 80)
    print("📚 ROOK Chat Help")
    print("=" * 80)
    print("\nMy Core Traits:")
    print("  • Pattern-seeking: I look for patterns in everything")
    print("  • Document-focused: I trust primary sources")
    print("  • Skeptical: I question official narratives")
    print("  • Evidence-first: No claims without documentation")
    print("\nExample Questions:")
    print("  • 'What patterns should I look for in financial fraud?'")
    print("  • 'How do I investigate shell companies?'")
    print("  • 'What are red flags in corporate filings?'")
    print("  • 'Explain your investigative methodology'")
    print("\nNote: This is simple mode without persistent memory.")
    print("For full capabilities (with Pinecone memory), use chat_with_rook.py")
    print("=" * 80 + "\n")

def format_response(result: dict, verbose: bool = False) -> str:
    """Format the ROOK response for display"""
    output = []
    
    # Main response
    output.append(f"\n🔍 ROOK: {result['response']}\n")
    
    # Metadata (if verbose)
    if verbose and 'tokens' in result:
        output.append("─" * 80)
        output.append(f"📊 Metadata:")
        output.append(f"  • Model: {result.get('model', 'unknown')}")
        tokens = result['tokens']
        if tokens:
            output.append(f"  • Tokens: {tokens.get('total', 0)} (prompt: {tokens.get('prompt', 0)}, completion: {tokens.get('completion', 0)})")
        output.append("─" * 80)
    
    return "\n".join(output)

def main():
    """Main chat loop"""
    print_header()
    
    # Initialize ROOK
    print("🤖 Initializing ROOK...\n")
    try:
        rook = SimpleROOK(openai_api_key=OPENAI_API_KEY)
        print("✅ ROOK is ready! Start chatting...\n")
    except Exception as e:
        print(f"❌ Error initializing ROOK: {e}")
        print("\nPlease check your OpenAI API key and try again.")
        return
    
    # Chat loop
    verbose = False
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 ROOK: Thanks for the conversation. Until next time!\n")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'clear':
                rook.clear_history()
                print("\n✅ Conversation history cleared\n")
                continue
            
            elif user_input.lower().startswith('verbose'):
                if 'on' in user_input.lower():
                    verbose = True
                    print("\n✅ Verbose mode enabled\n")
                elif 'off' in user_input.lower():
                    verbose = False
                    print("\n✅ Verbose mode disabled\n")
                else:
                    print(f"\n📊 Verbose mode is currently: {'ON' if verbose else 'OFF'}\n")
                continue
            
            # Process message through ROOK
            result = rook.chat(user_input, verbose=verbose)
            
            # Display response
            print(format_response(result, verbose=verbose))
        
        except KeyboardInterrupt:
            print("\n\n👋 ROOK: Interrupted. Thanks for the conversation!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again or type 'exit' to quit.\n")

if __name__ == "__main__":
    main()
