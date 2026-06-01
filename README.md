# VIDA

VIDA is a modular agent-based automation platform for CI/CD, infrastructure-as-code, and code management. It integrates with GitHub and other cloud providers to automate workflows, manage configurations, and interact with LLMs.

## Features
- Modular adapters for GitHub and other integrations
- FastAPI-based API server
- Database models and CRUD operations using SQLAlchemy
- LLM integration (OpenAI)
- YAML, HCL, and dotenv configuration support
- Asynchronous operations with aiofiles and httpx

## Project Structure

```
src/
  adapters/         # Integration adapters (GitHub, etc.)
  apis/             # FastAPI routers and endpoints
  database/         # Database models and connection logic
  models/           # Pydantic models, validators, and table definitions
  utils/            # Utility modules (logging, config, LLM, etc.)
```

## Getting Started

1. **Install dependencies:**
   ```sh
   pip install .
   ```
2. **Run the API server:**
   ```sh
   uvicorn src.apis.router:app --reload
   ```

## Configuration
- Environment variables can be set in a `.env` file.
- YAML and HCL files are supported for advanced configuration.

## License
MIT
