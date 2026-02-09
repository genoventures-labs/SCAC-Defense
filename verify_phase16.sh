#!/bin/bash
echo "--- PHASE 16 VERIFICATION: MULTI-SOURCE FUSION ---"
curl -s -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '[{"actor_id":"fusion_tester_v1","action":"read","resource":"dashboard","context":{}}]' | jq .fusion
