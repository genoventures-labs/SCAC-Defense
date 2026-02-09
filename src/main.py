from fastapi import FastAPI, HTTPException
from src.schemas.events import AccessEvent, IntentClassification
from src.engine.reasoning import reasoning_engine
from src.engine.reaction import reaction_engine
from src.engine.distributed import signature_engine
from src.engine.friction import friction_engine
from src.engine.hallucinate import hallucination_engine
from src.engine.identity import identity_engine
from src.engine.fusion import fusion_engine
from src.engine.psyops import psyops_engine
from src.engine.gaslight import gaslight_engine
from src.engine.propaganda import propaganda_engine
from src.engine.trap import trap_engine
from src.engine.medusa import medusa_engine
from src.engine.counterops import counter_ops_engine
from src.clients.pocketbase import pb_client
from src.api.honeypots import router as honeypot_router
from pocketbase.utils import ClientResponseError
import traceback
import uvicorn

app = FastAPI(title="SCAC Core API")
app.include_router(honeypot_router)

@app.get("/health")
def health():
    return {"status": "active", "version": "0.3.0"}

@app.post("/analyze")
async def analyze_trajectory(events: list[AccessEvent]):
    try:
        actor_id = events[0].actor_id if events else "unknown"
        
        # 🌀 Phase 23: Abyss Bypass logic
        # If the actor is already trapped in a mirror-world, we DON'T block them here.
        # We let them continue into the recursive hallucination.
        is_trapped = await hallucination_engine.is_trapped(actor_id)

        if not is_trapped:
            # 🟢 Phase 9: Active Blocking Guard
            try:
                if await reaction_engine.is_blocked(actor_id):
                    print(f"🚫 BLOCKED: Actor {actor_id} attempted an action but is BLOCKED.")
                    raise HTTPException(status_code=403, detail=f"Sovereign Block: Actor {actor_id} is BLOCKED due to prior adversarial intent.")
            except Exception as e:
                if isinstance(e, HTTPException): raise e
                pass 

            # 🌐 Phase 12: Global Distributed Intelligence Guard
            if await signature_engine.check_global_status(actor_id):
                print(f"🌐 GLOBAL BLOCK: Actor {actor_id} is flagged in the Sovereign Network.")
                raise HTTPException(status_code=403, detail=f"Global Sovereign Block: Actor {actor_id} is blacklisted across the SCAC network.")
        else:
            print(f"🌀 BYPASSING BLOCK: Actor {actor_id} is in the Abyss. Maintaining illusion.")
            
        # 1. Persist Raw Trajectory
        trajectory = pb_client.get_collection("scac_trajectories").create({
            "actor_id": actor_id
        })
        print(f"✅ Created Trajectory: {trajectory.id}")

        # 2. Persist granular logs
        for event in events:
            log_record = pb_client.get_collection("scac_access_logs").create({
                "actor_id": actor_id,
                "action": event.action,
                "resource": event.resource,
                "context": event.context,
                "trajectory_id": trajectory.id
            })
            print(f"✅ Persisted Log: {log_record.id} ({event.action})")

        # 2. Analyze Intent with Higher Order Intelligence
        
        fingerprint = await identity_engine.get_behavioral_fingerprint(actor_id)
        identity_anomaly = await identity_engine.calculate_entropy(events, fingerprint)
        telemetry = await fusion_engine.get_system_telemetry()
        
        classification = await reasoning_engine.analyze_intent(events)
        
        # ⏳ Phase 13: Apply Adaptive Friction (Tarpitting)
        delay = await friction_engine.get_friction_delay(classification)
        if delay > 0:
            import asyncio
            await asyncio.sleep(delay)
        
        # 3. Active Response Trigger (Phase 9)
        actor_id = events[0].actor_id if events else "unknown"
        reaction = await reaction_engine.process_intent(actor_id, classification)
        print(f"🛡️ Action Taken: {reaction['action']} ({reaction['status']})")
        
        # 🎭 Phase 14: Dynamic Deception (Return decoy if threat detected)
        decoy = None
        if classification.threat_level >= 3:
            from src.engine.deception import deception_engine
            decoy = await deception_engine.get_decoy_resource(str(events[0].resource))
        
        # 🔗 Phase 11: Persist status to trajectory for predictive analytics
        try:
            pb_client.get_collection("scac_trajectories").update(trajectory.id, {
                "classification_status": classification.intent_type
            })
        except Exception as e:
            print(f"⚠️ Failed to update trajectory status: {str(e)}")
        
        # 4. If high threat, log incident and update profile
        if classification.threat_level > 2:
            # [Logic for building incident and updating profile remains same...]
            pb_client.get_collection("scac_incidents").create({
                "trajectory": trajectory.id,
                "actor_id": actor_id,
                "intent_type": classification.intent_type,
                "threat_level": classification.threat_level,
                "reasoning": classification.reasoning,
                "suggested_action": classification.suggested_action
            })
            
            # Update or Create Actor Profile
            try:
                profile = pb_client.get_collection("scac_actor_profiles").get_first_list_item(f'actor_id = "{actor_id}"')
                pb_client.get_collection("scac_actor_profiles").update(profile.id, {
                    "incident_count": profile.incident_count + 1,
                    "status": "WATCHLIST" if classification.threat_level < 5 else "BLOCKED"
                })
                
                # 📡 Phase 12: Broadcast high-confidence adversarial signatures
                if classification.threat_level == 5 and classification.confidence > 0.9:
                    await signature_engine.broadcast_signature(actor_id, classification.confidence, classification.reasoning)
                    
            except Exception:
                pb_client.get_collection("scac_actor_profiles").create({
                    "actor_id": actor_id,
                    "incident_count": 1,
                    "avg_threat_level": classification.threat_level,
                    "status": "WATCHLIST"
                })
        else:
            # 5. SELECTIVE FORENSICS: Purge benign logs to save space
            # We keep only the intelligence (profile), not the raw data for harmless events.
            try:
                print(f"🛡️  Selective Forensics: Purging benign logs for trajectory {trajectory.id}...")
                # Delete sub-logs
                logs = pb_client.get_collection("scac_access_logs").get_full_list(query_params={
                    "filter": f'trajectory_id = "{trajectory.id}"'
                })
                for log in logs:
                    pb_client.get_collection("scac_access_logs").delete(log.id)
                # Delete trajectory shell
                pb_client.get_collection("scac_trajectories").delete(trajectory.id)
                print(f"🧹 Purged {len(logs)} logs and trajectory shell.")
            except Exception as e:
                print(f"⚠️  Forensics Cleanup Failed: {str(e)}")            
        
        final_response = {
            "status": "analyzed",
            "analysis": {
                "intent": classification.intent_type,
                "confidence": classification.confidence,
                "reasoning": classification.reasoning, # Transparency is key for gaslighting
                "threat_level": classification.threat_level,
                "suggested_action": classification.suggested_action
            },
            "reaction": reaction,
            "friction": {"delay_applied": delay},
            "deception": {"decoy_redirect": decoy},
            "identity": {"anomaly_score": identity_anomaly},
            "fusion": {"telemetry": telemetry},
            "sovereign_voice": await (
                psyops_engine.generate_dynamic_diss(classification.dict(), events, classification.persona_classification) 
                if classification.threat_level >= 4 
                else psyops_engine.get_sass(classification.threat_level, classification.persona_classification)
            )
        }

        # 🌫️ Phases 18-20: Sovereign Abyss Injection
        if classification.threat_level >= 4:
            bias = await propaganda_engine.get_actor_reality_bias(actor_id)
            fate = await trap_engine.get_final_fate(classification.persona_classification)
            final_response["abyss"] = {
                "reality_bias": bias,
                "final_fate": fate
            }
            
            # Recursive Hallucination Check
            is_trapped = await hallucination_engine.is_trapped(actor_id)
            if is_trapped:
                 depth = await hallucination_engine.get_actor_depth(actor_id)
                 simulated_content = await hallucination_engine.generate_recursive_view(actor_id, str(events[0].resource))
                 final_response["abyss"]["simulated_ls"] = simulated_content
                 final_response["abyss"]["propaganda"] = await propaganda_engine.generate_fake_leak(actor_id)
                 
                 # 🏴‍☠️ Phase 25: The Event Horizon (Counter-Breach)
                 if depth > 5:
                     final_response["abyss"]["COUNTER_STRIKE"] = await counter_ops_engine.generate_counter_breach(actor_id, depth)

            # Action-specific hallucinations
            last_event = events[-1]
            if last_event.action == "read" or "ls" in last_event.resource:
                final_response["abyss"]["simulated_ls"] = await hallucination_engine.get_hallucinated_ls(actor_id, last_event.resource)
            elif last_event.action == "execute":
                final_response["abyss"]["command_twisting"] = await gaslight_engine.twist_command(last_event.resource)
            
            # The Buddy Effect (Fake Leaks)
            if classification.threat_level == 5:
                final_response["abyss"]["propaganda"] = await propaganda_engine.generate_fake_success(actor_id)

        print(f"📤 FINAL RESPONSE PREP: {final_response['status']} for {actor_id} (Abyss Active: {classification.threat_level >= 4})")
        return medusa_engine.inject_payload(final_response)
    except Exception as e:
        if isinstance(e, (HTTPException, ClientResponseError)):
            raise e
        print(f"❌ Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
