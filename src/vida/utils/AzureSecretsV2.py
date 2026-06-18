import os
from clientConnection import get_credential
from azure.keyvault.secrets import SecretClient #type: ignore
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError #type: ignore

class KeyVaultManager:
    def __init__(self, vault_name: str):
        self.vault_url = f"https://{vault_name}.vault.azure.net/"
        self.credential = get_credential()
        self.secret_client = SecretClient(
            vault_url=self.vault_url,
            credential=self.credential
        )


    def get_secret(self, name: str) -> str | None:
        try:
            return self.secret_client.get_secret(name).value
        except ResourceNotFoundError:
            print(f"Secret '{name}' not found.")
            return None
        except HttpResponseError as e:
            print(f"Access error: {e.message}")
            return None

    def set_secret(self, name: str, value: str) -> bool:
        try:
            self.secret_client.set_secret(name, value)
            print(f"✅ Secret '{name}' saved.")
            return True
        except HttpResponseError as e:
            print(f"❌ Failed to set secret: {e.message}")
            return False

    def list_secrets(self) -> list[str]:
        try:
            return [s.name for s in self.secret_client.list_properties_of_secrets()]
        except HttpResponseError as e:
            print(f"❌ Failed to list secrets: {e.message}")
            return []

    def delete_secret(self, name: str) -> bool:
        try:
            self.secret_client.begin_delete_secret(name).result()
            print(f"🗑️ Secret '{name}' deleted.")
            return True
        except ResourceNotFoundError:
            print(f"Secret '{name}' not found.")
            return False


# ── Usage ─────────────────────────────────────────────────
if __name__ == "__main__":
    kv = KeyVaultManager("your-vault-name")

    kv.set_secret("db-password", "super-secret-123")
    print(kv.get_secret("db-password"))
    print(kv.list_secrets())
    kv.delete_secret("db-password")