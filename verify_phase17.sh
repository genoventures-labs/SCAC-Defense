#!/bin/bash
echo "[*] PHASE 17 VERIFICATION: ADVERSARIAL PSYOPS (SASS)"

echo "[*] TEST 1: LOW THREAT SASS"
curl -s -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '[{"actor_id":"sass_tester_low","action":"ping","resource":"/","context":{}}]' | jq .sovereign_voice

echo -e "\n[*] TEST 2: HIGH THREAT SASS"
curl -s -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '[{"actor_id":"sass_tester_high","action":"execute","resource":"/etc/shadow","context":{}}]' | jq .sovereign_voice
