"""
Global Pytest Fixtures & Configuration for Agentry Test Suite.
Enables instant local execution without external network latency or API rate limits.
"""

import os
import pytest

# Ensure local test runs are deterministic, fast, and self-contained
os.environ["TABPFN_OFFLINE_MODE"] = "1"
os.environ["SENTRY_PROVIDER"] = "rule"


@pytest.fixture(autouse=True, scope="session")
def configure_test_environment():
    """Configures deterministic offline environment for tests."""
    os.environ["TABPFN_OFFLINE_MODE"] = "1"
    os.environ["SENTRY_PROVIDER"] = "rule"
    yield
