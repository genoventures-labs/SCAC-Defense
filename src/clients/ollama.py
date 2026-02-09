import httpx
from src.utils.config import settings

class OllamaClient:
    def __init__(self):
        # Use OPENWEBUI_BASE_URL if provided, else fall back to OPENWEBUI_URL
        base = settings.OPENWEBUI_BASE_URL or settings.OPENWEBUI_URL
        self.base_url = f"{base}/api"
        self.default_model = settings.OLLAMA_MODEL
        self.token = settings.OPENWEBUI_TOKEN

    async def _ensure_token(self):
        # If we already have a static token (sk-), skip signin
        if self.token:
            print(f"🔑 Using pre-configured Open WebUI Token: {self.token[:10]}...")
            return

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/v1/auths/signin"
            print(f"📡 Attempting Sign-in to: {url}")
            response = await client.post(
                url,
                json={
                    "email": settings.OPENWEBUI_EMAIL,
                    "password": settings.OPENWEBUI_PASSWORD
                }
            )
            print(f"📥 Sign-in Response: {response.status_code}")
            response.raise_for_status()
            self.token = response.json().get("token")
            print("✅ Token acquired.")

    async def list_models(self) -> list:
        await self._ensure_token()
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{self.base_url}/models"
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            response.raise_for_status()
            data = response.json()
            models = [m.get("id") or m.get("name") for m in data.get("models", [])]
            # Some APIs use 'data' instead of 'models'
            if not models and "data" in data:
                models = [m.get("id") or m.get("name") for m in data.get("data", [])]
            
            return models

    async def chat_completion(self, messages: list, model: str = None, temperature: float = 0.0):
        await self._ensure_token()
        target_model = model or self.default_model
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature
            }
            print(f"📡 Requesting Completion from: {url}")
            print(f"📦 Model: {target_model}, Messages: {len(messages)}")
            
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                json=payload,
                timeout=60.0
            )
            
            print(f"📥 Completion Response: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ API Error Text: {response.text}")
            
            response.raise_for_status()
            try:
                res_json = response.json()
                print("✅ Completion successful.")
                return res_json
            except Exception as e:
                print(f"❌ JSON Parse Error. Raw Body: {response.text}")
                raise e

ollama_client = OllamaClient()
