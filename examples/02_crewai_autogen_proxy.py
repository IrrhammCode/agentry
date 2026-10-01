"""
Example 02: Zero-Code-Change Proxy Integration (CrewAI, AutoGen, OpenAI SDK).

Demonstrates how any agent framework (CrewAI, AutoGen, LangGraph, Cursor)
can be protected with 0 Python code modifications simply by setting
`base_url="http://localhost:8787/v1"`.
"""

import os
import sys

# Example showing how standard OpenAI SDK connects through Agentry Reverse Proxy
EXAMPLE_CODE = '''
from openai import OpenAI

# Simply configure base_url to route through Agentry's local Sentry Gateway (port 8787)
client = OpenAI(
    base_url="http://127.0.0.1:8787/v1",
    api_key=os.environ.get("OPENAI_API_KEY", "dummy-key-for-local-proxy"),
    default_headers={"X-Agentry-Session-ID": "crewai_analyst_session_01"}
)

# Standard chat completion invocation - identical to direct OpenAI API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an autonomous research agent."},
        {"role": "user", "content": "Analyze the sales quarterly figures."}
    ]
)

# Agentry transparently attaches governance metadata headers:
# - X-Agentry-Risk-Prob: 0.042
# - X-Agentry-Action: PASS
# - X-Agentry-Action-Entropy: 0.28
# - X-Agentry-Auto-Healed: true (if autonomic rewind triggered)
print("Agent Response:", response.choices[0].message.content)
'''

CREWAI_SNIPPET = '''
from crewai import Agent, Task, Crew, LLM

# Configure CrewAI LLM with Agentry Gateway
agentry_llm = LLM(
    model="openai/gpt-4o",
    base_url="http://127.0.0.1:8787/v1",
    api_key="sk-agentry-proxy"
)

coder = Agent(
    role="Senior Backend Engineer",
    goal="Fix failing unit tests",
    backstory="You fix bugs reliably without entering infinite loops.",
    llm=agentry_llm
)
'''


def main():
    print("=" * 65)
    print("Agentry Zero-Code-Change Reverse Proxy Integration")
    print("=" * 65)
    print("\n1. How to run the Agentry Proxy daemon:")
    print("   python run.py serve --port 8787")
    print("\n2. OpenAI Python Client Drop-in Usage:")
    print(EXAMPLE_CODE)
    print("3. CrewAI Framework Drop-in Usage:")
    print(CREWAI_SNIPPET)
    print("=" * 65)
    print("[OK] When an agent enters an infinite loop, Agentry's proxy automatically")
    print("     prunes poisoned turns, un-halts state, and resubmits to upstream LLM.")


if __name__ == "__main__":
    main()
