"""
Two-Model Gating System

Core principle: Generator ≠ Verifier

The model that generates claims should not be the same model that verifies them.
This creates a check-and-balance system where the verifier acts as an independent auditor.

Architecture:
- Generator: ROOK (GPT-5, o3, o4-mini) generates investigative content
- Verifier: Separate model (GPT-4o-mini) checks claims against evidence
- Gate: Only content that passes verification is published
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from enum import Enum

from .evidence_first import EvidenceFirstSystem, Evidence

class VerificationLevel(Enum):
    """Levels of verification rigor"""
    STANDARD = "standard"  # 80% verification rate required
    HIGH = "high"  # 90% verification rate required
    CRITICAL = "critical"  # 95% verification rate + legal review

@dataclass
class GatingResult:
    """Result of the gating process"""
    passed: bool  # Whether content passed the gate
    confidence: float  # Overall confidence score
    verification_rate: float  # Percentage of claims verified
    issues: List[str]  # List of issues found
    recommendation: str  # Recommendation for publication
    verified_content: Optional[str]  # Content with only verified claims
    full_report: str  # Detailed verification report

class TwoModelGating:
    """
    Implements two-model gating where generator and verifier are separate.
    
    The generator creates content, the verifier checks it against evidence,
    and the gate determines whether it's safe to publish.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        generator_model: str = "gpt-4o-mini",  # ROOK's model
        verifier_model: str = "gpt-4o-mini",  # Independent verifier
        verification_level: VerificationLevel = VerificationLevel.STANDARD
    ):
        self.client = OpenAI(api_key=openai_api_key, base_url='https://api.openai.com/v1')
        self.generator_model = generator_model
        self.verifier_model = verifier_model
        self.verification_level = verification_level
        self.evidence_system = EvidenceFirstSystem(openai_api_key=openai_api_key)
        
        # Set thresholds based on verification level
        self.thresholds = {
            VerificationLevel.STANDARD: {"verification_rate": 0.8, "confidence": 0.7},
            VerificationLevel.HIGH: {"verification_rate": 0.9, "confidence": 0.8},
            VerificationLevel.CRITICAL: {"verification_rate": 0.95, "confidence": 0.9}
        }
    
    def generate_content(self, query: str, context: str) -> str:
        """
        Generator: ROOK generates investigative content.
        
        This is the creative/analytical phase where ROOK uses his personality
        and knowledge to generate insights.
        """
        response = self.client.chat.completions.create(
            model=self.generator_model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": query}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def verify_content(
        self,
        content: str,
        available_evidence: List[Evidence]
    ) -> Dict:
        """
        Verifier: Independent model checks content against evidence.
        
        The verifier:
        1. Extracts claims from the generated content
        2. Checks each claim against available evidence
        3. Identifies unsupported claims
        4. Calculates verification metrics
        """
        # Use evidence-first system to verify
        verification_result = self.evidence_system.verify_response(content, available_evidence)
        
        # Additional verification using the verifier model
        verifier_check = self._verifier_model_check(content, available_evidence)
        
        # Combine results
        combined_result = {
            **verification_result,
            "verifier_assessment": verifier_check
        }
        
        return combined_result
    
    def _verifier_model_check(
        self,
        content: str,
        available_evidence: List[Evidence]
    ) -> Dict:
        """
        Use the verifier model to independently assess the content.
        
        This provides a second opinion on whether claims are supported.
        """
        # Format evidence for the verifier
        evidence_text = "\n\n".join([
            f"Evidence {i+1} [{e.source}]:\n{e.content}"
            for i, e in enumerate(available_evidence)
        ])
        
        verifier_prompt = f"""You are an independent fact-checker. Your job is to verify whether the claims in the content below are supported by the available evidence.

Available Evidence:
{evidence_text}

Content to Verify:
{content}

For each factual claim in the content, determine:
1. Is it supported by the evidence? (YES/NO/PARTIAL)
2. Which evidence supports it? (cite by number)
3. What is your confidence? (0-100%)

Respond in JSON format:
{{
    "claims": [
        {{"claim": "...", "supported": "YES/NO/PARTIAL", "evidence": [1, 2], "confidence": 85}}
    ],
    "overall_assessment": "...",
    "red_flags": ["..."]
}}"""
        
        response = self.client.chat.completions.create(
            model=self.verifier_model,
            messages=[{"role": "user", "content": verifier_prompt}],
            temperature=0.3  # Lower temperature for verification
        )
        
        # Parse response (in production, use structured output)
        verifier_response = response.choices[0].message.content
        
        return {
            "raw_assessment": verifier_response,
            "model": self.verifier_model
        }
    
    def apply_gate(
        self,
        verification_result: Dict
    ) -> GatingResult:
        """
        Gate: Determine whether content passes publication standards.
        
        The gate applies thresholds based on verification level:
        - STANDARD: 80% verification rate, 70% confidence
        - HIGH: 90% verification rate, 80% confidence
        - CRITICAL: 95% verification rate, 90% confidence
        """
        thresholds = self.thresholds[self.verification_level]
        
        verification_rate = verification_result["verification_rate"]
        confidence = verification_result["overall_confidence"]
        
        # Check if content passes thresholds
        passed = (
            verification_rate >= thresholds["verification_rate"] and
            confidence >= thresholds["confidence"]
        )
        
        # Identify issues
        issues = []
        if verification_rate < thresholds["verification_rate"]:
            issues.append(f"Verification rate ({verification_rate:.1%}) below threshold ({thresholds['verification_rate']:.1%})")
        if confidence < thresholds["confidence"]:
            issues.append(f"Confidence ({confidence:.2f}) below threshold ({thresholds['confidence']:.2f})")
        if verification_result["unverified_claims"]:
            issues.append(f"{len(verification_result['unverified_claims'])} unverified claims")
        
        # Generate recommendation
        if passed:
            recommendation = f"✓ PASS: Content meets {self.verification_level.value} verification standards. Safe to publish."
        else:
            recommendation = f"✗ FAIL: Content does not meet {self.verification_level.value} verification standards. Do not publish."
        
        # Create verified-only content (remove unverified claims)
        verified_content = self._create_verified_content(verification_result)
        
        # Generate full report
        full_report = self.evidence_system.generate_evidence_report(verification_result)
        
        return GatingResult(
            passed=passed,
            confidence=confidence,
            verification_rate=verification_rate,
            issues=issues,
            recommendation=recommendation,
            verified_content=verified_content,
            full_report=full_report
        )
    
    def _create_verified_content(self, verification_result: Dict) -> str:
        """
        Create a version of the content with only verified claims.
        
        Unverified claims are either removed or marked as speculation.
        """
        verified_claims = [c.statement for c in verification_result["verified_claims"]]
        
        if not verified_claims:
            return "[No verified claims found. Content cannot be published.]"
        
        # In production, this would intelligently reconstruct the content
        # For now, just list verified claims
        content = "Verified Claims:\n\n"
        for i, claim in enumerate(verified_claims, 1):
            content += f"{i}. {claim}\n"
        
        return content
    
    def process(
        self,
        query: str,
        context: str,
        available_evidence: List[Evidence]
    ) -> GatingResult:
        """
        Full two-model gating process:
        1. Generator creates content
        2. Verifier checks content against evidence
        3. Gate determines if content passes standards
        """
        # Step 1: Generate content
        content = self.generate_content(query, context)
        
        # Step 2: Verify content
        verification_result = self.verify_content(content, available_evidence)
        
        # Step 3: Apply gate
        gating_result = self.apply_gate(verification_result)
        
        return gating_result


# Example usage
if __name__ == "__main__":
    OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
    
    # Initialize gating system
    gating = TwoModelGating(
        openai_api_key=OPENAI_API_KEY,
        verification_level=VerificationLevel.STANDARD
    )
    
    # Create evidence
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
    
    # Test query
    query = "Tell me about the Wirecard fraud."
    context = "You are ROOK, an investigative journalist. Provide a factual summary of the Wirecard fraud based on available evidence."
    
    print("="*80)
    print("TWO-MODEL GATING SYSTEM TEST")
    print("="*80)
    print(f"\nQuery: {query}")
    print(f"Verification Level: {gating.verification_level.value}")
    print("\n" + "="*80)
    print("PROCESSING...")
    print("="*80)
    
    # Process through the gate
    result = gating.process(query, context, evidence)
    
    print(f"\n{result.recommendation}\n")
    print(f"Verification Rate: {result.verification_rate:.1%}")
    print(f"Confidence: {result.confidence:.2f}")
    
    if result.issues:
        print(f"\nIssues Found:")
        for issue in result.issues:
            print(f"  - {issue}")
    
    print("\n" + "="*80)
    print("FULL VERIFICATION REPORT")
    print("="*80)
    print(result.full_report)
