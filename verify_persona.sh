#!/bin/bash

# [*] PHASE 21 VERIFICATION: PERSONA-BASED PSYOPS

API_URL="http://localhost:8000/analyze"

echo "[*] TEST 1: SCRIPT KIDDIE ESCALATION"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:00:00Z", "actor_id": "sk_user_'$RANDOM'", "resource": "/etc/passwd", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T18:00:01Z", "actor_id": "sk_user_'$RANDOM'", "resource": "/etc/shadow", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T18:00:02Z", "actor_id": "sk_user_'$RANDOM'", "resource": "admin", "action": "read", "status": "success", "context": {}}
       ]' | jq -r '.classification.persona_classification, .sovereign_voice'

echo ""
echo "[*] TEST 2: BUG BOUNTY HUNTER PROBING"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:05:00Z", "actor_id": "bb_user_'$RANDOM'", "resource": "/.env", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T18:05:05Z", "actor_id": "bb_user_'$RANDOM'", "resource": "/api/v1/health", "action": "read", "status": "success", "context": {}}
       ]' | jq -r '.classification.persona_classification, .sovereign_voice'

echo ""
echo "[*] TEST 3: RED TEAMER METHODOLOGY"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:10:00Z", "actor_id": "rt_user_'$RANDOM'", "resource": "ssh_login", "action": "execute", "status": "failure", "context": {}},
         {"timestamp": "2026-02-08T18:10:30Z", "actor_id": "rt_user_'$RANDOM'", "resource": "sudo", "action": "execute", "status": "failure", "context": {}}
       ]' | jq -r '.classification.persona_classification, .sovereign_voice'

echo ""
echo "[*] TEST 4: BLACK HAT DESTRUCTION"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:15:00Z", "actor_id": "bh_user_'$RANDOM'", "resource": "rm -rf /", "action": "execute", "status": "permission_denied", "context": {}}
       ]' | jq -r '.classification.persona_classification, .sovereign_voice'
