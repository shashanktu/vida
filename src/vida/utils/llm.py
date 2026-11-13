
from openai import OpenAI
from azure.identity import get_bearer_token_provider

import os
import sys
import logging

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from vida.utils.config import Content_generator_model_config as cgconfig
from from vida.utils.clientConnection import get_credential  # Adjust import path

logger = logging.getLogger(__name__)


def get_azure_response(text):
    try:
        endpoint = cgconfig.AI_content_endpoint
        deployment = cgconfig.AI_content_model

        if not endpoint or not deployment:
            return "Error: Azure AI endpoint or deployment is missing"

        # Retrieve credentials using existing authentication method
        credential = get_credential()

        # Generate Entra ID token provider
        token_provider = get_bearer_token_provider(
            credential,
            "https://ai.azure.com/.default"
        )

        # Initialize modern Azure AI client
        client = OpenAI(
            base_url=endpoint.rstrip("/") + "/",
            api_key=token_provider
        )

        # Responses API
        response = client.responses.create(
            model=deployment,
            input=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_output_tokens=5000
        )

        return response.output_text

    except Exception as e:
        logger.exception("Azure AI response generation failed")
        return {
            "Azure Error": str(e)
        }


if __name__ == "__main__":
    print(get_azure_response("Hello, how are you?"))
