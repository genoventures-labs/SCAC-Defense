#!/bin/bash

# --- PHASE 22 VERIFICATION: THE STICKY RAT TRAP ---

API_URL="http://localhost:8000/analyze"

echo "--- DEPLOYING THE STICKY RAT TRAP (BLACK HAT) ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:20:00Z", "actor_id": "bh_trap_'$RANDOM'", "resource": "encrypt /data", "action": "execute", "status": "permission_denied", "context": {}}
       ]' | jq -r '.abyss.final_fate'

echo ""
echo "--- DEPLOYING THE STICKY RAT TRAP (SCRIPT KIDDIE) ---"
curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[
         {"timestamp": "2026-02-08T18:20:30Z", "actor_id": "sk_trap_'$RANDOM'", "resource": "/etc/shadow", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T18:20:31Z", "actor_id": "sk_trap_'$RANDOM'", "resource": "/etc/passwd", "action": "read", "status": "success", "context": {}},
         {"timestamp": "2026-02-08T18:20:32Z", "actor_id": "sk_trap_'$RANDOM'", "resource": "admin", "action": "read", "status": "success", "context": {}}
       ]' | jq -r '.abyss.final_fate'
