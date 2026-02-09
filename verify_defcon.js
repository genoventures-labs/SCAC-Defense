
// Verification Script for Defcon Level Logic

function verifyDefconMapping(backendThreatLevel) {
    const defconLevel = 6 - backendThreatLevel;
    console.log(`Backend Threat Level: ${backendThreatLevel} -> UI Defcon Level: ${defconLevel}`);

    // Expected mapping:
    // 5 (Critical) -> 1 (Defcon 1)
    // 4 (High) -> 2 (Defcon 2)
    // 3 (Elevated) -> 3 (Defcon 3)
    // 2 (Guarded) -> 4 (Defcon 4)
    // 1 (Low) -> 5 (Defcon 5)

    if (backendThreatLevel === 5 && defconLevel !== 1) console.error("FAIL: 5 should map to 1");
    if (backendThreatLevel === 1 && defconLevel !== 5) console.error("FAIL: 1 should map to 5");
}

console.log("Verifying Defcon Mapping Logic...");
[1, 2, 3, 4, 5].forEach(verifyDefconMapping);
console.log("Verification Complete.");
