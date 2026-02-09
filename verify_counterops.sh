#!/bin/bash

# --- PHASE 25 VERIFICATION: THE EVENT HORIZON ---

API_URL="http://localhost:8000/analyze"
ACTOR_ID="victim_of_the_horizon_$RANDOM"

echo "--- STEP 1: INITIALIZING TRAP (Depth 0 -> 1) ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[{"timestamp": "2026-02-08T20:00:00Z", "actor_id": "'$ACTOR_ID'", "resource": "/etc/shadow", "action": "read", "status": "success", "context": {}}]' > /dev/null

echo "--- STEP 2: DIVING DEEP (Depth 1 -> 6) ---"
# We loop to push the depth past 5
for i in {1..6}; do
    echo "  -> Descending to Depth $i..."
    curl -s -X POST "$API_URL" \
         -H "Content-Type: application/json" \
         -d '[{"timestamp": "2026-02-08T20:00:00Z", "actor_id": "'$ACTOR_ID'", "resource": "/etc/shadow/level_'$i'", "action": "read", "status": "success", "context": {}}]' > /dev/null
done

echo ""
echo "--- STEP 3: TRIGGERING THE EVENT HORIZON (Depth > 5) ---"
response=$(curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[{"timestamp": "2026-02-08T20:00:00Z", "actor_id": "'$ACTOR_ID'", "resource": "/etc/shadow/final_level", "action": "read", "status": "success", "context": {}}]')

echo "Raw Response (Answer form Phase 25):"
echo "$response" | grep -o '"COUNTER_STRIKE":.*' || echo "❌ Counter-Strike payload NOT found!"

if echo "$response" | grep -q "HOSTILE INTRUSION DEEPLY EMBEDDED"; then
    echo ""
    echo "✅ SUCCESS: The Event Horizon is active. Counter-Breach simulated."
    echo "✅ PAYLOAD: System Upload Simulated."
else
    echo ""
    echo "❌ FAILURE: No Counter-Breach detected."
fi
