"""
CrewAI Step Callback Hook for Agentry.
Allows seamless integration into CrewAI agents and tasks:

    from crewai import Agent, Task, Crew
    from agentry.integrations import AgentryCrewHook
    
    hook = AgentryCrewHook(session_id="research_crew_01")
    
    agent = Agent(
        role="Researcher",
        goal="Investigate market trends",
        step_callback=hook
    )
"""

import time
import logging
from typing import Any, Optional

from agentry.guard import AgentryGuard, AgentHaltException, SentryDecision

logger = logging.getLogger("agentry.integrations.crewai")


class AgentryCrewHook:
    """
    CrewAI step hook for real-time monitoring and intervention.
    """

    def __init__(
        self,
        session_id: str,
        guard: Optional[AgentryGuard] = None,
        agent_role: str = "CrewAI-Agent",
        model_name: str = "crewai-llm",
        raise_on_kill: bool = True
    ):
        self.session_id = session_id
        self.guard = guard or AgentryGuard(raise_on_kill=raise_on_kill)
        self.agent_role = agent_role
        self.model_name = model_name

    def __call__(self, step_output: Any) -> SentryDecision:
        """
        Invoked by CrewAI after every agent step.
        """
        # Parse step output string and tool if available
        output_str = str(step_output)
        tool_name = "crewai_action"

        if hasattr(step_output, "tool"):
            tool_name = str(getattr(step_output, "tool"))
        if hasattr(step_output, "tool_input"):
            input_text = str(getattr(step_output, "tool_input"))
        else:
            input_text = output_str[:150]

        thought = ""
        if hasattr(step_output, "thought"):
            thought = str(getattr(step_output, "thought"))

        return self.guard.audit(
            session_id=self.session_id,
            tool_name=tool_name,
            input_text=input_text,
            output_text=output_str,
            thought_trace=thought,
            agent_role=self.agent_role,
            model_name=self.model_name
        )
