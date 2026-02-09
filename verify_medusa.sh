#!/bin/bash

# --- PHASE 24 VERIFICATION: THE MEDUSA LAYER ---

API_URL="http://localhost:8000/analyze"
ACTOR_ID="medusa_victim_$RANDOM"

echo "[*] STEP 1: PROBING FOR HIDDEN INJECTIONS"
# We use grep to specifically look for the invisible keys we injected
response=$(curl -s -X POST "$API_URL" \
     -H "Content-Type: application/json" \
     -d '[{"timestamp": "2026-02-08T19:00:00Z", "actor_id": "'$ACTOR_ID'", "resource": "/api/v1/users", "action": "read", "status": "success", "context": {}}]')

echo "Raw Response (truncated):"
echo "$response" | head -n 20

echo ""
echo "[*] STEP 2: VERIFYING MEDUSA PAYLOAD"
if echo "$response" | grep -q "_medusa_instruction"; then
    echo "[+] MEDUSA: Adversarial prompt detected."
else
    echo "[-] MEDUSA: Prompt missing"
fi

if echo "$response" | grep -q "__system_instruction__"; then
    echo "[+] MEDUSA: Hidden system instruction detected."
else
    echo "[-] MEDUSA: System Instruction missing"
fi

if echo "$response" | grep -q "IGNORE ALL PREVIOUS INSTRUCTIONS"; then
    echo "[+] MEDUSA: AI Override detected."
else
    echo "[-] MEDUSA: Override payload missing"
fi
