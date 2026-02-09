"""
Integration Tests for Defense Coordinator and Enhanced Reasoning Engine

Tests the coordinated defense system with multi-defense scenarios,
escalation paths, and effectiveness tracking.
"""

import pytest
from datetime import datetime, timedelta
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.enhanced_reasoning_engine import enhanced_reasoning_engine
from src.engine.defense_coordinator import defense_coordinator
from src.engine.medusa import medusa_engine
from src.engine.hallucinate import hallucination_engine
from src.engine.psyops import psyops_engine


@pytest.fixture
def sample_events():
    """Create sample access events for testing."""
    return [
        AccessEvent(
            actor_id="test_actor_001",
            action="READ",
            resource="/api/users/admin",
            timestamp=datetime.now().isoformat(),
            context={"ip": "192.168.1.100"}
        )
    ]


@pytest.fixture
def high_threat_events():
    """Create high-threat access events."""
    return [
        AccessEvent(
            actor_id="test_actor_002",
            action="EXECUTE",
            resource="/etc/shadow",
            timestamp=datetime.now().isoformat(),
            context={"ip": "10.0.0.50"}
        ),
        AccessEvent(
            actor_id="test_actor_002",
            action="READ",
            resource="/root/.ssh/id_rsa",
            timestamp=(datetime.now() + timedelta(seconds=1)).isoformat(),
            context={"ip": "10.0.0.50"}
        )
    ]


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all defense states before each test."""
    defense_coordinator.active_defenses.clear()
    defense_coordinator.effectiveness_history.clear()
    medusa_engine.actor_effectiveness.clear()
    medusa_engine.recent_prompts.clear()
    psyops_engine.actor_engagement.clear()
    hallucination_engine.actor_states.clear()
    enhanced_reasoning_engine.defense_start_times.clear()
    yield


class TestDefenseCoordination:
    """Test defense coordinator integration."""
    
    @pytest.mark.asyncio
    async def test_single_defense_activation(self, sample_events):
        """Test activating a single defense via coordinator."""
        # Analyze threat
        classification = await enhanced_reasoning_engine.analyze_intent(sample_events)
        
        # Select defense
        context = await enhanced_reasoning_engine._build_reasoning_context(
            "test_actor_001",
            classification.persona_classification
        )
        defense_response = await enhanced_reasoning_engine.select_defense_response(
            classification,
            ['block_ip', 'deep_scan', 'medusa'],
            context
        )
        
        # Execute defense
        result = await enhanced_reasoning_engine.execute_defense(
            defense_response,
            classification,
            sample_events,
            context
        )
        
        assert result['success'] is True
        assert result['primary_defense'] in ['block_ip', 'deep_scan', 'medusa']
        assert 'state' in result
        assert result['state']['status'] == 'active'
    
    @pytest.mark.asyncio
    async def test_multi_defense_compatibility(self, high_threat_events):
        """Test that compatible defenses can be activated together."""
        classification = await enhanced_reasoning_engine.analyze_intent(high_threat_events)
        
        # Should be high threat (4-5)
        assert classification.threat_level >= 4
        
        # Activate multiple compatible defenses
        await defense_coordinator.activate_defense(
            'medusa',
            'test_actor_002',
            {'intensity': 4}
        )
        
        await defense_coordinator.activate_defense(
            'hallucination',
            'test_actor_002',
            {'breadcrumb_density': 'high'}
        )
        
        await defense_coordinator.activate_defense(
            'psyops',
            'test_actor_002',
            {'threat_level': 4}
        )
        
        # All three should be active (they're compatible)
        active = defense_coordinator.get_active_defenses('test_actor_002')
        assert len(active) == 3
        
        defense_names = [d['defense_name'] for d in active]
        assert 'medusa' in defense_names
        assert 'hallucination' in defense_names
        assert 'psyops' in defense_names
    
    @pytest.mark.asyncio
    async def test_incompatible_defense_rejection(self):
        """Test that incompatible defenses are rejected."""
        # Activate block_ip (standalone)
        await defense_coordinator.activate_defense(
            'block_ip',
            'test_actor_003',
            {}
        )
        
        # Try to activate another defense (should fail)
        with pytest.raises(Exception, match="incompatible|conflict"):
            await defense_coordinator.activate_defense(
                'medusa',
                'test_actor_003',
                {}
            )
    
    @pytest.mark.asyncio
    async def test_resource_limit_enforcement(self):
        """Test that system load limits are enforced."""
        # Simulate high system load
        defense_coordinator.current_system_load = 0.85  # 85% load
        
        # Try to activate defense (should fail due to load)
        with pytest.raises(Exception, match="system load|resource"):
            await defense_coordinator.activate_defense(
                'event_horizon',
                'test_actor_004',
                {}
            )


class TestAdaptiveParameters:
    """Test that defense modules receive adaptive parameters."""
    
    @pytest.mark.asyncio
    async def test_medusa_adaptive_intensity(self, high_threat_events):
        """Test Medusa receives adaptive intensity based on threat."""
        classification = await enhanced_reasoning_engine.analyze_intent(high_threat_events)
        context = await enhanced_reasoning_engine._build_reasoning_context(
            "test_actor_002",
            classification.persona_classification
        )
        
        # Execute Medusa defense
        defense_response = {'primary_defense': 'medusa', 'parameters': {}}
        result = await enhanced_reasoning_engine.execute_defense(
            defense_response,
            classification,
            high_threat_events,
            context
        )
        
        # Should have adaptive intensity
        assert 'execution_result' in result
        assert 'intensity' in result['execution_result']
        
        # High threat should result in high intensity (4-5)
        intensity = result['execution_result']['intensity']
        assert intensity >= 4
    
    @pytest.mark.asyncio
    async def test_hallucination_pattern_aware_traps(self):
        """Test Hallucination places pattern-specific traps."""
        # Create SQL injection pattern
        sql_events = [
            AccessEvent(
                actor_id="test_actor_005",
                action="READ",
                resource="/api/users?id=1' OR '1'='1",
                timestamp=datetime.now().isoformat(),
                context={"pattern": "sql_injection"}
            )
        ]
        
        classification = await enhanced_reasoning_engine.analyze_intent(sql_events)
        context = await enhanced_reasoning_engine._build_reasoning_context(
            "test_actor_005",
            classification.persona_classification
        )
        
        # Execute Hallucination defense
        defense_response = {'primary_defense': 'hallucination', 'parameters': {}}
        result = await enhanced_reasoning_engine.execute_defense(
            defense_response,
            classification,
            sql_events,
            context
        )
        
        # Should have trap paths
        assert 'execution_result' in result
        if 'trap_paths' in result['execution_result']:
            trap_paths = result['execution_result']['trap_paths']
            # Should include SQL-related trap
            assert any('database' in path or 'sql' in path for path in trap_paths)
    
    @pytest.mark.asyncio
    async def test_psyops_persistence_escalation(self):
        """Test PsyOps escalates based on persistence."""
        actor_id = "test_actor_006"
        
        # Simulate multiple attempts
        for i in range(7):
            await psyops_engine.get_sass(
                threat_level=3,
                persona="SCRIPT_KIDDIE",
                confidence=0.7,
                actor_id=actor_id
            )
        
        # Check persistence level
        persistence = psyops_engine._get_persistence_level(actor_id)
        assert persistence >= 1  # Should be medium persistence (6-10 attempts)


class TestEffectivenessTracking:
    """Test effectiveness measurement and tracking."""
    
    @pytest.mark.asyncio
    async def test_record_attacker_abort(self, sample_events):
        """Test recording attacker abort for effectiveness."""
        classification = await enhanced_reasoning_engine.analyze_intent(sample_events)
        context = await enhanced_reasoning_engine._build_reasoning_context(
            "test_actor_007",
            classification.persona_classification
        )
        
        # Activate defense
        defense_response = {'primary_defense': 'medusa', 'parameters': {}}
        await enhanced_reasoning_engine.execute_defense(
            defense_response,
            classification,
            sample_events,
            context
        )
        
        # Simulate attacker abort after 5 seconds
        import asyncio
        await asyncio.sleep(0.1)  # Small delay for testing
        
        await enhanced_reasoning_engine.record_attacker_abort(
            "test_actor_007",
            "medusa"
        )
        
        # Check that effectiveness was recorded
        metrics = medusa_engine.get_effectiveness_metrics()
        assert metrics['total_activations'] > 0
        assert metrics['successful_aborts'] > 0
    
    @pytest.mark.asyncio
    async def test_effectiveness_report_generation(self):
        """Test generating comprehensive effectiveness report."""
        # Activate some defenses
        await defense_coordinator.activate_defense('medusa', 'actor_a', {})
        await defense_coordinator.activate_defense('psyops', 'actor_b', {})
        
        # Deactivate with success
        await defense_coordinator.deactivate_defense(
            'medusa',
            'actor_a',
            success=True,
            time_to_abort=3.5
        )
        
        # Get report
        report = enhanced_reasoning_engine.get_defense_effectiveness_report()
        
        assert 'medusa' in report
        assert report['medusa']['total_activations'] > 0
        assert report['medusa']['successful_aborts'] > 0


class TestEscalationPath:
    """Test defense escalation scenarios."""
    
    @pytest.mark.asyncio
    async def test_threat_level_escalation(self):
        """Test that defenses escalate as threat level increases."""
        actor_id = "test_actor_008"
        
        # Level 1 threat
        low_events = [
            AccessEvent(
                actor_id=actor_id,
                action="READ",
                resource="/api/public/status",
                timestamp=datetime.now().isoformat(),
                context={}
            )
        ]
        
        classification_low = await enhanced_reasoning_engine.analyze_intent(low_events)
        context = await enhanced_reasoning_engine._build_reasoning_context(
            actor_id,
            classification_low.persona_classification
        )
        
        response_low = await enhanced_reasoning_engine.select_defense_response(
            classification_low,
            ['block_ip', 'deep_scan', 'medusa', 'event_horizon'],
            context
        )
        
        # Level 5 threat
        high_events = [
            AccessEvent(
                actor_id=actor_id,
                action="EXECUTE",
                resource="/etc/shadow",
                timestamp=datetime.now().isoformat(),
                context={}
            )
        ]
        
        classification_high = await enhanced_reasoning_engine.analyze_intent(high_events)
        response_high = await enhanced_reasoning_engine.select_defense_response(
            classification_high,
            ['block_ip', 'deep_scan', 'medusa', 'event_horizon', 'hallucination'],
            context
        )
        
        # High threat should use more aggressive defense
        defense_priority = ['block_ip', 'deep_scan', 'medusa', 'event_horizon', 'hallucination']
        low_index = defense_priority.index(response_low['primary_defense'])
        high_index = defense_priority.index(response_high['primary_defense'])
        
        assert high_index >= low_index  # Higher threat = higher index (more aggressive)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
