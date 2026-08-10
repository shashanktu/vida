from agent_framework import Agent #type: ignore
from ..utils.clientConnection import get_client
from agent_framework.exceptions import ChatClientException #type: ignore
import asyncio
from vida.utils.config import Base_agent_config as baconfig
import inspect
from pprint import pformat
from vida.utils.crud_ops import AgentRunOps as aro
from vida.database.database import sessionlocal
from vida.models.requests.Agent_Run_request import AgentRunCreateRequest, AgentRunUpdateRequest
from vida.utils.preprocess import serialize_agent_response
from datetime import datetime, timezone
import json
from importlib.resources import files
# from agent_framework.middleware import SecurityAgentMiddleware #type: ignore

class Base_Agent:
    _instance = None
    name = None
    model = None
    AI_endpoint = None
    instructions = None
    tools = []
    context_providers = []
    agent_middleware = []
    run_middleware = []
    debug_context = False
    session = None

    def __init__(self):
        self._agent = Agent(
            client=get_client(model=self.model, endpoint=self.AI_endpoint),
            name=self.name,
            instructions=self.instructions,
            tools=self.tools,
            context_providers=self.context_providers,
            middleware=self.agent_middleware
        )
        self._session = self.session if self.session else self._agent.create_session()
        print(f"Session: {self._session}")
        print(f"[{self.name}] Initialized with model '{self.model}' and endpoint '{self.AI_endpoint}'")

    @classmethod
    def get_instance(cls):
        if "_instance" not in cls.__dict__ or cls.__dict__["_instance"] is None:
            cls._instance = cls()
        return cls._instance

    # async def run(self, prompt: str):
    async def run(self, prompt: str, retries: int = 2, tools: list = None, session=None, task_id = -1):
        issue = None
        response = None
        start_time = datetime.now(timezone.utc)
        try:
            for attempt in range(retries + 1):
                try:
                    response =  await self._agent.run(prompt,
                                                session=session if session else self._session,
                                                middleware=self.run_middleware,
                                                tools=tools or [],
                                                )
                    return response
                except ChatClientException as e:
                    if "Azure CLI" in str(e) and attempt < retries:
                        print(f"Azure CLI not ready, retrying in 2s... (attempt {attempt + 1})")
                        await asyncio.sleep(2)
                    else:
                        issue = str(e)
                        raise
        except Exception as e:
            issue = str(e)
            raise

        finally:
            end_time = datetime.now(timezone.utc)
            db=sessionlocal()
            status = "success" if response else "failed"
            agent_ids = json.loads(
                files("vida").joinpath("data/agent_id.json").read_text()
            )
            run_details = AgentRunCreateRequest(
                    agent_id=agent_ids.get(self.name),
                    task_id=task_id,
                    run_prompt=prompt,
                    run_status=status,
                    run_result=json.loads(response.text),
                    raw_run_result=serialize_agent_response(response),
                    run_logs_path="dummy_logs_path",
                    issue=issue,
                    start_time=start_time,
                    end_time=end_time,
                )



            aro().add_run(db=db, run=run_details)

            await self._clear_session()
            db.close()
        # return await self._agent.run(prompt)

    # async def _clear_session(self):
    #     for provider in self.context_providers:
    #         if hasattr(provider, "clear"):
    #             await provider.clear()
    async def _clear_session(self):
        if self.debug_context:
            await self._print_context()
        for provider in self.context_providers:
            if hasattr(provider, "clear") and not getattr(provider, "persist_across_sessions", False):
                await provider.clear()

    async def run_stream(self, prompt: str):
        """Streaming run — yields text chunks as they arrive"""
        try:
            async for chunk in self._agent.run(
                prompt,
                stream=True,
                session=self._session,
                middleware=self.run_middleware
            ):
                if chunk.text:
                    yield chunk.text
        finally:
            await self._clear_session()

    async def _print_context(self):
        print(f"\n{'='*60}")
        print(f"[{self.name}] Session Context Before Clear")
        print(f"{'='*60}")
        tools_data = {}
        state = self._session.state

        for provider in self.context_providers:
            source_id = getattr(provider, "source_id", provider.__class__.__name__)
            print(f"\n--- {provider.__class__.__name__} (source_id: '{source_id}') ---")

            messages = state.get(source_id, {}).get("messages", [])

            if not messages:
                print(f"  (no messages)")
                continue

            for msg in messages:
                role = getattr(msg, "role", "?")
                contents = getattr(msg, "contents", [])

                print(f"\n  [{role}]")
                for content in contents:
                    ctype = getattr(content, "type", "unknown")

                    if ctype == "text":
                        # plain text — user messages, assistant responses
                        print(f"    text       : {content.text}")

                    elif ctype == "function_call":
                        # sub-agent tool call — what the coordinator requested
                        print(f"    tool_call  : {content.name}({str(getattr(content, 'arguments', ''))})")

                    elif ctype == "function_result":
                        # sub-agent response — what came back
                        print(f"    tool_result: {str(getattr(content, 'result', content))}")

                    else:
                        # catch-all for reasoning, data, etc.
                        print(f"    [{ctype}]: {str(content)}")

        print(f"\n{'='*60}\n")



    async def describe_tools(self) -> dict:
        """Return detailed metadata for all registered tools."""

        tools_data = {}

        attr_names = [
            "_input_schema",
            "required",
            "title",
            "description",
            "approval_mode",
            "name",
        ]

        for index, tool_fn in enumerate(self.tools):

            tool_name = getattr(
                tool_fn,
                "name",
                getattr(tool_fn, "__name__", f"tool_{index}")
            )

            tool_info = {
                "metadata": {},
                "attributes": {},
            }

            # -------------------------
            # __ai_function__ metadata
            # -------------------------
            meta = getattr(tool_fn, "__ai_function__", None)

            if meta:

                # Dict metadata
                if isinstance(meta, dict):
                    tool_info["metadata"] = {
                        key: pformat(value)
                        for key, value in meta.items()
                    }

                # Object metadata
                else:
                    try:
                        tool_info["metadata"] = {
                            key: pformat(value)
                            for key, value in vars(meta).items()
                        }
                    except Exception as e:
                        tool_info["metadata"] = {
                            "error": str(e)
                        }

            # -------------------------
            # Selected object attributes
            # -------------------------
            for attr_name in attr_names:

                try:
                    value = getattr(tool_fn, attr_name)

                    if inspect.ismethod(value):
                        tool_info["attributes"][attr_name] = "<method>"

                    elif inspect.isfunction(value):
                        tool_info["attributes"][attr_name] = "<function>"

                    elif inspect.iscoroutinefunction(value):
                        tool_info["attributes"][attr_name] = "<async function>"

                    else:
                        tool_info["attributes"][attr_name] = pformat(value)

                except Exception as e:
                    tool_info["attributes"][attr_name] = f"<ERROR: {e}>"

            tools_data[tool_name] = tool_info

        return tools_data


