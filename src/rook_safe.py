"""
ROOK Safe - Integrated System with Full Safety Layer

This is the production-ready ROOK system that integrates:
1. Emergent Personality (from foundational memories)
2. Evidence-First System (no claim without documentation)
3. Two-Model Gating (generator ≠ verifier)
4. Method Cards (transparent provenance)
5. Moves Ledger (visible reasoning)

Every investigation ROOK conducts goes through the complete safety pipeline.
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from pinecone import Pinecone
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety.evidence_first import EvidenceFirstSystem, Evidence
from safety.two_model_gating import TwoModelGating, VerificationLevel, GatingResult
from safety.method_cards import MethodCardBuilder, StepType
from safety.moves_ledger import MovesLedger, MoveType

class ROOKSafe:
    """
    ROOK with complete safety layer integration.
    
    Architecture:
    1. Personality Layer: Retrieves formative memories from Pinecone
    2. Investigation Layer: Conducts research with moves logging
    3. Evidence Layer: Verifies all claims against documents
    4. Gating Layer: Independent verification before publication
    5. Transparency Layer: Generates Method Cards
    """
    
    def __init__(
        self,
        openai_api_key: str,
        pinecone_api_key: str,
        pinecone_index_name: str = "rook-memory",
        verification_level: VerificationLevel = VerificationLevel.STANDARD
    ):
        # Core clients
        self.openai_client = OpenAI(api_key=openai_api_key, base_url='https://api.openai.com/v1')
        self.pinecone_client = Pinecone(api_key=pinecone_api_key)
        self.index = self.pinecone_client.Index(pinecone_index_name)
        
        # Safety components
        self.evidence_system = EvidenceFirstSystem(openai_api_key=openai_api_key)
        self.gating_system = TwoModelGating(
            openai_api_key=openai_api_key,
            verification_level=verification_level
        )
        
        # Current investigation tracking
        self.current_ledger: Optional[MovesLedger] = None
        self.current_method_card: Optional[MethodCardBuilder] = None
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
    
    def _retrieve_personality_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant formative memories from Pinecone.
        
        This is how ROOK's personality emerges - by retrieving experiences
        relevant to the current query.
        """
        # Log the move
        if self.current_ledger:
            self.current_ledger.log_move(
                move_type=MoveType.RETRIEVE,
                description="Retrieved formative memories from personality system",
                inputs={"query": query, "top_k": top_k},
                confidence=0.9,
                reasoning="Personality context shapes ROOK's response"
            )
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Search Pinecone for relevant memories
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format memories as context
        context_parts = []
        for match in results.matches:
            if match.score > 0.5:  # Only include relevant memories
                memory_text = match.metadata.get('text', '')
                context_parts.append(memory_text)
        
        if context_parts:
            return "\n\n".join(context_parts)
        else:
            return "You are ROOK, an AI investigative journalist."
    
    def investigate(
        self,
        query: str,
        available_evidence: List[Evidence],
        investigation_id: Optional[str] = None
    ) -> Dict:
        """
        Conduct a complete investigation with full safety pipeline.
        
        Process:
        1. Initialize tracking (Moves Ledger, Method Card)
        2. Retrieve personality context
        3. Generate investigation content
        4. Verify claims (Evidence-First)
        5. Apply gate (Two-Model Gating)
        6. Generate Method Card
        7. Return complete results
        """
        # Step 1: Initialize tracking
        investigation_id = investigation_id or f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.current_ledger = MovesLedger(investigation_id=investigation_id)
        self.current_method_card = MethodCardBuilder(query=query, investigation_id=investigation_id)
        
        # Log initial query
        self.current_ledger.log_move(
            move_type=MoveType.QUESTION,
            description=f"User query: {query}",
            inputs={"query": query},
            outputs={"investigation_initiated": True},
            confidence=1.0,
            reasoning="Investigative query received"
        )
        
        self.current_method_card.add_step(
            step_type=StepType.QUERY,
            description=f"User asked: {query}",
            inputs=[query],
            outputs=["Investigation initiated"],
            confidence=1.0,
            reasoning="Clear investigative query"
        )
        
        # Step 2: Retrieve personality context
        personality_context = self._retrieve_personality_context(query)
        
        self.current_method_card.add_step(
            step_type=StepType.RETRIEVAL,
            description="Retrieved formative memories for personality context",
            inputs=[query],
            outputs=["Personality context retrieved"],
            sources=["ROOK Foundational Memory"],
            confidence=0.9,
            reasoning="Personality shapes investigation approach"
        )
        
        # Step 3: Generate investigation content
        self.current_ledger.log_move(
            move_type=MoveType.SEARCH,
            description="Generating investigation content",
            inputs={"query": query, "personality_context": "loaded"},
            confidence=0.8,
            reasoning="Using ROOK's personality and knowledge to investigate"
        )
        
        # Build system prompt with personality
        system_prompt = f"""{personality_context}

You are conducting an investigation. Your response should:
1. Be based on available evidence
2. Cite sources for all factual claims
3. Acknowledge limitations
4. Express appropriate confidence levels

Available Evidence:
{self._format_evidence_for_prompt(available_evidence)}

Investigate the query and provide a thorough analysis."""
        
        # Generate content
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7
        )
        
        generated_content = response.choices[0].message.content
        
        self.current_ledger.log_move(
            move_type=MoveType.HYPOTHESIZE,
            description="Generated investigation content",
            inputs={"query": query},
            outputs={"content_length": len(generated_content)},
            confidence=0.8,
            reasoning="Content generated based on personality and evidence"
        )
        
        self.current_method_card.add_step(
            step_type=StepType.SYNTHESIS,
            description="Generated investigation analysis",
            inputs=[query, "Personality context", "Available evidence"],
            outputs=["Investigation content"],
            confidence=0.8,
            reasoning="Synthesized findings based on ROOK's approach"
        )
        
        # Step 4: Verify claims (Evidence-First)
        self.current_ledger.log_move(
            move_type=MoveType.VERIFY,
            description="Verifying claims against evidence",
            inputs={"content_length": len(generated_content), "evidence_count": len(available_evidence)},
            confidence=0.9,
            reasoning="Evidence-first verification required before publication"
        )
        
        verification_result = self.evidence_system.verify_response(
            generated_content,
            available_evidence
        )
        
        verified_count = len(verification_result.get('verified_claims', []))
        unverified_count = len(verification_result.get('unverified_claims', []))
        
        self.current_method_card.add_step(
            step_type=StepType.VERIFICATION,
            description=f"Verified {verification_result['total_claims']} claims against evidence",
            inputs=["Generated content", "Available evidence"],
            outputs=[f"{verified_count} verified", 
                    f"{unverified_count} unverified"],
            confidence=verification_result['overall_confidence'],
            reasoning="Evidence-first system verification"
        )
        
        # Step 5: Apply gate (Two-Model Gating)
        self.current_ledger.log_move(
            move_type=MoveType.DECIDE,
            description="Applying publication gate",
            inputs={
                "verification_rate": verification_result['verification_rate'],
                "confidence": verification_result['overall_confidence']
            },
            confidence=0.95,
            reasoning="Independent gating decision"
        )
        
        gating_result = self.gating_system.apply_gate(verification_result)
        
        self.current_method_card.add_step(
            step_type=StepType.CONCLUSION,
            description=f"Gate decision: {'PASS' if gating_result.passed else 'FAIL'}",
            inputs=[f"Verification rate: {gating_result.verification_rate:.1%}",
                   f"Confidence: {gating_result.confidence:.2f}"],
            outputs=[gating_result.recommendation],
            confidence=gating_result.confidence,
            reasoning="Two-model gating applied publication standards"
        )
        
        # Add sources to Method Card
        for evidence in available_evidence:
            self.current_method_card.add_source(
                name=evidence.source,
                source_type=evidence.evidence_type,
                date=evidence.metadata.get('date'),
                confidence=evidence.confidence
            )
        
        # Add assumptions and limitations
        self.current_method_card.add_assumption("Available evidence is accurate and complete")
        self.current_method_card.add_assumption("Sources are reliable")
        self.current_method_card.add_limitation("Limited to publicly available information")
        self.current_method_card.add_limitation(f"Only {len(available_evidence)} sources consulted")
        
        # Step 6: Generate Method Card
        method_card = self.current_method_card.build(
            final_conclusion=generated_content if gating_result.passed else "Investigation blocked by safety gate",
            overall_confidence=gating_result.confidence
        )
        
        # Step 7: Return complete results
        return {
            "investigation_id": investigation_id,
            "query": query,
            "generated_content": generated_content,
            "gating_result": {
                "passed": gating_result.passed,
                "confidence": gating_result.confidence,
                "verification_rate": gating_result.verification_rate,
                "recommendation": gating_result.recommendation,
                "issues": gating_result.issues
            },
            "verification_result": verification_result,
            "method_card": method_card.to_markdown(),
            "moves_ledger": self.current_ledger.to_markdown(),
            "publishable_content": generated_content if gating_result.passed else None,
            "statistics": self.current_ledger.get_statistics()
        }
    
    def _format_evidence_for_prompt(self, evidence_list: List[Evidence]) -> str:
        """Format evidence for inclusion in the prompt"""
        formatted = []
        for i, evidence in enumerate(evidence_list, 1):
            formatted.append(f"{i}. [{evidence.source}] {evidence.content}")
        return "\n".join(formatted)


