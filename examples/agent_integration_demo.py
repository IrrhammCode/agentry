"""
Agentry Drop-in SDK & Middleware Examples.
Demonstrates how to add real-time TabPFN-3.5 guardrails to any autonomous agent
in 2 lines of Python code.
"""

import sys
import time
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentry import AgentryGuard, AgentHaltException

# Initialize the global Sentry Guardrail
guard = AgentryGuard(raise_on_kill=True)


# =========================================================================
# Pattern 1: Protecting Agent Tools with @guard.protect Decorator
# =========================================================================

@guard.protect(session_id="agent_coder_01", tool_name="bash")
def execute_bash(command: str) -> str:
    """Agent tool that executes shell commands."""
    print(f"Executing: {command}")
    # Simulate a broken command in an infinite loop
    if "git push" in command:
        return "fatal: Authentication failed for 'https://github.com/...'"
    return "Success"


# =========================================================================
# Pattern 2: Context Manager for Complex Multi-Step Agent Turns
# =========================================================================

def run_agent_turn_with_context(session_id: str, prompt: str):
    with guard.step(session_id=session_id, tool_name="llm_agent", input_text=prompt) as monitor:
        # Simulate agent execution
        time.sleep(0.05)
        response = "Completed task analysis."
        monitor.record_output(response)
        monitor.record_tokens(prompt=1800, completion=250)
    print(f"Step {monitor.decision.step_index}: Action -> {monitor.decision.action} (Risk: {monitor.decision.risk_level})")


# =========================================================================
# Pattern 3: LangChain / LangGraph Integration
# =========================================================================

def run_langchain_example():
    """
    To use with LangChain:
    
        from agentry.integrations import AgentryLangChainCallback
        from langchain.agents import AgentExecutor
        
        callback = AgentryLangChainCallback(session_id="langchain_run_01")
        executor = AgentExecutor(agent=agent, tools=tools, callbacks=[callback])
        executor.invoke({"input": "Fix the failing tests"})
    """
    from agentry.integrations import AgentryLangChainCallback
    cb = AgentryLangChainCallback(session_id="langchain_demo_01")
    cb.on_tool_start({"name": "pytest"}, "pytest -k test_core")
    cb.on_tool_end("1 passed in 0.2s")
    print("LangChain Callback recorded nominal tool step.")


# =========================================================================
# Main Demonstration Runner
# =========================================================================

if __name__ == "__main__":
    print("--- 1. Testing Nominal Execution ---")
    res = execute_bash("ls -la")
    print(f"Result: {res}\n")

    print("--- 2. Testing Context Manager ---")
    run_agent_turn_with_context("agent_coder_01", "Analyze repository structure")
    print()

    print("--- 3. Testing Autonomous KILL on Runaway Loop ---")
    try:
        for i in range(1, 8):
            print(f"Agent Attempt {i}...")
            execute_bash("git push origin main --force")
    except AgentHaltException as e:
        print("\n[SUCCESS] Agentry Sentry intercepted the runaway loop:")
        print(e)
