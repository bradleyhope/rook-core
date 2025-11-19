"""
Moves Ledger System

Core principle: Make ROOK's reasoning visible in real-time.

The Moves Ledger logs every action ROOK takes during an investigation:
- Every search performed
- Every document retrieved
- Every hypothesis formed
- Every claim verified
- Every decision made

This creates a complete audit trail that can be:
- Reviewed for quality control
- Analyzed for patterns
- Used to improve ROOK's reasoning
- Shared with readers for transparency
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class MoveType(Enum):
    """Types of moves ROOK can make"""
    SEARCH = "search"  # Searched for information
    RETRIEVE = "retrieve"  # Retrieved a document/memory
    HYPOTHESIZE = "hypothesize"  # Formed a hypothesis
    VERIFY = "verify"  # Verified a claim
    CITE = "cite"  # Cited a source
    QUESTION = "question"  # Asked a question
    DECIDE = "decide"  # Made a decision
    REFLECT = "reflect"  # Reflected on progress
    ERROR = "error"  # Encountered an error

@dataclass
class Move:
    """A single move in the investigation"""
    move_id: str
    move_type: MoveType
    timestamp: datetime
    description: str
    inputs: Dict[str, Any]  # What went into this move
    outputs: Dict[str, Any]  # What came out of this move
    confidence: float  # Confidence in this move (0-1)
    reasoning: str  # Why this move was made
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert move to dictionary"""
        return {
            "move_id": self.move_id,
            "move_type": self.move_type.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "metadata": self.metadata
        }
    
    def to_markdown(self) -> str:
        """Convert move to markdown for display"""
        lines = []
        lines.append(f"### {self.move_type.value.upper()}: {self.description}")
        lines.append(f"**Time**: {self.timestamp.strftime('%H:%M:%S')}")
        lines.append(f"**Confidence**: {self.confidence:.1%}")
        lines.append(f"**Reasoning**: {self.reasoning}")
        
        if self.inputs:
            lines.append(f"\n**Inputs**:")
            for key, value in self.inputs.items():
                lines.append(f"- {key}: {value}")
        
        if self.outputs:
            lines.append(f"\n**Outputs**:")
            for key, value in self.outputs.items():
                lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)