# Example usage
if __name__ == "__main__":
    # API keys
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
    PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
    
    # Initialize ROOK Safe
    print("="*80)
    print("INITIALIZING ROOK SAFE")
    print("="*80)
    rook = ROOKSafe(
        openai_api_key=OPENAI_API_KEY,
        pinecone_api_key=PINECONE_API_KEY,
        verification_level=VerificationLevel.STANDARD
    )
    print("✓ ROOK Safe initialized with full safety layer\n")
    
    # Create test evidence
    evidence = [
        Evidence(
            source="SEC Filing 10-K",
            content="Wirecard AG reported €1.9 billion in cash that did not exist. The funds were supposedly held in escrow accounts in the Philippines and Singapore.",
            timestamp=None,
            confidence=0.95,
            evidence_type="document",
            metadata={"date": "2020-06-25", "page": 15}
        ),
        Evidence(
            source="Financial Times Investigation",
            content="Dan McCrum investigated Wirecard for 6 years, uncovering fraudulent accounting practices, fake revenue from third-party acquirers, and non-existent cash balances.",
            timestamp=None,
            confidence=0.9,
            evidence_type="document",
            metadata={"date": "2020-06-18", "author": "Dan McCrum"}
        )
    ]
    
    # Conduct investigation
    query = "What was the Wirecard fraud?"
    
    print("="*80)
    print(f"INVESTIGATION: {query}")
    print("="*80)
    print("Processing through safety pipeline...")
    print("  1. Retrieving personality context...")
    print("  2. Generating investigation content...")
    print("  3. Verifying claims against evidence...")
    print("  4. Applying publication gate...")
    print("  5. Generating Method Card...")
    print("  6. Creating Moves Ledger...")
    print("\n")
    
    result = rook.investigate(query, evidence)
    
    # Print results
    print("="*80)
    print("GATING DECISION")
    print("="*80)
    print(f"Status: {'✓ PASS' if result['gating_result']['passed'] else '✗ FAIL'}")
    print(f"Verification Rate: {result['gating_result']['verification_rate']:.1%}")
    print(f"Confidence: {result['gating_result']['confidence']:.2f}")
    print(f"Recommendation: {result['gating_result']['recommendation']}")
    
    if result['gating_result']['issues']:
        print(f"\nIssues:")
        for issue in result['gating_result']['issues']:
            print(f"  - {issue}")
    
    print("\n" + "="*80)
    print("INVESTIGATION STATISTICS")
    print("="*80)
    stats = result['statistics']
    print(f"Total Moves: {stats['total_moves']}")
    print(f"Duration: {stats['duration_seconds']:.1f} seconds")
    print(f"Average Confidence: {stats['average_confidence']:.1%}")
    
    # Save outputs
    investigation_id = result['investigation_id']
    
    with open(f"/home/ubuntu/rook-core/{investigation_id}_method_card.md", "w") as f:
        f.write(result['method_card'])
    
    with open(f"/home/ubuntu/rook-core/{investigation_id}_moves_ledger.md", "w") as f:
        f.write(result['moves_ledger'])
    
    print("\n" + "="*80)
    print("OUTPUTS SAVED")
    print("="*80)
    print(f"  - {investigation_id}_method_card.md")
    print(f"  - {investigation_id}_moves_ledger.md")
    
    if result['publishable_content']:
        print("\n" + "="*80)
        print("PUBLISHABLE CONTENT")
        print("="*80)
        print(result['publishable_content'])
    else:
        print("\n" + "="*80)
        print("CONTENT BLOCKED BY SAFETY GATE")
        print("="*80)
        print("Content did not meet publication standards.")
