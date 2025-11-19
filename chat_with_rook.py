#!/usr/bin/env python3
"""
ROOK Terminal Chat Interface

A simple terminal-based chat interface to interact with ROOK.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rook_enhanced import ROOKEnhanced
import readline  # For better input editing

# API Keys
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def print_header():
    """Print the ROOK chat header"""
    print("\n" + "=" * 80)
    print("🔍 ROOK - AI Investigative Journalist")
    print("=" * 80)
    print("\nWelcome! I'm ROOK, an AI investigative journalist with emergent personality.")
    print("I learn from experiences, maintain memories, and always cite my sources.")
    print("\nCommands:")
    print("  • Type your message and press Enter to chat")
    print("  • Type 'exit' or 'quit' to end the conversation")
    print("  • Type 'help' for more information")
    print("  • Type 'verbose on/off' to toggle detailed processing info")
    print("=" * 80 + "\n")

def print_help():
    """Print help information"""
    print("\n" + "=" * 80)
    print("📚 ROOK Chat Help")
    print("=" * 80)
    print("\nWhat I can do:")
    print("  • Answer questions about investigative journalism")
    print("  • Discuss fraud patterns and financial investigations")
    print("  • Explain my reasoning and methodology")
    print("  • Learn from our conversation and remember context")
    print("\nWhat makes me different:")
    print("  • My personality emerges from formative experiences")
    print("  • I always cite sources and show my reasoning")
    print("  • I maintain conversation history and learn from interactions")
    print("  • I use different models based on query complexity")
    print("\nSafety features:")
    print("  • Evidence-first: I don't make claims without documentation")
    print("  • Two-model verification: My claims are verified by a separate system")
    print("  • Transparent reasoning: I show how I arrived at conclusions")
    print("=" * 80 + "\n")

def format_response(result: dict, verbose: bool = False) -> str:
    """Format the ROOK response for display"""
    output = []
    
    # Main response
    output.append(f"\n🔍 ROOK: {result['response']}\n")
    
    # Metadata (if verbose)
    if verbose:
        output.append("─" * 80)
        output.append(f"📊 Metadata:")
        output.append(f"  • Model: {result['model_used']}")
        output.append(f"  • Query Type: {result['routing']['analysis'].get('query_type', 'unknown')}")
        output.append(f"  • KB Context: {'Yes' if result['kb_context_used'] else 'No'}")
        if 'tokens_used' in result:
            tokens = result['tokens_used']
            output.append(f"  • Tokens: {tokens.get('total', 0)} (prompt: {tokens.get('prompt', 0)}, completion: {tokens.get('completion', 0)})")
        output.append("─" * 80)
    
    return "\n".join(output)

def main():
    """Main chat loop"""
    print_header()
    
    # Initialize ROOK
    try:
        rook = ROOKEnhanced(
            pinecone_api_key=PINECONE_API_KEY,
            openai_api_key=OPENAI_API_KEY
        )
    except Exception as e:
        print(f"\n❌ Error initializing ROOK: {e}")
        print("\nPlease check your API keys and try again.")
        return
    
    print("\n✅ ROOK is ready! Start chatting...\n")
    
    # Chat loop
    verbose = False
    user_id = "terminal_user"
    
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
            
            # Process query through ROOK
            result = rook.process_query(
                query=user_input,
                user_id=user_id,
                verbose=False  # Don't print internal verbose output
            )
            
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
