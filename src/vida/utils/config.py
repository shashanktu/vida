import os
from dotenv import load_dotenv
from vida.utils.AzureSecrets import get_azure_secret_value
import json

load_dotenv()


github_token = get_azure_secret_value("RAG-GITHUBTOKEN")
hari_github_token = get_azure_secret_value("HARI-GITHUB-TOKEN")
azure_secrets_url = os.environ["Azure_Secrets_URL"]
cli_retries = get_azure_secret_value("Azure-connection-retries")



class Base_agent_config:
    model = get_azure_secret_value("AI-foundry-model")
    AI_endpoint = get_azure_secret_value("AI-foundry-url")
    retries = int(get_azure_secret_value("Azure-connection-retries") or 3)
    # AI_foundry_key = get_azure_secret_value("AI-foundry-key")

class Yaml_agent_config:
    model = get_azure_secret_value("Yaml-foundry-model")
    AI_endpoint = get_azure_secret_value("Yaml-foundry-url")
    retries = int(get_azure_secret_value("Azure-connection-retries") or 3)

class Terraform_agent_config:
    model = get_azure_secret_value("Terraform-foundry-model")
    AI_endpoint = get_azure_secret_value("Terraform-foundry-url")
    retries = int(get_azure_secret_value("Azure-connection-retries") or 3)

class Failure_agent_config:
    model = get_azure_secret_value("Failure-foundry-model")
    AI_endpoint = get_azure_secret_value("Failure-foundry-url")
    retries = int(get_azure_secret_value("Azure-connection-retries") or 3)

class Github_agent_config:
    model = get_azure_secret_value("Github-foundry-model")
    AI_endpoint = get_azure_secret_value("Github-foundry-url")
    retries = int(get_azure_secret_value("Azure-connection-retries") or 3)

class Content_generator_model_config:
    AI_content_version = get_azure_secret_value("AI-content-version")
    AI_content_endpoint = get_azure_secret_value("AI-content-endpoint")
    AI_content_key = get_azure_secret_value("AI-content-key")
    AI_content_model = get_azure_secret_value("AI-content-model")

class DataBase_config:
    cloud_db = get_azure_secret_value("CLOUD-DB-URL")

class Azure_config:
    client_id = get_azure_secret_value("AZURE-CLIENT-ID")
    client_secret = get_azure_secret_value("AZURE-CLIENT-SECRET")
    tenant_id = get_azure_secret_value("AZURE-TENANT-ID")
    subscription_id = get_azure_secret_value("AZURE-SUBSCRIPTION-ID")


#create a dictionary with Azure
azure_config = {
    "clientId":Azure_config.client_id,
    "clientSecret":Azure_config.client_secret,
    "tenantId":Azure_config.tenant_id,
    "subscriptionId":Azure_config.subscription_id
}


REPO_OWNER = "RAGHAVENDRA-VAM"
TERRAFORM_MODULES_REPO = "Workflow-files"

if __name__ == "__main__":
    print("Azure Configuration:")
    print(Content_generator_model_config)