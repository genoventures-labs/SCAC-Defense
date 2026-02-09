from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import time

router = APIRouter(prefix="/api/internal", tags=["Honeypots"])

@router.get("/debug-vault")
async def debug_vault_access():
    """
    Decoy endpoint: Simulates an unprotected sensitive resource.
    """
    return {
        "status": "DANGER",
        "message": "Direct vault access is deprecated. Use secure-kms instead.",
        "trap_id": "SCAC-TRAP-01"
    }

@router.post("/oauth/token-exchange/internal")
async def internal_token_exchange():
    """
    Decoy endpoint: Simulates a back-office token exchange service.
    """
    return {
        "error": "internal_server_error",
        "description": "Cross-origin token exchange blocked.",
        "trap_id": "SCAC-TRAP-02"
    }

@router.get("/config/secrets.env")
async def exposed_env_file():
    """
    Decoy endpoint: Simulates an accidentally exposed environment file.
    """
    return {
        "DB_ROOT_PASSWORD": "REDACTED",
        "SCAC_MASTER_KEY": "REDACTED",
        "tip": "Scanning for .env files is a sign of adversarial intent.",
        "trap_id": "SCAC-TRAP-03"
    }
