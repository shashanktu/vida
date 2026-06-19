from vida.utils.clientConnection import get_credential
from azure.keyvault.secrets import SecretClient #type: ignore
# from config import azure_secrets_url a s asu
import os
from dotenv import load_dotenv  
load_dotenv()

azure_secrets_url = os.environ["Azure_Secrets_URL"]
credential = get_credential()
client = SecretClient(vault_url = azure_secrets_url, credential=credential)

# client.set_secret("my-secret-name", "my-secret-value")
# print("Secret set successfully!")

def get_all_azure_secrets():
    return [secret.name for secret in client.list_properties_of_secrets()]


def get_azure_secret_value(secret_name: str) -> str:
    key = client.get_secret(secret_name)
    return key.value

def set_azure_secret(secret_name: str, secret_value: str) -> str:
    client.set_secret(secret_name, secret_value)
    return f"Secret \"{secret_name}\" added successfully!"

def delete_azure_secret(secret_name: str) -> str:
    client.begin_delete_secret(secret_name)
    return f"Secret \"{secret_name}\" deleted successfully!"

if __name__ == "__main__":
    # Example usage
    name = input("Enter secret name: ")
    value = input("Enter secret value: ")
    print(set_azure_secret(name, value))
