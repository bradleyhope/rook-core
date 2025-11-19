"""
Method Cards System

Core principle: Show your work.

For every investigation, ROOK publishes a "Method Card" that shows:
- What sources were consulted
- How the hypothesis evolved
- What retrieval paths were taken
- What assumptions were made
- What confidence levels were assigned

This creates transparency and allows readers to evaluate ROOK's reasoning.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class StepType(Enum):
    """Types of investigative steps"""
    QUERY = "query"  # Initial query or question
    SEARCH = "search"  # Search for information
    RETRIEVAL = "retrieval"  # Retrieved specific documents/memories
    HYPOTHESIS = "hypothesis"  # Formed a hypothesis
    VERIFICATION = "verification"  # Verified a claim
    SYNTHESIS = "synthesis"  # Synthesized information
    CONCLUSION = "conclusion"  # Drew a conclusion

@dataclass
class InvestigativeStep:
    """A single step in the investigative process"""
    step_type: StepType
    timestamp: datetime
    description: str
    inputs: List[str]  # What went into this step
    outputs: List[str]  # What came out of this step
    sources: List[str]  # Sources consulted
    confidence: float  # Confidence in this step (0-1)
    reasoning: str  # Why this step was taken
    alternatives_considered: List[str] = field(default_factory=list)  # Other paths considered

@dataclass
class MethodCard:
    """
    A Method Card documents the complete investigative process.
    
    It shows:
    - The initial query
    - Each step taken
    - Sources consulted
    - How the hypothesis evolved
    - Final conclusions and confidence
    """
    investigation_id: str
    query: str
    timestamp: datetime
    steps: List[InvestigativeStep]
    sources_consulted: List[Dict]  # All sources used
    final_conclusion: str
    overall_confidence: float
    assumptions: List[str]  # Assumptions made
    limitations: List[str]  # Known limitations
    metadata: Dict = field(default_factory=dict)
    
    def to_markdown(self) -> str:
        """Generate a human-readable Method Card in Markdown format"""
        lines = []
        
        # Header
        lines.append("# Method Card")
        lines.append(f"\n**Investigation ID**: `{self.investigation_id}`")
        lines.append(f"**Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Query**: {self.query}")
        lines.append(f"\n**Overall Confidence**: {self.overall_confidence:.1%}")
        
        # Executive Summary
        lines.append("\n## Executive Summary")
        lines.append(f"\n{self.final_conclusion}")
        
        # Investigative Process
        lines.append("\n## Investigative Process")
        lines.append(f"\nThis investigation involved {len(self.steps)} steps:")
        
        for i, step in enumerate(self.steps, 1):
            lines.append(f"\n### Step {i}: {step.step_type.value.title()}")
            lines.append(f"\n**Time**: {step.timestamp.strftime('%H:%M:%S')}")
            lines.append(f"**Description**: {step.description}")
            lines.append(f"**Confidence**: {step.confidence:.1%}")
            
            if step.inputs:
                lines.append(f"\n**Inputs**:")
                for inp in step.inputs:
                    lines.append(f"- {inp}")
            
            if step.outputs:
                lines.append(f"\n**Outputs**:")
                for out in step.outputs:
                    lines.append(f"- {out}")
            
            if step.sources:
                lines.append(f"\n**Sources Consulted**:")
                for source in step.sources:
                    lines.append(f"- {source}")
            
            lines.append(f"\n**Reasoning**: {step.reasoning}")
            
            if step.alternatives_considered:
                lines.append(f"\n**Alternatives Considered**:")
                for alt in step.alternatives_considered:
                    lines.append(f"- {alt}")
        
        # Sources
        lines.append("\n## Sources Consulted")
        lines.append(f"\nTotal sources: {len(self.sources_consulted)}")
        
        for i, source in enumerate(self.sources_consulted, 1):
            lines.append(f"\n### Source {i}: {source.get('name', 'Unknown')}")
            lines.append(f"**Type**: {source.get('type', 'Unknown')}")
            if source.get('url'):
                lines.append(f"**URL**: {source['url']}")
            if source.get('date'):
                lines.append(f"**Date**: {source['date']}")
            if source.get('confidence'):
                lines.append(f"**Confidence**: {source['confidence']:.1%}")
        
        # Assumptions
        if self.assumptions:
            lines.append("\n## Assumptions")
            for assumption in self.assumptions:
                lines.append(f"- {assumption}")
        
        # Limitations
        if self.limitations:
            lines.append("\n## Limitations")
            for limitation in self.limitations:
                lines.append(f"- {limitation}")
        
        # Metadata
        if self.metadata:
            lines.append("\n## Metadata")
            for key, value in self.metadata.items():
                lines.append(f"- **{key}**: {value}")
        
        # Footer
        lines.append("\n---")
        lines.append("\n*This Method Card was automatically generated to provide transparency into ROOK's investigative process.*")
        
        return "\n".join(lines)
    
    def to_json(self) -> Dict:
        """Generate a machine-readable Method Card in JSON format"""
        return {
            "investigation_id": self.investigation_id,
            "query": self.query,
            "timestamp": self.timestamp.isoformat(),
            "steps": [
                {
                    "step_type": step.step_type.value,
                    "timestamp": step.timestamp.isoformat(),
                    "description": step.description,
                    "inputs": step.inputs,
                    "outputs": step.outputs,
                    "sources": step.sources,
                    "confidence": step.confidence,
                    "reasoning": step.reasoning,
                    "alternatives_considered": step.alternatives_considered
                }
                for step in self.steps
            ],
            "sources_consulted": self.sources_consulted,
            "final_conclusion": self.final_conclusion,
            "overall_confidence": self.overall_confidence,
            "assumptions": self.assumptions,
            "limitations": self.limitations,
            "metadata": self.metadata
        }

class MethodCardBuilder:
    """
    Builder for creating Method Cards during an investigation.
    
    Usage:
        builder = MethodCardBuilder(query="What happened at Wirecard?")
        builder.add_step(...)
        builder.add_step(...)
        card = builder.build()
    """
    
    def __init__(self, query: str, investigation_id: Optional[str] = None):
        self.query = query
        self.investigation_id = investigation_id or self._generate_id()
        self.timestamp = datetime.now()
        self.steps: List[InvestigativeStep] = []
        self.sources_consulted: List[Dict] = []
        self.assumptions: List[str] = []
        self.limitations: List[str] = []
        self.metadata: Dict = {}
    
    def _generate_id(self) -> str:
        """Generate a unique investigation ID"""
        return f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    def add_step(
        self,
        step_type: StepType,
        description: str,
        inputs: List[str] = None,
        outputs: List[str] = None,
        sources: List[str] = None,
        confidence: float = 1.0,
        reasoning: str = "",
        alternatives_considered: List[str] = None
    ) -> 'MethodCardBuilder':
        """Add a step to the investigation"""
        step = InvestigativeStep(
            step_type=step_type,
            timestamp=datetime.now(),
            description=description,
            inputs=inputs or [],
            outputs=outputs or [],
            sources=sources or [],
            confidence=confidence,
            reasoning=reasoning,
            alternatives_considered=alternatives_considered or []
        )
        self.steps.append(step)
        return self
    
    def add_source(
        self,
        name: str,
        source_type: str,
        url: Optional[str] = None,
        date: Optional[str] = None,
        confidence: float = 1.0,
        **kwargs
    ) -> 'MethodCardBuilder':
        """Add a source to the investigation"""
        source = {
            "name": name,
            "type": source_type,
            "url": url,
            "date": date,
            "confidence": confidence,
            **kwargs
        }
        self.sources_consulted.append(source)
        return self
    
    def add_assumption(self, assumption: str) -> 'MethodCardBuilder':
        """Add an assumption made during the investigation"""
        self.assumptions.append(assumption)
        return self
    
    def add_limitation(self, limitation: str) -> 'MethodCardBuilder':
        """Add a known limitation of the investigation"""
        self.limitations.append(limitation)
        return self
    
    def add_metadata(self, key: str, value: any) -> 'MethodCardBuilder':
        """Add metadata to the investigation"""
        self.metadata[key] = value
        return self
    
    def build(self, final_conclusion: str, overall_confidence: float) -> MethodCard:
        """Build the final Method Card"""
        return MethodCard(
            investigation_id=self.investigation_id,
            query=self.query,
            timestamp=self.timestamp,
            steps=self.steps,
            sources_consulted=self.sources_consulted,
            final_conclusion=final_conclusion,
            overall_confidence=overall_confidence,
            assumptions=self.assumptions,
            limitations=self.limitations,
            metadata=self.metadata
        )


# Example usage
if __name__ == "__main__":
    # Create a Method Card for a Wirecard investigation
    builder = MethodCardBuilder(query="What was the Wirecard fraud?")
    
    # Step 1: Initial query
    builder.add_step(
        step_type=StepType.QUERY,
        description="User asked about the Wirecard fraud",
        inputs=["User query: What was the Wirecard fraud?"],
        outputs=["Investigation initiated"],
        confidence=1.0,
        reasoning="Clear investigative query requiring document research"
    )
    
    # Step 2: Search for relevant documents
    builder.add_step(
        step_type=StepType.SEARCH,
        description="Searched knowledge base for Wirecard-related documents",
        inputs=["Query: Wirecard fraud"],
        outputs=["Found 5 relevant documents"],
        sources=["ROOK Knowledge Base"],
        confidence=0.9,
        reasoning="Knowledge base contains comprehensive Wirecard documentation"
    )
    
    # Step 3: Retrieve specific documents
    builder.add_step(
        step_type=StepType.RETRIEVAL,
        description="Retrieved SEC filings and Financial Times investigation",
        inputs=["Document IDs: SEC-10K-2020, FT-Investigation-2020"],
        outputs=["Retrieved 2 primary sources"],
        sources=["SEC Filing 10-K (2020-06-25)", "Financial Times Investigation (2020-06-18)"],
        confidence=0.95,
        reasoning="Primary sources with high credibility"
    )
    
    # Step 4: Form hypothesis
    builder.add_step(
        step_type=StepType.HYPOTHESIS,
        description="Hypothesis: Wirecard committed accounting fraud by reporting non-existent cash",
        inputs=["SEC Filing: €1.9B missing", "FT Investigation: 6 years of reporting"],
        outputs=["Hypothesis: Accounting fraud with missing €1.9B"],
        confidence=0.9,
        reasoning="Multiple independent sources confirm missing funds",
        alternatives_considered=[
            "Accounting error (rejected: too large and systematic)",
            "Temporary liquidity issue (rejected: funds never existed)"
        ]
    )
    
    # Step 5: Verify claims
    builder.add_step(
        step_type=StepType.VERIFICATION,
        description="Verified key claims against primary sources",
        inputs=["Claim: €1.9B missing", "Claim: 6-year investigation"],
        outputs=["Both claims verified with high confidence"],
        sources=["SEC Filing 10-K", "Financial Times"],
        confidence=0.95,
        reasoning="Claims directly supported by primary source documents"
    )
    
    # Step 6: Synthesize findings
    builder.add_step(
        step_type=StepType.SYNTHESIS,
        description="Synthesized findings into coherent narrative",
        inputs=["Verified claims", "Timeline of events", "Key actors"],
        outputs=["Comprehensive fraud narrative"],
        confidence=0.9,
        reasoning="All pieces fit together into consistent story"
    )
    
    # Step 7: Draw conclusion
    builder.add_step(
        step_type=StepType.CONCLUSION,
        description="Concluded that Wirecard committed systematic accounting fraud",
        inputs=["Synthesized narrative", "Verified evidence"],
        outputs=["Final conclusion with 90% confidence"],
        confidence=0.9,
        reasoning="Strong evidence from multiple independent sources"
    )
    
    # Add sources
    builder.add_source(
        name="SEC Filing 10-K",
        source_type="Government Document",
        date="2020-06-25",
        confidence=0.95,
        page=15
    )
    
    builder.add_source(
        name="Financial Times Investigation",
        source_type="Investigative Journalism",
        url="https://ft.com/wirecard",
        date="2020-06-18",
        confidence=0.9,
        author="Dan McCrum"
    )
    
    # Add assumptions
    builder.add_assumption("SEC filings are accurate and trustworthy")
    builder.add_assumption("Financial Times investigation was conducted with journalistic rigor")
    
    # Add limitations
    builder.add_limitation("Did not have access to internal Wirecard documents")
    builder.add_limitation("Relied on publicly available information only")
    builder.add_limitation("Investigation timeline limited to 2019-2020 period")
    
    # Add metadata
    builder.add_metadata("investigator", "ROOK")
    builder.add_metadata("duration_seconds", 45)
    builder.add_metadata("sources_consulted_count", 2)
    
    # Build the Method Card
    card = builder.build(
        final_conclusion="Wirecard AG committed systematic accounting fraud by reporting €1.9 billion in cash that did not exist. The fraud was exposed through a 6-year investigation by the Financial Times and confirmed by SEC filings in June 2020.",
        overall_confidence=0.9
    )
    
    # Print the Method Card
    print(card.to_markdown())
    
    # Save to file
    with open("/home/ubuntu/rook-core/example_method_card.md", "w") as f:
        f.write(card.to_markdown())
    
    print("\n" + "="*80)
    print("Method Card saved to: /home/ubuntu/rook-core/example_method_card.md")
    print("="*80)
