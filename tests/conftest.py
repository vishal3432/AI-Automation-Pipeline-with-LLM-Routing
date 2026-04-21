import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
