"""
LangChain / LangGraph Callback Handler for Agentry.
Allows 1-line integration into LangChain AgentExecutor and LangGraph workflows:

    from agentry.integrations import AgentryLangChainCallback
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[AgentryLangChainCallback(session_id="run_42")]
    )
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union
from uuid import UUID

from agentry.guard import AgentryGuard, AgentHaltException, SentryDecision

logger = logging.getLogger("agentry.integrations.langchain")

# Gracefully support environments with or without langchain_core installed
try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    class BaseCallbackHandler:  # type: ignore
        """Fallback stub when langchain_core is not installed."""
        pass


class AgentryLangChainCallback(BaseCallbackHandler):
    """
    Agentry In-Line Guardrail Callback for LangChain & LangGraph.
    Monitors tool turns, tracks token growth and repetition, and triggers
    TabPFN-3.5 risk assessments to halt runaway agents.
    """

    def __init__(
        self,
        session_id: str,
        guard: Optional[AgentryGuard] = None,
        agent_role: str = "LangChain-Agent",
        model_name: str = "gpt-4o",
        raise_on_kill: bool = True
    ):
        super().__init__()
        self.session_id = session_id
        self.guard = guard or AgentryGuard(raise_on_kill=raise_on_kill)
        self.agent_role = agent_role
        self.model_name = model_name
        self.raise_on_kill = raise_on_kill

        self._current_tool: Optional[str] = None
        self._current_input: str = ""
        self._tool_start_time: float = 0.0
        self._last_prompt_tokens: int = 0
        self._last_completion_tokens: int = 0
        self._last_thought: str = ""

    def on_llm_end(self, response: Any, *, run_id: Optional[UUID] = None, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        """Capture token usage and thoughts from LLM generation."""
        try:
            if hasattr(response, "llm_output") and response.llm_output:
                token_usage = response.llm_output.get("token_usage", {})
                self._last_prompt_tokens = token_usage.get("prompt_tokens", 0)
                self._last_completion_tokens = token_usage.get("completion_tokens", 0)

            # Capture thought trace from the first generation if available
            if hasattr(response, "generations") and response.generations:
                first_gen = response.generations[0][0]
                text = getattr(first_gen, "text", "")
                self._last_thought = text[:200]
        except Exception as e:
            logger.debug("Failed parsing LLM token usage: %s", e)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *, run_id: Optional[UUID] = None, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        """Register the start of an agent tool execution."""
        self._current_tool = serialized.get("name", "tool")
        self._current_input = str(input_str)
        self._tool_start_time = time.time()

    def on_tool_end(self, output: str, *, run_id: Optional[UUID] = None, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        """Intercept tool completion, audit via TabPFN, and halt if runaway."""
        latency_ms = (time.time() - self._tool_start_time) * 1000.0 if self._tool_start_time else 800.0
        tool_name = self._current_tool or "tool"
        
        self.guard.audit(
            session_id=self.session_id,
            tool_name=tool_name,
            input_text=self._current_input,
            output_text=str(output),
            prompt_tokens=self._last_prompt_tokens,
            completion_tokens=self._last_completion_tokens,
            thought_trace=self._last_thought,
            agent_role=self.agent_role,
            model_name=self.model_name,
            latency_ms=latency_ms
        )

    def on_tool_error(self, error: BaseException, *, run_id: Optional[UUID] = None, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> None:
        """Intercept tool errors and update error streak telemetry."""
        latency_ms = (time.time() - self._tool_start_time) * 1000.0 if self._tool_start_time else 800.0
        tool_name = self._current_tool or "tool"
        
        self.guard.audit(
            session_id=self.session_id,
            tool_name=tool_name,
            input_text=self._current_input,
            output_text=f"{type(error).__name__}: {str(error)}",
            prompt_tokens=self._last_prompt_tokens,
            completion_tokens=self._last_completion_tokens,
            thought_trace=self._last_thought,
            agent_role=self.agent_role,
            model_name=self.model_name,
            latency_ms=latency_ms
        )
