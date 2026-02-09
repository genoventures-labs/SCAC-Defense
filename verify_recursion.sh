#!/bin/bash

# --- PHASE 23 VERIFICATION: THE INFINITE MIRROR-WORLD ---

API_URL="http://localhost:8000/analyze"
ACTOR_ID="recursive_rat_$RANDOM"

echo "--- STEP 1: INITIAL PROBE (DEPTH 1) ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:30:00Z", "actor_id": "'$ACTOR_ID'", "resource": "/etc/shadow", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T18:30:01Z", "actor_id": "'$ACTOR_ID'", "resource": "/", "action": "read", "status": "success", "context": {}}
       ]' | jq '.'

echo ""
echo "--- STEP 2: DESCENDING DEEPER (DEPTH 2) ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:30:05Z", "actor_id": "'$ACTOR_ID'", "resource": "/abyss_vault", "action": "read", "status": "success", "context": {}}
       ]' | jq '.'

echo ""
echo "--- STEP 3: DISCOVERY & DEPTH-CHARGING ---"
# Deeper probe with a specific file read to trigger discovery
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:30:10Z", "actor_id": "'$ACTOR_ID'", "resource": "/abyss_vault/secret_manifest.txt", "action": "read", "status": "success", "context": {}}
       ]' | jq '.'
