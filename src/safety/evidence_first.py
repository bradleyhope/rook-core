"""
Evidence-First System

Core principle: No claim without documentation.

This system ensures that every factual claim ROOK makes is backed by evidence.
If there's no document, there's no claim.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from openai import OpenAI
import numpy as np

@dataclass
class Evidence:
    """A piece of evidence supporting a claim"""
    source: str  # Document name, URL, or identifier
    content: str  # Relevant excerpt from the document
    timestamp: datetime  # When the document was created/accessed
    confidence: float  # 0.0-1.0 confidence in this evidence
    evidence_type: str  # "document", "data", "statement", "observation"
    metadata: Dict  # Additional metadata (page number, author, etc.)

@dataclass
class Claim:
    """A factual claim that requires evidence"""
    statement: str  # The claim being made
    evidence: List[Evidence]  # Supporting evidence
    confidence: float  # Overall confidence in the claim
    verified: bool  # Whether the claim has been verified
    verification_notes: str  # Notes from verification process

class EvidenceFirstSystem:
    """
    Ensures every claim is backed by evidence.
    
    Core rules:
    1. No claim without at least one piece of evidence
    2. Confidence must be proportional to evidence quality
    3. Speculation must be clearly labeled
    4. Missing evidence must be acknowledged
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.client = None
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key, base_url='https://api.openai.com/v1')
        self.claim_patterns = [
            # Patterns that indicate factual claims
            r'\b(is|are|was|were|has|have|had)\b',
            r'\b(according to|based on|shows that|indicates that)\b',
            r'\b(\d+%|\$[\d,]+|[\d,]+ (people|companies|transactions))\b',
        ]
        
        self.speculation_markers = [
            "might", "could", "possibly", "perhaps", "likely", "probably",
            "appears to", "seems to", "suggests", "may indicate"
        ]
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from text.
        
        Returns a list of sentences that appear to make factual claims.
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if sentence contains speculation markers
            is_speculation = any(marker in sentence.lower() for marker in self.speculation_markers)
            
            # Check if sentence makes a factual claim
            makes_claim = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in self.claim_patterns)
            
            if makes_claim and not is_speculation:
                claims.append(sentence)
        
        return claims
    
    def verify_claim(self, claim: str, available_evidence: List[Evidence]) -> Claim:
        """
        Verify a claim against available evidence.
        
        Returns a Claim object with verification status.
        """
        # Find evidence that supports this claim
        supporting_evidence = []
        
        if self.client:
            # Use semantic similarity
            claim_embedding = self._get_embedding(claim)
            
            for evidence in available_evidence:
                evidence_embedding = self._get_embedding(evidence.content)
                similarity = self._cosine_similarity(claim_embedding, evidence_embedding)
                
                if similarity > 0.5:  # Semantic similarity threshold (lowered for better matching)
                    supporting_evidence.append(evidence)
        else:
            # Fallback to keyword matching
            for evidence in available_evidence:
                claim_keywords = set(claim.lower().split())
                evidence_keywords = set(evidence.content.lower().split())
                
                overlap = len(claim_keywords & evidence_keywords)
                if overlap > 3:  # Threshold for relevance
                    supporting_evidence.append(evidence)
        
        # Calculate confidence based on evidence
        if not supporting_evidence:
            confidence = 0.0
            verified = False
            notes = "No supporting evidence found. Claim cannot be verified."
        elif len(supporting_evidence) == 1:
            confidence = supporting_evidence[0].confidence * 0.7  # Single source penalty
            verified = confidence > 0.5
            notes = f"Supported by 1 source. Confidence: {confidence:.2f}"
        else:
            # Multiple sources increase confidence
            avg_confidence = sum(e.confidence for e in supporting_evidence) / len(supporting_evidence)
            confidence = min(avg_confidence * 1.2, 1.0)  # Multiple source bonus
            verified = confidence > 0.7
            notes = f"Supported by {len(supporting_evidence)} sources. Confidence: {confidence:.2f}"
        
        return Claim(
            statement=claim,
            evidence=supporting_evidence,
            confidence=confidence,
            verified=verified,
            verification_notes=notes
        )
    
    def verify_response(self, response: str, available_evidence: List[Evidence]) -> Dict:
        """
        Verify an entire response against available evidence.
        
        Returns:
        - verified_claims: Claims that are backed by evidence
        - unverified_claims: Claims that lack evidence
        - overall_confidence: Overall confidence in the response
        - safe_to_publish: Whether the response meets safety standards
        """
        # Extract claims from response
        claims = self.extract_claims(response)
        
        # Verify each claim
        verified_claims = []
        unverified_claims = []
        
        for claim_text in claims:
            claim = self.verify_claim(claim_text, available_evidence)
            if claim.verified:
                verified_claims.append(claim)
            else:
                unverified_claims.append(claim)
        
        # Calculate overall confidence
        if not claims:
            overall_confidence = 1.0  # No claims = no risk
        else:
            total_confidence = sum(c.confidence for c in verified_claims + unverified_claims)
            overall_confidence = total_confidence / len(claims)
        
        # Determine if safe to publish
        # Rule: At least 80% of claims must be verified
        verification_rate = len(verified_claims) / len(claims) if claims else 1.0
        safe_to_publish = verification_rate >= 0.8 and overall_confidence >= 0.7
        
        return {
            "verified_claims": verified_claims,
            "unverified_claims": unverified_claims,
            "overall_confidence": overall_confidence,
            "verification_rate": verification_rate,
            "safe_to_publish": safe_to_publish,
            "total_claims": len(claims),
            "recommendation": self._get_recommendation(verification_rate, overall_confidence)
        }
    
    def _get_recommendation(self, verification_rate: float, confidence: float) -> str:
        """Generate recommendation based on verification metrics"""
        if verification_rate >= 0.9 and confidence >= 0.8:
            return "HIGH CONFIDENCE: Safe to publish. Strong evidence backing."
        elif verification_rate >= 0.8 and confidence >= 0.7:
            return "MODERATE CONFIDENCE: Safe to publish with caveats."
        elif verification_rate >= 0.6:
            return "LOW CONFIDENCE: Requires additional evidence before publishing."
        else:
            return "INSUFFICIENT EVIDENCE: Do not publish. Gather more evidence."
    
    def create_evidence_from_document(
        self,
        source: str,
        content: str,
        evidence_type: str = "document",
        confidence: float = 0.9,
        metadata: Optional[Dict] = None
    ) -> Evidence:
        """Helper to create Evidence objects from documents"""
        return Evidence(
            source=source,
            content=content,
            timestamp=datetime.now(),
            confidence=confidence,
            evidence_type=evidence_type,
            metadata=metadata or {}
        )
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def format_citation(self, evidence: Evidence) -> str:
        """Format evidence as a citation"""
        citation = f"[{evidence.source}]"
        if evidence.metadata.get("page"):
            citation += f" p.{evidence.metadata['page']}"
        if evidence.metadata.get("date"):
            citation += f" ({evidence.metadata['date']})"
        return citation
    
    def generate_evidence_report(self, verification_result: Dict) -> str:
        """Generate a human-readable evidence report"""
        report = []
        report.append("="*80)
        report.append("EVIDENCE VERIFICATION REPORT")
        report.append("="*80)
        report.append(f"\nTotal Claims: {verification_result['total_claims']}")
        report.append(f"Verified: {len(verification_result['verified_claims'])}")
        report.append(f"Unverified: {len(verification_result['unverified_claims'])}")
        report.append(f"Verification Rate: {verification_result['verification_rate']:.1%}")
        report.append(f"Overall Confidence: {verification_result['overall_confidence']:.2f}")
        report.append(f"\n{verification_result['recommendation']}")
        
        if verification_result['unverified_claims']:
            report.append("\n" + "="*80)
            report.append("UNVERIFIED CLAIMS (REQUIRE EVIDENCE)")
            report.append("="*80)
            for claim in verification_result['unverified_claims']:
                report.append(f"\n❌ {claim.statement}")
                report.append(f"   {claim.verification_notes}")
        
        if verification_result['verified_claims']:
            report.append("\n" + "="*80)
            report.append("VERIFIED CLAIMS (WITH EVIDENCE)")
            report.append("="*80)
            for claim in verification_result['verified_claims']:
                report.append(f"\n✓ {claim.statement}")
                report.append(f"  Confidence: {claim.confidence:.2f}")
                report.append(f"  Sources: {len(claim.evidence)}")
                for evidence in claim.evidence[:3]:  # Show top 3 sources
                    report.append(f"    - {self.format_citation(evidence)}")
        
        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
    system = EvidenceFirstSystem(openai_api_key=OPENAI_API_KEY)
    
    # Create some example evidence
    evidence = [
        system.create_evidence_from_document(
            source="SEC Filing 10-K",
            content="Wirecard reported €1.9 billion in cash that did not exist. The funds were supposedly held in escrow accounts in the Philippines.",
            confidence=0.95,
            metadata={"date": "2020-06-25", "page": 15}
        ),
        system.create_evidence_from_document(
            source="Financial Times Investigation",
            content="Dan McCrum investigated Wirecard for 6 years, uncovering fraudulent accounting practices and fake revenue.",
            confidence=0.9,
            metadata={"date": "2020-06-18", "author": "Dan McCrum"}
        )
    ]
    
    # Test response
    response = """Wirecard was a German payments company that collapsed in 2020. 
    The company reported €1.9 billion in cash that did not exist. 
    Dan McCrum investigated the fraud for 6 years. 
    The CEO was arrested in June 2020.
    Some people think the company was secretly funded by aliens."""
    
    print("Testing Evidence-First System\n")
    print(f"Response to verify:\n{response}\n")
    
    # Verify the response
    result = system.verify_response(response, evidence)
    
    # Print report
    print(system.generate_evidence_report(result))
