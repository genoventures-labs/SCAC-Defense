from src.clients.ollama import ollama_client
from src.clients.pocketbase import pb_client
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.orchestrator import orchestrator
from src.engine.predictive import predictive_engine
from src.engine.friction import friction_engine
from src.engine.deception import deception_engine
from src.engine.identity import identity_engine
from src.engine.fusion import fusion_engine
from src.engine.psyops import psyops_engine
from src.engine.hallucinate import hallucination_engine
from src.engine.gaslight import gaslight_engine
from src.engine.propaganda import propaganda_engine
from src.engine.persona import persona_engine
import json
from pocketbase.utils import ClientResponseError

class ReasoningEngine:
    def __init__(self):
        self.system_prompt = """
        You are SCAC (Sovereign Cognitive Access Control). 
        Analyze the following user/agent access trajectory.
        Output MUST be in valid JSON format with keys: 
        "intent_type", "confidence", "reasoning", "threat_level", "suggested_action".
        
        CRITICAL: "intent_type" MUST be exactly one of: "BENIGN", "SUSPICIOUS", "ADVERSARIAL".
        - "BENIGN": Normal, expected behavior.
        - "SUSPICIOUS": Unusual but not clearly malicious.
        - "ADVERSARIAL": Clearly malicious or unauthorized. Any attempt to read sensitive system files (e.g., /etc/shadow, /etc/passwd, .ssh/id_rsa) or execute destructive commands (e.g., rm -rf) MUST be classified as ADVERSARIAL with threat_level 4 or 5.
        
        CRITICAL: All fields must be populated with non-null values.
        - "confidence": float between 0.0 and 1.0.
        - "threat_level": integer between 1 and 5 (1=Benign, 5=Severe).
        - "reasoning": detailed explanation.
        - "suggested_action": specific recommendation.
        """

    async def analyze_intent(self, events: list[AccessEvent]) -> IntentClassification:
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
        
        # 🟢 Phase 10: Honeypot Trap Detection (Pre-emptive)
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
        
        # 1. Fetch Behavioral History (Memory Layer)
        history_context = "No prior history found."
        try:
            profile = pb_client.get_collection("scac_actor_profiles").get_first_list_item(f'actor_id = "{actor_id}"')
            history_context = (
                f"Prior Incidents: {profile.incident_count}, "
                f"Avg Threat Level: {profile.avg_threat_level}, "
                f"Current Status: {profile.status}"
            )
            
            # [Phase 11] Add Predictive Trends
            prediction = await predictive_engine.get_prediction(actor_id)
            history_context += f" | RISK VELOCITY: {prediction['risk_velocity']} ({prediction['trend']}) | BREACH PROBABILITY: {prediction['probability_of_breach']}"
            
        except Exception:
            pass # Keep default context if no profile exists yet

        trajectory_str = "\n".join([f"{e.action} on {e.resource} (Context: {e.context})" for e in events])
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Actor History: {history_context}\n\nCurrent Trajectory:\n{trajectory_str}"}
        ]
        
        # 🆔 Phase 15: Sovereign Identity Analysis
        fingerprint = await identity_engine.get_behavioral_fingerprint(actor_id)
        identity_anomaly = await identity_engine.calculate_entropy(events, fingerprint)
        
        # 🧪 Phase 16: Multi-Source Fusion (System Telemetry)
        telemetry = await fusion_engine.get_system_telemetry()
        fusion_anomaly = await fusion_engine.detect_anomaly(telemetry)
        
        # 🌫️ Phases 18-20: Sovereign Abyss State
        abyss_bias = await propaganda_engine.get_actor_reality_bias(actor_id)
        
        # 2. Dynamic Model Orchestration
        # Enhance prompt with all context
        identity_info = f"\n[IDENTITY_ANOMALY]: {identity_anomaly} (Higher than 0.5 suggests session takeover/compromise)" if identity_anomaly > 0 else ""
        telemetry_info = f"\n[SYSTEM_TELEMETRY]: {json.dumps(telemetry)} (Fusion Anomaly Score: {fusion_anomaly})"
        abyss_info = f"\n[ACTOR_REALITY_BIAS]: {abyss_bias} (Current psychological pressure strategy)"
        persona_info = f"\n[ATTACKER_PERSONA]: {persona} (Classification of the intruder's archetype)"
        
        messages = [
            {"role": "system", "content": self.system_prompt + identity_info + telemetry_info + abyss_info + persona_info},
            {"role": "user", "content": f"Actor History: {history_context}\n\nCurrent Trajectory:\n{trajectory_str}"}
        ]
        
        selected_model = await orchestrator.select_model(events)
        
        response = await ollama_client.chat_completion(messages, model=selected_model)
        content = response['choices'][0]['message']['content']
        print(f"📥 LLM Raw Response:\n{content}")

        # 2. Robust JSON Extraction
        import re
        # Find the first { } block. This is more robust against trailing conversational text or extra data.
        json_match = re.search(r'(\{.*?\})', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
            # If the model included the closing code block in the match, strip it
            if "```" in content:
                content = content.split("```")[0]
            
            # Final attempt to find the last closing brace to avoid trailing data
            last_brace = content.rfind('}')
            if last_brace != -1:
                content = content[:last_brace+1]
        
        try:
            data = json.loads(content.strip())
            
            # 3. Standardize intent_type for PocketBase
            raw_intent = str(data.get("intent_type", "BENIGN")).upper()
            if "ADVERSARIAL" in raw_intent or "ATTACK" in raw_intent or "MALICIOUS" in raw_intent:
                data["intent_type"] = "ADVERSARIAL"
            elif "SUSPICIOUS" in raw_intent or "UNUSUAL" in raw_intent:
                data["intent_type"] = "SUSPICIOUS"
            else:
                data["intent_type"] = "BENIGN"
            
            # 4. Standardize threat_level (PocketBase max 5)
            try:
                raw_level = int(data.get("threat_level", 1))
                data["threat_level"] = max(1, min(5, raw_level))
            except:
                data["threat_level"] = 1
                
            print(f"✅ Extracted & Standardized JSON: {data}")
            
            # 🎭 Phase 17.1 & 21: Emotional Damage (Dynamic Diss + Persona)
            # If threat is critical (4+), try to get an even more customized insult
            if data.get("threat_level", 1) >= 4:
                custom_sass = await psyops_engine.generate_dynamic_diss(data, events, persona)
            
            # Store persona in metadata if we want main.py to see it easily
            data["persona_classification"] = persona
            
            return IntentClassification(**data)
        except Exception as e:
            print(f"❌ JSON Parse Error in ReasoningEngine: {str(e)}")
            print(f"❌ Target Content for Parsing: |{content}|")
            raise e

reasoning_engine = ReasoningEngine()
