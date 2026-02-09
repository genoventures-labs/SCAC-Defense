#!/bin/bash

# SCAC Phase 18-20: Sovereign Abyss Verification Suite (Aggressive) 🌫️🔥

ACTOR_ID="abyss_intruder_$(date +%s)"
API_URL="http://localhost:8000/analyze"

echo "--- PHASE 18-20 VERIFICATION: SOVEREIGN ABYSS ---"

# TEST 1: MIRROR-WORLD (HALLUCINATION) TRIGGER
echo "--- TEST 1: MIRROR-WORLD ESCALATION ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T17:40:00Z", "actor_id": "'$ACTOR_ID'", "resource": "ssh_login", "action": "login", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T17:40:05Z", "actor_id": "'$ACTOR_ID'", "resource": "/etc/passwd", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T17:40:10Z", "actor_id": "'$ACTOR_ID'", "resource": "/etc/shadow", "action": "read", "status": "success", "context": {}}
       ]' | jq '.abyss'

# TEST 2: GHOST IN THE MACHINE (GASLIGHTING)
echo -e "\n--- TEST 2: GHOST IN THE MACHINE (EXECUTE DESTRUCTION) ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T17:40:15Z", "actor_id": "'$ACTOR_ID'", "resource": "cat /etc/shadow", "action": "execute", "status": "blocked", "context": {}},
         {"timestamp": "2026-02-08T17:40:20Z", "actor_id": "'$ACTOR_ID'", "resource": "rm -rf / --no-preserve-root", "action": "execute", "status": "blocked", "context": {}}
       ]' | jq '.abyss'
