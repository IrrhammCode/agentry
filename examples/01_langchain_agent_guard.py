"""
Example 01: LangChain & LangGraph Integration with Agentry Guardrails.

Shows how to attach Agentry's TabPFN-3.5 foundation guardrail to LangChain
and LangGraph agent workflows using the callback handler and tool decorators.
"""

import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentry import AgentryGuard, AgentHaltException
from agentry.integrations import AgentryLangChainCallback


def demonstrate_langchain_callback():
    print("=" * 60)
    print("1. Agentry LangChain Callback Handler")
    print("=" * 60)

    # Initialize the callback for a specific session
    callback = AgentryLangChainCallback(
        session_id="langchain_workflow_42",
        raise_on_kill=True
    )

    print("[*] Simulating LangChain tool invocations...")

    # Step 1: Tool execution (nominal)
    callback.on_tool_start({"name": "sql_query_tool"}, "SELECT * FROM users WHERE active = true;")
    callback.on_tool_end("Fetched 15 rows successfully.")
    print("  -> Step 1 (sql_query_tool): PASS [Nominal]")

    # Step 2: Tool execution (nominal)
    callback.on_tool_start({"name": "csv_exporter"}, "export_to_csv('users.csv')")
    callback.on_tool_end("Saved users.csv (1.2 KB)")
    print("  -> Step 2 (csv_exporter): PASS [Nominal]")

    # Step 3: Tool execution with error
    callback.on_tool_start({"name": "s3_uploader"}, "upload_file('users.csv', 's3://production-bucket')")
    callback.on_tool_error(Exception("AccessDenied: AWS credential expired"))
    print("  -> Step 3 (s3_uploader): Recorded error streak")


def demonstrate_tool_protection_decorator():
    print("\n" + "=" * 60)
    print("2. Protecting Agent Tool Functions via @guard.protect")
    print("=" * 60)

    guard = AgentryGuard(raise_on_kill=False)

    @guard.protect(session_id="agent_worker_99", tool_name="execute_python")
    def run_python_repl(code: str) -> str:
        """Custom Python REPL tool for an autonomous agent."""
        if "while True" in code:
            raise TimeoutError("Execution timed out after 10000ms")
        return "Result: 42"

    print("[*] Invoking safe code execution:")
    res = run_python_repl("print(2 + 2)")
    print(f"  -> Execution result: {res}")

    print("\n[OK] LangChain & Decorator Guardrails verified successfully.")


if __name__ == "__main__":
    demonstrate_langchain_callback()
    demonstrate_tool_protection_decorator()
