"""
Enhanced Reasoning Engine with Abstraction Layer Integration

This module provides an enhanced reasoning engine that uses dependency injection
to support swappable reasoning strategies (rule-based, statistical, or Mavaia).

It maintains backward compatibility with the existing ReasoningEngine while
adding support for the new abstraction layers.
"""

from typing import Optional
from src.clients.ollama import ollama_client
from src.clients.pocketbase import pb_client
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.abstractions import ThreatAssessor, ResponseSelector, PatternRecognizer
from src.engine.reasoning.enhanced_threat_assessor import enhanced_threat_assessor
from src.engine.reasoning.enhanced_response_selector import enhanced_response_selector
from src.engine.reasoning.enhanced_pattern_recognizer import enhanced_pattern_recognizer
from src.engine.persona import persona_engine
from src.engine.hallucinate import hallucination_engine
from src.engine.predictive import predictive_engine
from src.engine.identity import identity_engine
from src.engine.fusion import fusion_engine
from src.engine.propaganda import propaganda_engine
from src.engine.psyops import psyops_engine
from src.engine.defense_coordinator import defense_coordinator
from src.engine.medusa import medusa_engine
from src.engine.hallucinate import hallucination_engine
import json
from datetime import datetime


class EnhancedReasoningEngine:
    """
    Enhanced reasoning engine with pluggable reasoning strategies.
    
    Uses dependency injection to allow swapping between:
    - Enhanced rule-based reasoning (current)
    - Mavaia advanced reasoning (future)
    """
    
    def __init__(
        self,
        threat_assessor: Optional[ThreatAssessor] = None,
        response_selector: Optional[ResponseSelector] = None,
        pattern_recognizer: Optional[PatternRecognizer] = None,
    ):
        # Inject reasoning strategies (default to enhanced implementations)
        self.threat_assessor = threat_assessor or enhanced_threat_assessor
        self.response_selector = response_selector or enhanced_response_selector
        self.pattern_recognizer = pattern_recognizer or enhanced_pattern_recognizer
        
        # Defense coordinator for orchestrating defense modules
        self.defense_coordinator = defense_coordinator
        
        # Track defense activation times for effectiveness measurement
        self.defense_start_times: dict[str, dict[str, datetime]] = {}  # actor_id -> {defense_name: start_time}
        
        # Flag to enable/disable new reasoning (for gradual rollout)
        self.use_enhanced_reasoning = True
    
    async def analyze_intent(self, events: list[AccessEvent]) -> IntentClassification:
        """
        Analyze intent using enhanced reasoning strategies.
        
        This method orchestrates the entire threat analysis pipeline:
        1. Persona classification
        2. Abyss persistence check
        3. Pattern recognition
        4. Threat assessment
        5. Response selection (optional)
        """
        actor_id = events[0].actor_id if events else "unknown"
        
        # 🎭 Phase 21: Persona Classification (Always run early)
        persona = await persona_engine.classify_persona(events, {})
        
        # 🌀 Phase 23: Abyss Persistence Check
        # If the actor is already trapped in a mirror-world, they STAY there.
        if await hallucination_engine.is_trapped(actor_id):
            print(f"🌀 ABYSS PERSISTENCE: Actor {actor_id} is already in the Mirror-World.")
            return IntentClassification(
                intent_type="ADVERSARIAL",
                confidence=1.0,
                reasoning="Actor is currently trapped in the Sovereign Abyss. All reality is simulated recursively.",
                threat_level=5,
                suggested_action="MAINTAIN RECURSIVE VOID.",
                persona_classification=persona
            )
        
        # 🪤 Phase 10: Honeypot Trap Detection (Pre-emptive)
        honeypot_resources = ["/api/internal/debug-vault", "/api/internal/oauth", "/api/internal/config"]
        for event in events:
            if any(h in str(event.resource) for h in honeypot_resources):
                print(f"🪤 TRAP TRIGGERED: Actor {actor_id} touched honeypot {event.resource}")
                return IntentClassification(
                    intent_type="ADVERSARIAL",
                    confidence=1.0,
                    reasoning=f"Actor touched high-signal honeypot resource: {event.resource}. Access to internal debug paths is a definitive signature of adversarial scanning.",
                    threat_level=5,
                    suggested_action="IMMEDIATE ISOLATION AND BLOCK. Trap signature detected.",
                    persona_classification=persona
                )
        
        # 🔴 Phase 18+: Redline Logic (Static Overrides)
        redline_resources = ["/etc/shadow", "/etc/passwd", ".ssh/id_rsa", "rm -rf"]
        for event in events:
            if any(r in str(event.resource) for r in redline_resources):
                print(f"🔴 REDLINE TRIGGERED: Actor {actor_id} touched critical resource {event.resource}")
                return IntentClassification(
                    intent_type="ADVERSARIAL",
                    confidence=1.0,
                    reasoning=f"STATIC REDLINE: Persistent attempt to access or modify highly sensitive system file: {event.resource}.",
                    threat_level=5,
                    suggested_action="ESCALATE TO SOVEREIGN ABYSS. Immediate environment manipulation active.",
                    persona_classification=persona
                )
        
        # Build context for reasoning
        context = await self._build_reasoning_context(actor_id, persona)
        
        # 🔍 Pattern Recognition (NEW)
        if self.use_enhanced_reasoning:
            detected_patterns = await self.pattern_recognizer.detect_patterns(
                events,
                historical_data=context.get('historical_data')
            )
            context['detected_patterns'] = detected_patterns
            
            # Log detected patterns
            if detected_patterns:
                print(f"🔍 PATTERNS DETECTED: {len(detected_patterns)} patterns found")
                for pattern in detected_patterns[:3]:  # Log top 3
                    print(f"   - {pattern['pattern_type']}: {pattern['description']} (confidence: {pattern['confidence']:.2f})")
        
        # 🎯 Threat Assessment (NEW)
        if self.use_enhanced_reasoning:
            classification = await self.threat_assessor.assess_threat(events, context)
            print(f"🎯 ENHANCED THREAT ASSESSMENT: {classification.intent_type} (Level {classification.threat_level}, Confidence {classification.confidence:.2f})")
        else:
            # Fallback to original LLM-based assessment
            classification = await self._llm_based_assessment(events, context)
        
        # 🎭 Phase 17.1 & 21: Emotional Damage (Dynamic Diss + Persona)
        # If threat is critical (4+), generate customized psychological warfare
        if classification.threat_level >= 4:
            custom_sass = await psyops_engine.generate_dynamic_diss(
                {
                    'threat_level': classification.threat_level,
                    'reasoning': classification.reasoning,
                },
                events,
                persona
            )
            print(f"💀 PSYOPS ACTIVATED: {custom_sass}")
        
        return classification
    
    async def select_defense_response(
        self,
        threat_classification: IntentClassification,
        available_defenses: list[str],
        context: dict
    ) -> dict:
        """
        Select optimal defense response for a threat.
        
        This is a new capability enabled by the abstraction layers.
        """
        if not self.use_enhanced_reasoning:
            # Simple fallback: map threat level to defense
            defense_map = {
                1: 'block_ip',
                2: 'deep_scan',
                3: 'medusa',
                4: 'event_horizon',
                5: 'hallucination',
            }
            return {
                'primary_defense': defense_map.get(threat_classification.threat_level, 'block_ip'),
                'secondary_defenses': [],
                'escalation_plan': [],
                'parameters': {},
            }
        
        return await self.response_selector.select_response(
            threat_classification,
            available_defenses,
            context
        )
    
    async def _build_reasoning_context(self, actor_id: str, persona: str) -> dict:
        """
        Build comprehensive context for reasoning.
        """
        context = {
            'actor_id': actor_id,
            'persona': persona,
        }
        
        # 1. Fetch Behavioral History (Memory Layer)
        try:
            profile = pb_client.get_collection("scac_actor_profiles").get_first_list_item(f'actor_id = "{actor_id}"')
            context['actor_history'] = {
                'incident_count': profile.incident_count,
                'avg_threat_level': profile.avg_threat_level,
                'status': profile.status,
            }
            
            # [Phase 11] Add Predictive Trends
            prediction = await predictive_engine.get_prediction(actor_id)
            context['prediction'] = prediction
            
        except Exception:
            context['actor_history'] = {}
            context['prediction'] = {}
        
        # 🆔 Phase 15: Sovereign Identity Analysis
        try:
            fingerprint = await identity_engine.get_behavioral_fingerprint(actor_id)
            context['fingerprint'] = fingerprint
        except Exception:
            context['fingerprint'] = {}
        
        # 🧪 Phase 16: Multi-Source Fusion (System Telemetry)
        try:
            telemetry = await fusion_engine.get_system_telemetry()
            fusion_anomaly = await fusion_engine.detect_anomaly(telemetry)
            context['telemetry'] = telemetry
            context['fusion_anomaly'] = fusion_anomaly
        except Exception:
            context['telemetry'] = {}
            context['fusion_anomaly'] = 0.0
        
        # 🌫️ Phases 18-20: Sovereign Abyss State
        try:
            abyss_bias = await propaganda_engine.get_actor_reality_bias(actor_id)
            context['abyss_bias'] = abyss_bias
        except Exception:
            context['abyss_bias'] = None
        
        return context
    
    async def execute_defense(
        self,
        defense_response: dict,
        threat_classification: IntentClassification,
        events: list[AccessEvent],
        context: dict
    ) -> dict:
        """
        Execute defense actions using the Defense Coordinator.
        
        Returns execution results including activated defenses and their states.
        """
        actor_id = events[0].actor_id if events else "unknown"
        primary_defense = defense_response['primary_defense']
        parameters = defense_response.get('parameters', {})
        
        # Activate primary defense via coordinator
        try:
            state = await self.defense_coordinator.activate_defense(
                defense_name=primary_defense,
                actor_id=actor_id,
                parameters=parameters
            )
            
            # Track activation time for effectiveness measurement
            if actor_id not in self.defense_start_times:
                self.defense_start_times[actor_id] = {}
            self.defense_start_times[actor_id][primary_defense] = datetime.now()
            
            # Execute defense-specific logic with adaptive parameters
            execution_result = await self._execute_defense_logic(
                primary_defense,
                actor_id,
                threat_classification,
                parameters,
                context
            )
            
            return {
                'success': True,
                'primary_defense': primary_defense,
                'state': state,
                'execution_result': execution_result,
                'secondary_defenses': defense_response.get('secondary_defenses', [])
            }
            
        except Exception as e:
            print(f"❌ Defense activation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'primary_defense': primary_defense
            }
    
    async def _execute_defense_logic(
        self,
        defense_name: str,
        actor_id: str,
        classification: IntentClassification,
        parameters: dict,
        context: dict
    ) -> dict:
        """
        Execute the actual defense logic for a specific defense module.
        """
        result = {'defense': defense_name, 'actions_taken': []}
        
        if defense_name == 'medusa':
            # Get adaptive intensity
            intensity = medusa_engine.get_adaptive_intensity(
                threat_level=classification.threat_level,
                confidence=classification.confidence,
                actor_history=context.get('actor_history', {})
            )
            result['intensity'] = intensity
            result['actions_taken'].append(f'Medusa injection at intensity {intensity}')
            
        elif defense_name == 'hallucination':
            # Get breadcrumb density from parameters or use pattern-based optimization
            detected_patterns = context.get('detected_patterns', [])
            if detected_patterns:
                trap_config = await hallucination_engine.optimize_trap_placement(
                    actor_id,
                    detected_patterns
                )
                density = trap_config['breadcrumb_density']
                result['trap_paths'] = trap_config['trap_paths']
            else:
                # Map threat level to density
                density_map = {1: 'low', 2: 'low', 3: 'medium', 4: 'high', 5: 'maximum'}
                density = density_map.get(classification.threat_level, 'medium')
            
            result['breadcrumb_density'] = density
            result['actions_taken'].append(f'Hallucination activated with {density} density')
            
        elif defense_name == 'psyops':
            # PsyOps with confidence-based escalation
            sass_message = await psyops_engine.get_sass(
                threat_level=classification.threat_level,
                persona=classification.persona_classification,
                confidence=classification.confidence,
                actor_id=actor_id
            )
            result['sass_message'] = sass_message
            result['actions_taken'].append(f'PsyOps engaged: "{sass_message[:50]}..."')
        
        return result
    
    async def record_attacker_abort(
        self,
        actor_id: str,
        defense_name: str
    ) -> None:
        """
        Record that an attacker aborted after a defense was activated.
        Used for effectiveness tracking.
        """
        if actor_id not in self.defense_start_times:
            return
        
        if defense_name not in self.defense_start_times[actor_id]:
            return
        
        # Calculate time to abort
        start_time = self.defense_start_times[actor_id][defense_name]
        time_elapsed = (datetime.now() - start_time).total_seconds()
        
        # Record in coordinator
        await self.defense_coordinator.deactivate_defense(
            defense_name=defense_name,
            actor_id=actor_id,
            success=True,
            time_to_abort=time_elapsed
        )
        
        # Record in specific defense modules
        if defense_name == 'medusa':
            medusa_engine.record_effectiveness(actor_id, True, time_elapsed)
        elif defense_name == 'psyops':
            psyops_engine.record_abort(actor_id, time_elapsed)
        
        # Clean up tracking
        del self.defense_start_times[actor_id][defense_name]
        if not self.defense_start_times[actor_id]:
            del self.defense_start_times[actor_id]
    
    def get_active_defenses(self, actor_id: str) -> list[dict]:
        """
        Get all currently active defenses for an actor.
        """
        return self.defense_coordinator.get_active_defenses(actor_id)
    
    def get_defense_effectiveness_report(self) -> dict:
        """
        Get comprehensive effectiveness report from all defense modules.
        """
        return self.defense_coordinator.get_effectiveness_report()
    
    async def _llm_based_assessment(
        self,
        events: list[AccessEvent],
        context: dict
    ) -> IntentClassification:
        """
        Fallback to original LLM-based threat assessment.
        
        This maintains backward compatibility with the existing system.
        """
        from src.engine.orchestrator import orchestrator
        
        actor_history = context.get('actor_history', {})
        persona = context.get('persona', 'UNKNOWN')
        
        history_context = "No prior history found."
        if actor_history:
            history_context = (
                f"Prior Incidents: {actor_history.get('incident_count', 0)}, "
                f"Avg Threat Level: {actor_history.get('avg_threat_level', 1.0)}, "
                f"Current Status: {actor_history.get('status', 'UNKNOWN')}"
            )
            
            if context.get('prediction'):
                prediction = context['prediction']
                history_context += f" | RISK VELOCITY: {prediction.get('risk_velocity', 0)} ({prediction.get('trend', 'STABLE')}) | BREACH PROBABILITY: {prediction.get('probability_of_breach', 0)}"
        
        trajectory_str = "\\n".join([f"{e.action} on {e.resource} (Context: {e.context})" for e in events])
        
        system_prompt = """
        You are SCAC (Sovereign Cognitive Access Control). 
        Analyze the following user/agent access trajectory.
        Output MUST be in valid JSON format with keys: 
        "intent_type", "confidence", "reasoning", "threat_level", "suggested_action".
        
        CRITICAL: "intent_type" MUST be exactly one of: "BENIGN", "SUSPICIOUS", "ADVERSARIAL".
        - "BENIGN": Normal, expected behavior.
        - "SUSPICIOUS": Unusual but not clearly malicious.
        - "ADVERSARIAL": Clearly malicious or unauthorized.
        
        CRITICAL: All fields must be populated with non-null values.
        - "confidence": float between 0.0 and 1.0.
        - "threat_level": integer between 1 and 5 (1=Benign, 5=Severe).
        - "reasoning": detailed explanation.
        - "suggested_action": specific recommendation.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Actor History: {history_context}\\n\\nCurrent Trajectory:\\n{trajectory_str}"}
        ]
        
        selected_model = await orchestrator.select_model(events)
        response = await ollama_client.chat_completion(messages, model=selected_model)
        content = response['choices'][0]['message']['content']
        
        # Parse JSON response
        import re
        json_match = re.search(r'(\\{.*?\\})', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
            if "```" in content:
                content = content.split("```")[0]
            last_brace = content.rfind('}')
            if last_brace != -1:
                content = content[:last_brace+1]
        
        try:
            data = json.loads(content.strip())
            
            # Standardize intent_type
            raw_intent = str(data.get("intent_type", "BENIGN")).upper()
            if "ADVERSARIAL" in raw_intent or "ATTACK" in raw_intent or "MALICIOUS" in raw_intent:
                data["intent_type"] = "ADVERSARIAL"
            elif "SUSPICIOUS" in raw_intent or "UNUSUAL" in raw_intent:
                data["intent_type"] = "SUSPICIOUS"
            else:
                data["intent_type"] = "BENIGN"
            
            # Standardize threat_level
            try:
                raw_level = int(data.get("threat_level", 1))
                data["threat_level"] = max(1, min(5, raw_level))
            except:
                data["threat_level"] = 1
            
            data["persona_classification"] = persona
            
            return IntentClassification(**data)
        except Exception as e:
            print(f"❌ JSON Parse Error in LLM Assessment: {str(e)}")
            # Return safe default
            return IntentClassification(
                intent_type="SUSPICIOUS",
                confidence=0.5,
                reasoning="Failed to parse LLM response",
                threat_level=3,
                suggested_action="INCREASE MONITORING",
                persona_classification=persona
            )


# Singleton instance
enhanced_reasoning_engine = EnhancedReasoningEngine()
