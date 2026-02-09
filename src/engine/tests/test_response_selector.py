"""
Test Suite for Enhanced Response Selector

Tests the multi-criteria decision matrix, escalation ladder, and effectiveness
tracking capabilities of the EnhancedResponseSelector.
"""

import pytest
import asyncio
from src.schemas.events import IntentClassification
from src.engine.reasoning.enhanced_response_selector import EnhancedResponseSelector


@pytest.fixture
def response_selector():
    """Create response selector instance for testing."""
    return EnhancedResponseSelector()


@pytest.fixture
def low_threat():
    """Create low threat classification."""
    return IntentClassification(
        intent_type="SUSPICIOUS",
        confidence=0.6,
        reasoning="Minor anomaly detected",
        threat_level=2,
        suggested_action="MONITOR",
        persona_classification="UNKNOWN"
    )


@pytest.fixture
def high_threat():
    """Create high threat classification."""
    return IntentClassification(
        intent_type="ADVERSARIAL",
        confidence=0.95,
        reasoning="Critical system file access detected",
        threat_level=5,
        suggested_action="ESCALATE",
        persona_classification="BLACK_HAT"
    )


@pytest.fixture
def available_defenses():
    """List of available defense protocols."""
    return ['block_ip', 'deep_scan', 'medusa', 'psyops', 'event_horizon', 'hallucination']


