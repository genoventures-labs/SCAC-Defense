from pocketbase import PocketBase
from src.utils.config import settings

class PocketBaseClient:
    def __init__(self):
        self.client = PocketBase(settings.POCKETBASE_URL)
        self._authenticate()

    def _authenticate(self):
        if settings.POCKETBASE_ADMIN_EMAIL and settings.POCKETBASE_ADMIN_PASSWORD:
            self.client.admins.auth_with_password(
                settings.POCKETBASE_ADMIN_EMAIL, 
                settings.POCKETBASE_ADMIN_PASSWORD
            )

    def get_collection(self, name: str):
        return self.client.collection(name)

pb_client = PocketBaseClient()