class MovesLedger:
    """
    The Moves Ledger tracks all moves during an investigation.
    
    It provides:
    - Real-time logging of actions
    - Complete audit trail
    - Ability to replay investigations
    - Pattern analysis across investigations
    """
    
    def __init__(self, investigation_id: str):
        self.investigation_id = investigation_id
        self.moves: List[Move] = []
        self.start_time = datetime.now()
        self.move_counter = 0
    
    def log_move(
        self,
        move_type: MoveType,
        description: str,
        inputs: Dict[str, Any] = None,
        outputs: Dict[str, Any] = None,
        confidence: float = 1.0,
        reasoning: str = "",
        metadata: Dict[str, Any] = None
    ) -> Move:
        """Log a move to the ledger"""
        self.move_counter += 1
        move_id = f"{self.investigation_id}-M{self.move_counter:03d}"
        
        move = Move(
            move_id=move_id,
            move_type=move_type,
            timestamp=datetime.now(),
            description=description,
            inputs=inputs or {},
            outputs=outputs or {},
            confidence=confidence,
            reasoning=reasoning,
            metadata=metadata or {}
        )
        
        self.moves.append(move)
        return move
    
    def get_moves_by_type(self, move_type: MoveType) -> List[Move]:
        """Get all moves of a specific type"""
        return [m for m in self.moves if m.move_type == move_type]
    
    def get_recent_moves(self, count: int = 10) -> List[Move]:
        """Get the most recent moves"""
        return self.moves[-count:]
    
    def get_move_by_id(self, move_id: str) -> Optional[Move]:
        """Get a specific move by ID"""
        for move in self.moves:
            if move.move_id == move_id:
                return move
        return None
    
    def get_statistics(self) -> Dict:
        """Get statistics about the investigation"""
        move_types = {}
        for move in self.moves:
            move_type = move.move_type.value
            move_types[move_type] = move_types.get(move_type, 0) + 1
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        avg_confidence = sum(m.confidence for m in self.moves) / len(self.moves) if self.moves else 0
        
        return {
            "investigation_id": self.investigation_id,
            "total_moves": len(self.moves),
            "move_types": move_types,
            "duration_seconds": total_duration,
            "average_confidence": avg_confidence,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat()
        }
    
    def to_markdown(self) -> str:
        """Generate a markdown report of all moves"""
        lines = []
        
        # Header
        lines.append("# Moves Ledger")
        lines.append(f"\n**Investigation ID**: `{self.investigation_id}`")
        lines.append(f"**Start Time**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Moves**: {len(self.moves)}")
        
        # Statistics
        stats = self.get_statistics()
        lines.append(f"\n## Statistics")
        lines.append(f"- **Duration**: {stats['duration_seconds']:.1f} seconds")
        lines.append(f"- **Average Confidence**: {stats['average_confidence']:.1%}")
        lines.append(f"\n**Move Types**:")
        for move_type, count in stats['move_types'].items():
            lines.append(f"- {move_type}: {count}")
        
        # All moves
        lines.append(f"\n## All Moves")
        for i, move in enumerate(self.moves, 1):
            lines.append(f"\n## Move {i}")
            lines.append(move.to_markdown())
        
        # Footer
        lines.append("\n---")
        lines.append("\n*This Moves Ledger was automatically generated to provide visibility into ROOK's reasoning process.*")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Generate a JSON export of all moves"""
        data = {
            "investigation_id": self.investigation_id,
            "start_time": self.start_time.isoformat(),
            "statistics": self.get_statistics(),
            "moves": [move.to_dict() for move in self.moves]
        }
        return json.dumps(data, indent=2)
    
    def replay(self, speed: float = 1.0):
        """
        Replay the investigation in real-time (for debugging/review).
        
        Args:
            speed: Playback speed multiplier (1.0 = real-time, 2.0 = 2x speed)
        """
        import time
        
        print(f"Replaying investigation: {self.investigation_id}")
        print(f"Speed: {speed}x")
        print("="*80)
        
        last_time = self.start_time
        for i, move in enumerate(self.moves, 1):
            # Calculate time since last move
            time_diff = (move.timestamp - last_time).total_seconds()
            sleep_time = time_diff / speed
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            # Display move
            print(f"\n[Move {i}/{len(self.moves)}] {move.move_type.value.upper()}")
            print(f"Time: {move.timestamp.strftime('%H:%M:%S')}")
            print(f"Description: {move.description}")
            print(f"Confidence: {move.confidence:.1%}")
            print(f"Reasoning: {move.reasoning}")
            
            last_time = move.timestamp
        
        print("\n" + "="*80)
        print("Replay complete")


# Example usage
if __name__ == "__main__":
    # Create a Moves Ledger for a Wirecard investigation
    ledger = MovesLedger(investigation_id="INV-20251112-WIRECARD")
    
    # Move 1: Initial query
    ledger.log_move(
        move_type=MoveType.QUESTION,
        description="User asked: What was the Wirecard fraud?",
        inputs={"query": "What was the Wirecard fraud?"},
        outputs={"investigation_initiated": True},
        confidence=1.0,
        reasoning="Clear investigative query requiring document research"
    )
    
    # Move 2: Search knowledge base
    ledger.log_move(
        move_type=MoveType.SEARCH,
        description="Searched knowledge base for 'Wirecard fraud'",
        inputs={"search_query": "Wirecard fraud", "search_type": "semantic"},
        outputs={"results_found": 5, "top_result_score": 0.92},
        confidence=0.9,
        reasoning="Knowledge base likely contains relevant Wirecard documentation"
    )
    
    # Move 3: Retrieve top documents
    ledger.log_move(
        move_type=MoveType.RETRIEVE,
        description="Retrieved SEC Filing 10-K and FT Investigation",
        inputs={"document_ids": ["SEC-10K-2020", "FT-INV-2020"]},
        outputs={
            "documents_retrieved": 2,
            "total_pages": 250,
            "sources": ["SEC", "Financial Times"]
        },
        confidence=0.95,
        reasoning="Primary sources with high credibility scores"
    )
    
    # Move 4: Form hypothesis
    ledger.log_move(
        move_type=MoveType.HYPOTHESIZE,
        description="Hypothesis: Wirecard committed accounting fraud",
        inputs={
            "evidence": ["€1.9B missing cash", "6-year FT investigation"],
            "pattern": "Missing funds + long investigation = fraud"
        },
        outputs={
            "hypothesis": "Systematic accounting fraud",
            "confidence": 0.9
        },
        confidence=0.9,
        reasoning="Multiple independent sources point to fraud, not error"
    )
    
    # Move 5: Verify key claim
    ledger.log_move(
        move_type=MoveType.VERIFY,
        description="Verified claim: €1.9B in cash did not exist",
        inputs={
            "claim": "€1.9B in cash did not exist",
            "sources_to_check": ["SEC-10K-2020", "FT-INV-2020"]
        },
        outputs={
            "verified": True,
            "supporting_sources": 2,
            "confidence": 0.95
        },
        confidence=0.95,
        reasoning="Claim directly stated in SEC filing and confirmed by FT"
    )
    
    # Move 6: Cite sources
    ledger.log_move(
        move_type=MoveType.CITE,
        description="Cited SEC Filing 10-K as primary source",
        inputs={"source_id": "SEC-10K-2020"},
        outputs={
            "citation": "[SEC Filing 10-K, p.15, 2020-06-25]",
            "citation_type": "primary_source"
        },
        confidence=0.95,
        reasoning="Government document with high reliability"
    )
    
    # Move 7: Reflect on progress
    ledger.log_move(
        move_type=MoveType.REFLECT,
        description="Reflected on investigation progress",
        inputs={
            "moves_so_far": 6,
            "claims_verified": 1,
            "sources_consulted": 2
        },
        outputs={
            "assessment": "Strong evidence for fraud hypothesis",
            "next_steps": ["Verify additional claims", "Synthesize findings"]
        },
        confidence=0.9,
        reasoning="Have strong primary sources, ready to synthesize"
    )
    
    # Move 8: Make decision
    ledger.log_move(
        move_type=MoveType.DECIDE,
        description="Decision: Proceed with fraud conclusion",
        inputs={
            "hypothesis_confidence": 0.9,
            "verified_claims": 1,
            "source_quality": "high"
        },
        outputs={
            "decision": "Conclude systematic accounting fraud",
            "confidence": 0.9
        },
        confidence=0.9,
        reasoning="Evidence exceeds threshold for high-confidence conclusion"
    )
    
    # Print the ledger
    print(ledger.to_markdown())
    
    # Save to file
    with open("/home/ubuntu/rook-core/example_moves_ledger.md", "w") as f:
        f.write(ledger.to_markdown())
    
    with open("/home/ubuntu/rook-core/example_moves_ledger.json", "w") as f:
        f.write(ledger.to_json())
    
    print("\n" + "="*80)
    print("Moves Ledger saved to:")
    print("  - /home/ubuntu/rook-core/example_moves_ledger.md")
    print("  - /home/ubuntu/rook-core/example_moves_ledger.json")
    print("="*80)
    
    # Print statistics
    print("\n" + "="*80)
    print("INVESTIGATION STATISTICS")
    print("="*80)
    stats = ledger.get_statistics()
    print(json.dumps(stats, indent=2))
