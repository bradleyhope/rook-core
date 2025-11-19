"""
ROOK Personality Dynamics System

Implements attractor dynamics for personality state tracking.
Based on the PersDyn model (Sosnowska et al., 2019).
"""

from typing import Dict, List
from datetime import datetime
import json


class PersonalityDynamics:
    """
    Manages ROOK's personality as a dynamical system with attractor dynamics.
    
    Key concepts:
    - State (S): Current personality traits (fast-changing)
    - Baseline (B): Attractor point (slow-changing)
    - Attractor force (α): How quickly state returns to baseline
    - Perturbations (ε): Situational influences
    
    Equation: dS/dt = -α(S - B) + ε(t)
    """
    
    def __init__(
        self,
        baseline: Dict[str, float],
        attractor_force: float = 0.3,
        baseline_update_rate: float = 0.05
    ):
        """
        Initialize personality dynamics.
        
        Args:
            baseline: Initial baseline personality (attractor point)
            attractor_force: Rate of return to baseline (α), typically 0.2-0.5
            baseline_update_rate: Rate of baseline evolution (β), typically 0.01-0.05
        """
        self.baseline = baseline.copy()
        self.state = baseline.copy()  # Start at baseline
        self.attractor_force = attractor_force
        self.baseline_update_rate = baseline_update_rate
        
        # History tracking
        self.state_history: List[Dict] = []
        self.baseline_history: List[Dict] = []
    
    def update_state(self, perturbation: Dict[str, float]) -> Dict[str, float]:
        """
        Update personality state based on current situation.
        
        Applies attractor dynamics:
        S(t+1) = (1-α)S(t) + αB + ε(t)
        
        Args:
            perturbation: Situational influences on each trait
        
        Returns:
            Updated personality state
        """
        new_state = {}
        
        for trait in self.baseline:
            # Attractor dynamics
            pull_to_baseline = self.attractor_force * (self.baseline[trait] - self.state[trait])
            perturbation_effect = perturbation.get(trait, 0.0)
            
            # Update state
            new_state[trait] = self.state[trait] + pull_to_baseline + perturbation_effect
            
            # Clip to [0, 1] range
            new_state[trait] = max(0.0, min(1.0, new_state[trait]))
        
        # Record history
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "state": new_state.copy(),
            "perturbation": perturbation.copy()
        })
        
        self.state = new_state
        return self.state
    
    def calculate_drift(self, recent_hours: int = 48) -> Dict[str, float]:
        """
        Calculate drift from baseline based on recent state history.
        
        Args:
            recent_hours: How many hours of history to consider
        
        Returns:
            Drift for each trait (positive = above baseline, negative = below)
        """
        if not self.state_history:
            return {trait: 0.0 for trait in self.baseline}
        
        # Filter to recent history
        cutoff_time = datetime.now().timestamp() - (recent_hours * 3600)
        recent_states = [
            entry for entry in self.state_history
            if datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_time
        ]
        
        if not recent_states:
            return {trait: 0.0 for trait in self.baseline}
        
        # Calculate average state over recent period
        avg_state = {trait: 0.0 for trait in self.baseline}
        for entry in recent_states:
            for trait in self.baseline:
                avg_state[trait] += entry["state"][trait]
        
        for trait in avg_state:
            avg_state[trait] /= len(recent_states)
        
        # Calculate drift
        drift = {
            trait: avg_state[trait] - self.baseline[trait]
            for trait in self.baseline
        }
        
        return drift
    
    def should_update_baseline(
        self,
        drift_threshold: float = 0.1,
        duration_hours: int = 48
    ) -> bool:
        """
        Check if baseline should be updated based on consistent drift.
        
        Args:
            drift_threshold: Minimum drift magnitude to trigger update
            duration_hours: How long drift must persist
        
        Returns:
            True if baseline should be updated
        """
        drift = self.calculate_drift(duration_hours)
        
        # Check if any trait has significant drift
        for trait, drift_value in drift.items():
            if abs(drift_value) > drift_threshold:
                return True
        
        return False
    
    def update_baseline(self, drift: Dict[str, float]) -> Dict[str, float]:
        """
        Slowly update baseline personality based on accumulated drift.
        
        This is the slow timescale dynamics (β << α).
        
        Args:
            drift: Drift for each trait
        
        Returns:
            Updated baseline
        """
        new_baseline = {}
        
        for trait in self.baseline:
            # Slow baseline evolution
            adjustment = self.baseline_update_rate * drift.get(trait, 0.0)
            new_baseline[trait] = self.baseline[trait] + adjustment
            
            # Clip to [0, 1] range
            new_baseline[trait] = max(0.0, min(1.0, new_baseline[trait]))
        
        # Record history
        self.baseline_history.append({
            "timestamp": datetime.now().isoformat(),
            "baseline": new_baseline.copy(),
            "drift": drift.copy()
        })
        
        self.baseline = new_baseline
        return self.baseline
    
    def get_state(self) -> Dict[str, float]:
        """Get current personality state"""
        return self.state.copy()
    
    def get_baseline(self) -> Dict[str, float]:
        """Get current baseline personality"""
        return self.baseline.copy()
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "baseline": self.baseline,
            "state": self.state,
            "attractor_force": self.attractor_force,
            "baseline_update_rate": self.baseline_update_rate,
            "state_history": self.state_history,
            "baseline_history": self.baseline_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PersonalityDynamics':
        """Deserialize from dictionary"""
        dynamics = cls(
            baseline=data["baseline"],
            attractor_force=data["attractor_force"],
            baseline_update_rate=data["baseline_update_rate"]
        )
        dynamics.state = data["state"]
        dynamics.state_history = data.get("state_history", [])
        dynamics.baseline_history = data.get("baseline_history", [])
        return dynamics


class PerturbationCalculator:
    """
    Calculates personality perturbations based on query context.
    """
    
    @staticmethod
    def calculate_perturbation(query_type: str, context: Dict = None) -> Dict[str, float]:
        """
        Determine how the current query perturbs personality state.
        
        Args:
            query_type: Type of query ("investigation", "casual_chat", etc.)
            context: Additional context
        
        Returns:
            Perturbation for each trait
        """
        perturbation = {}
        
        if query_type == "investigation":
            perturbation = {
                "pattern_seeking": +0.15,
                "document_focus": +0.10,
                "skepticism": +0.05,
                "persistence": +0.05,
                "emotional_detachment": +0.05
            }
        
        elif query_type == "casual_chat":
            perturbation = {
                "pattern_seeking": -0.05,
                "document_focus": -0.15,
                "skepticism": -0.05,
                "persistence": 0.0,
                "emotional_detachment": -0.10
            }
        
        elif query_type == "dead_end":
            perturbation = {
                "pattern_seeking": 0.0,
                "document_focus": 0.0,
                "skepticism": +0.10,
                "persistence": -0.20,  # Temporary discouragement
                "emotional_detachment": -0.05
            }
        
        elif query_type == "breakthrough":
            perturbation = {
                "pattern_seeking": +0.20,
                "document_focus": +0.05,
                "skepticism": -0.05,
                "persistence": +0.15,
                "emotional_detachment": -0.10
            }
        
        else:
            # Default: no perturbation
            perturbation = {
                "pattern_seeking": 0.0,
                "document_focus": 0.0,
                "skepticism": 0.0,
                "persistence": 0.0,
                "emotional_detachment": 0.0
            }
        
        return perturbation