class TestResponseSelector:
    """Test suite for EnhancedResponseSelector."""
    
    @pytest.mark.asyncio
    async def test_low_threat_response(self, response_selector, low_threat, available_defenses):
        """Test response selection for low threat."""
        context = {'actor_id': 'test_user', 'system_load': 0.3, 'active_defenses': []}
        
        response = await response_selector.select_response(low_threat, available_defenses, context)
        
        assert response['primary_defense'] in ['block_ip', 'deep_scan']
        assert len(response['secondary_defenses']) == 0  # No secondary for low threat
        assert 'escalation_plan' in response
        print(f"✅ Low threat response: {response['primary_defense']}")
    
    @pytest.mark.asyncio
    async def test_high_threat_response(self, response_selector, high_threat, available_defenses):
        """Test response selection for high threat."""
        context = {'actor_id': 'attacker', 'system_load': 0.3, 'active_defenses': []}
        
        response = await response_selector.select_response(high_threat, available_defenses, context)
        
        assert response['primary_defense'] in ['event_horizon', 'hallucination']
        assert len(response['secondary_defenses']) >= 1  # Should have secondary defenses
        assert 'parameters' in response
        print(f"✅ High threat response: {response['primary_defense']} + {response['secondary_defenses']}")
    
    @pytest.mark.asyncio
    async def test_escalation_path(self, response_selector, low_threat):
        """Test escalation path generation."""
        current_response = {'primary_defense': 'block_ip'}
        
        escalation_path = await response_selector.get_escalation_path(current_response, low_threat.threat_level)
        
        assert len(escalation_path) > 0
        assert all('defense' in step for step in escalation_path)
        assert all('trigger_condition' in step for step in escalation_path)
        print(f"✅ Escalation path: {len(escalation_path)} steps")
        for i, step in enumerate(escalation_path[:3]):
            print(f"   {i+1}. {step['defense']} - {step['trigger_condition']}")
    
    @pytest.mark.asyncio
    async def test_effectiveness_tracking(self, response_selector):
        """Test effectiveness evaluation and tracking."""
        response = {'primary_defense': 'medusa'}
        outcome = {
            'actor_id': 'test_attacker',
            'actor_aborted': True,
            'time_to_abort': 45,  # seconds
            'damage_prevented': 0.8,
            'false_positive': False
        }
        
        effectiveness = await response_selector.evaluate_effectiveness(response, outcome)
        
        assert 0.0 <= effectiveness <= 1.0
        assert effectiveness >= 0.7  # Should be high for successful defense
        
        # Check that history was updated
        assert 'test_attacker' in response_selector.effectiveness_history
        assert 'medusa' in response_selector.effectiveness_history['test_attacker']
        print(f"✅ Effectiveness score: {effectiveness:.2f}")
    
    @pytest.mark.asyncio
    async def test_defense_scoring(self, response_selector, high_threat):
        """Test multi-criteria defense scoring."""
        context = {
            'actor_id': 'test',
            'system_load': 0.5,
            'active_defenses': []
        }
        
        score = await response_selector._calculate_defense_score('medusa', high_threat, context)
        
        assert 0.0 <= score <= 1.0
        print(f"✅ Defense score for 'medusa': {score:.2f}")
    
    @pytest.mark.asyncio
    async def test_system_load_consideration(self, response_selector, high_threat, available_defenses):
        """Test that system load affects defense selection."""
        # High system load
        high_load_context = {'actor_id': 'test', 'system_load': 0.9, 'active_defenses': []}
        
        response_high_load = await response_selector.select_response(high_threat, available_defenses, high_load_context)
        
        # Low system load
        low_load_context = {'actor_id': 'test', 'system_load': 0.1, 'active_defenses': []}
        
        response_low_load = await response_selector.select_response(high_threat, available_defenses, low_load_context)
        
        # Under high load, should prefer lighter defenses
        high_load_cost = response_selector.defense_costs.get(response_high_load['primary_defense'], 0.5)
        low_load_cost = response_selector.defense_costs.get(response_low_load['primary_defense'], 0.5)
        
        print(f"✅ High load defense: {response_high_load['primary_defense']} (cost: {high_load_cost:.2f})")
        print(f"✅ Low load defense: {response_low_load['primary_defense']} (cost: {low_load_cost:.2f})")
    
    @pytest.mark.asyncio
    async def test_defense_parameters(self, response_selector, high_threat, available_defenses):
        """Test defense-specific parameter generation."""
        context = {'actor_id': 'test', 'system_load': 0.3, 'active_defenses': []}
        
        response = await response_selector.select_response(high_threat, available_defenses, context)
        
        assert 'parameters' in response
        
        # Check for defense-specific parameters
        if response['primary_defense'] == 'medusa':
            assert 'injection_intensity' in response['parameters']
        elif response['primary_defense'] == 'psyops':
            assert 'sass_level' in response['parameters']
            assert 'persona' in response['parameters']
        elif response['primary_defense'] == 'event_horizon':
            assert 'containment_depth' in response['parameters']
        
        print(f"✅ Defense parameters: {response['parameters']}")
    
    @pytest.mark.asyncio
    async def test_learning_from_history(self, response_selector, high_threat, available_defenses):
        """Test that selector learns from effectiveness history."""
        context = {'actor_id': 'repeat_attacker', 'system_load': 0.3, 'active_defenses': []}
        
        # First response
        response1 = await response_selector.select_response(high_threat, available_defenses, context)
        defense1 = response1['primary_defense']
        
        # Simulate poor effectiveness
        await response_selector.evaluate_effectiveness(
            {'primary_defense': defense1},
            {'actor_id': 'repeat_attacker', 'actor_aborted': False, 'time_to_abort': 1000, 'damage_prevented': 0.1, 'false_positive': False}
        )
        
        # Second response should potentially choose differently
        response2 = await response_selector.select_response(high_threat, available_defenses, context)
        
        print(f"✅ Learning test - First: {defense1}, Second: {response2['primary_defense']}")
    
    @pytest.mark.asyncio
    async def test_cost_benefit_analysis(self, response_selector, high_threat):
        """Test cost/benefit calculation."""
        response = {'primary_defense': 'hallucination'}
        
        cost_benefit = await response_selector.calculate_cost_benefit(response, high_threat)
        
        assert 'cost' in cost_benefit
        assert 'benefit' in cost_benefit
        assert 0.0 <= cost_benefit['cost'] <= 1.0
        assert 0.0 <= cost_benefit['benefit'] <= 1.0
        print(f"✅ Cost/benefit for hallucination: cost={cost_benefit['cost']:.2f}, benefit={cost_benefit['benefit']:.2f}")


if __name__ == "__main__":
    # Run tests
    print("🧪 Running Enhanced Response Selector Tests...\n")
    pytest.main([__file__, "-v", "-s"])
