#!/bin/bash
echo "[*] TEST 1: NORMAL CADENCE (BASELINE)"
curl -s -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '[{"actor_id":"id_final_v1","action":"read","resource":"dashboard","context":{}}]' | jq .

echo -e "\n[*] TEST 2: ANOMALOUS TRANSITIONS (MULTIPLE EVENTS)"
curl -s -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '[{"actor_id":"id_final_v1","action":"read","resource":"dashboard","context":{}}, {"actor_id":"id_final_v1","action":"read","resource":"admin_panel","context":{}}]' | jq .
