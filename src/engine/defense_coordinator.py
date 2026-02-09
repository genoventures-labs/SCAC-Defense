"""
Defense Coordinator

Orchestrates multiple defense mechanisms with:
- State management across all active defenses
- Defense compatibility checking
- Resource allocation and load balancing
- Effectiveness tracking and learning
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class DefenseStatus(Enum):
    """Status of a defense mechanism."""
    INACTIVE = "inactive"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    FAILED = "failed"


@dataclass
class DefenseState:
    """State of an active defense."""
    defense_name: str
    status: DefenseStatus
    activated_at: datetime
    parameters: Dict[str, Any]
    target_actor: str
    effectiveness_score: float = 0.0
    events_processed: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Effectiveness metrics
    attacker_aborted: bool = False
    time_to_abort: Optional[float] = None
    resources_consumed: float = 0.0
    false_positive: bool = False


@dataclass
class DefenseEffectiveness:
    """Aggregated effectiveness metrics for a defense type."""
    defense_name: str
    total_activations: int = 0
    successful_defenses: int = 0  # Attacker aborted
    false_positives: int = 0
    avg_time_to_abort: float = 0.0
    avg_resources_consumed: float = 0.0
    success_rate: float = 0.0
    last_used: Optional[datetime] = None


class DefenseCoordinator:
    """
    Coordinates multiple defense mechanisms with intelligent state management.
    """
    
    def __init__(self):
        # Active defenses by actor_id
        self.active_defenses: Dict[str, List[DefenseState]] = {}
        
        # Historical effectiveness data
        self.effectiveness_history: Dict[str, DefenseEffectiveness] = {}
        
        # Defense compatibility matrix (which defenses work well together)
        self.compatibility_matrix = {
            'medusa': {'hallucination', 'psyops'},  # Works well with these
            'hallucination': {'medusa', 'psyops'},
            'psyops': {'medusa', 'hallucination', 'deep_scan'},
            'event_horizon': {'hallucination'},  # Honeypot + fake world
            'deep_scan': {'psyops'},
            'block_ip': set(),  # Standalone
        }
        
        # Resource costs (0.0-1.0 scale)
        self.resource_costs = {
            'block_ip': 0.1,
            'deep_scan': 0.3,
            'medusa': 0.2,
            'psyops': 0.15,
            'event_horizon': 0.6,
            'hallucination': 0.7,
        }
        
        # Maximum concurrent defenses per actor
        self.max_defenses_per_actor = 3
        
        # System resource tracking
        self.current_system_load = 0.0
        self.max_system_load = 0.8
    
    async def activate_defense(
        self,
        defense_name: str,
        actor_id: str,
        parameters: Dict[str, Any]
    ) -> DefenseState:
        """
        Activate a defense mechanism for a specific actor.
        """
        # Check if we can activate this defense
        if not await self._can_activate(defense_name, actor_id):
            raise ValueError(f"Cannot activate {defense_name} for {actor_id}: resource or compatibility constraints")
        
        # Create defense state
        state = DefenseState(
            defense_name=defense_name,
            status=DefenseStatus.ACTIVATING,
            activated_at=datetime.now(),
            parameters=parameters,
            target_actor=actor_id
        )
        
        # Add to active defenses
        if actor_id not in self.active_defenses:
            self.active_defenses[actor_id] = []
        self.active_defenses[actor_id].append(state)
        
        # Update system load
        self.current_system_load += self.resource_costs.get(defense_name, 0.5)
        
        # Mark as active
        state.status = DefenseStatus.ACTIVE
        state.last_updated = datetime.now()
        
        # Update effectiveness history
        if defense_name not in self.effectiveness_history:
            self.effectiveness_history[defense_name] = DefenseEffectiveness(
                defense_name=defense_name
            )
        self.effectiveness_history[defense_name].total_activations += 1
        self.effectiveness_history[defense_name].last_used = datetime.now()
        
        return state
    
    async def deactivate_defense(
        self,
        defense_name: str,
        actor_id: str,
        reason: str = "completed"
    ) -> None:
        """
        Deactivate a defense mechanism.
        """
        if actor_id not in self.active_defenses:
            return
        
        # Find and remove the defense
        for i, state in enumerate(self.active_defenses[actor_id]):
            if state.defense_name == defense_name:
                state.status = DefenseStatus.DEACTIVATING
                
                # Update effectiveness metrics
                await self._update_effectiveness(state, reason)
                
                # Remove from active list
                self.active_defenses[actor_id].pop(i)
                
                # Update system load
                self.current_system_load -= self.resource_costs.get(defense_name, 0.5)
                self.current_system_load = max(0.0, self.current_system_load)
                
                break
        
        # Clean up empty actor entries
        if not self.active_defenses[actor_id]:
            del self.active_defenses[actor_id]
    
    async def get_active_defenses(self, actor_id: str) -> List[DefenseState]:
        """
        Get all active defenses for an actor.
        """
        return self.active_defenses.get(actor_id, [])
    
    async def get_compatible_defenses(
        self,
        current_defenses: List[str],
        available_defenses: List[str]
    ) -> List[str]:
        """
        Get defenses compatible with currently active ones.
        """
        if not current_defenses:
            return available_defenses
        
        compatible = set(available_defenses)
        
        for active_defense in current_defenses:
            if active_defense in self.compatibility_matrix:
                # Only keep defenses that are compatible with this one
                compatible &= self.compatibility_matrix[active_defense]
        
        return list(compatible)
    
    async def recommend_defense_combination(
        self,
        threat_level: int,
        available_defenses: List[str],
        actor_id: str
    ) -> List[str]:
        """
        Recommend optimal defense combination based on threat level and effectiveness history.
        """
        # Get currently active defenses
        active = await self.get_active_defenses(actor_id)
        active_names = [d.defense_name for d in active]
        
        # Filter available defenses to compatible ones
        compatible = await self.get_compatible_defenses(active_names, available_defenses)
        
        # Score each defense based on effectiveness and threat level
        scored_defenses = []
        for defense in compatible:
            score = await self._score_defense(defense, threat_level)
            scored_defenses.append((defense, score))
        
        # Sort by score
        scored_defenses.sort(key=lambda x: x[1], reverse=True)
        
        # Select top defenses up to max concurrent
        max_additional = self.max_defenses_per_actor - len(active_names)
        recommended = [d[0] for d in scored_defenses[:max_additional]]
        
        return recommended
    
    async def record_attacker_abort(
        self,
        actor_id: str,
        time_elapsed: float
    ) -> None:
        """
        Record that an attacker aborted their attack.
        """
        if actor_id not in self.active_defenses:
            return
        
        # Mark all active defenses as successful
        for state in self.active_defenses[actor_id]:
            state.attacker_aborted = True
            state.time_to_abort = time_elapsed
            state.effectiveness_score = 1.0
    
    async def get_effectiveness_report(self) -> Dict[str, Any]:
        """
        Generate effectiveness report for all defenses.
        """
        report = {
            'defenses': {},
            'system_stats': {
                'current_load': self.current_system_load,
                'active_defense_count': sum(len(d) for d in self.active_defenses.values()),
                'total_actors_under_defense': len(self.active_defenses)
            }
        }
        
        for defense_name, metrics in self.effectiveness_history.items():
            # Calculate success rate
            if metrics.total_activations > 0:
                metrics.success_rate = metrics.successful_defenses / metrics.total_activations
            
            report['defenses'][defense_name] = {
                'total_activations': metrics.total_activations,
                'successful_defenses': metrics.successful_defenses,
                'success_rate': metrics.success_rate,
                'false_positives': metrics.false_positives,
                'avg_time_to_abort': metrics.avg_time_to_abort,
                'avg_resources_consumed': metrics.avg_resources_consumed,
                'last_used': metrics.last_used.isoformat() if metrics.last_used else None
            }
        
        return report
    
    async def _can_activate(self, defense_name: str, actor_id: str) -> bool:
        """
        Check if a defense can be activated.
        """
        # Check system load
        defense_cost = self.resource_costs.get(defense_name, 0.5)
        if self.current_system_load + defense_cost > self.max_system_load:
            return False
        
        # Check max defenses per actor
        active_count = len(self.active_defenses.get(actor_id, []))
        if active_count >= self.max_defenses_per_actor:
            return False
        
        # Check compatibility with active defenses
        if actor_id in self.active_defenses:
            active_names = [d.defense_name for d in self.active_defenses[actor_id]]
            compatible = await self.get_compatible_defenses(active_names, [defense_name])
            if defense_name not in compatible:
                return False
        
        return True
    
    async def _score_defense(self, defense_name: str, threat_level: int) -> float:
        """
        Score a defense based on effectiveness history and threat level.
        """
        score = 0.0
        
        # Base score from threat level match (higher threat = prefer stronger defenses)
        defense_strength = {
            'block_ip': 1,
            'deep_scan': 2,
            'medusa': 3,
            'psyops': 4,
            'event_horizon': 5,
            'hallucination': 5
        }
        
        strength = defense_strength.get(defense_name, 3)
        threat_match = 1.0 - abs(strength - threat_level) / 5.0
        score += threat_match * 0.4
        
        # Historical effectiveness
        if defense_name in self.effectiveness_history:
            metrics = self.effectiveness_history[defense_name]
            score += metrics.success_rate * 0.4
            
            # Penalize recent usage (prefer variety)
            if metrics.last_used:
                hours_since_use = (datetime.now() - metrics.last_used).total_seconds() / 3600
                novelty_bonus = min(1.0, hours_since_use / 24.0) * 0.2
                score += novelty_bonus
        else:
            # New defense, give it a chance
            score += 0.3
        
        return score
    
    async def _update_effectiveness(self, state: DefenseState, reason: str) -> None:
        """
        Update effectiveness metrics when a defense is deactivated.
        """
        if state.defense_name not in self.effectiveness_history:
            return
        
        metrics = self.effectiveness_history[state.defense_name]
        
        # Update success count
        if state.attacker_aborted:
            metrics.successful_defenses += 1
        
        # Update false positive count
        if reason == "false_positive":
            metrics.false_positives += 1
            state.false_positive = True
        
        # Update average time to abort
        if state.time_to_abort is not None:
            total_time = metrics.avg_time_to_abort * (metrics.total_activations - 1)
            metrics.avg_time_to_abort = (total_time + state.time_to_abort) / metrics.total_activations
        
        # Update average resources consumed
        total_resources = metrics.avg_resources_consumed * (metrics.total_activations - 1)
        metrics.avg_resources_consumed = (total_resources + state.resources_consumed) / metrics.total_activations


# Singleton instance
defense_coordinator = DefenseCoordinator()
