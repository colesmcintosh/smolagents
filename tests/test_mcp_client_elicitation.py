from types import ModuleType
from unittest.mock import MagicMock

import pytest
import sys


def _install_fake_mcpadapt():
    """Install a minimal fake 'mcpadapt' package into sys.modules that captures MCPAdapt kwargs."""
    calls = {}

    core_mod = ModuleType("mcpadapt.core")

    class FakeMCPAdapt:
        def __init__(self, *args, **kwargs):
            calls["kwargs"] = kwargs

        def __enter__(self):
            return []

        def __exit__(self, *exc):
            return None

    core_mod.MCPAdapt = FakeMCPAdapt

    adapter_mod = ModuleType("mcpadapt.smolagents_adapter")

    class FakeSmolAgentsAdapter:
        def __init__(self, *args, **kwargs):
            pass

    adapter_mod.SmolAgentsAdapter = FakeSmolAgentsAdapter

    pkg = ModuleType("mcpadapt")

    sys.modules["mcpadapt"] = pkg
    sys.modules["mcpadapt.core"] = core_mod
    sys.modules["mcpadapt.smolagents_adapter"] = adapter_mod

    return calls


# Ignore FutureWarning about structured_output default value change: these tests
# focus on the adapter wiring and not on the default behavior.
@pytest.mark.filterwarnings("ignore:.*structured_output:FutureWarning")
class TestMcpClientElicitation:
    def test_elicitation_handler_param_forwarded(self):
        # Arrange
        calls = _install_fake_mcpadapt()
        from smolagents.mcp_client import MCPClient

        handler = MagicMock(name="elicitation_handler")
        server_parameters = MagicMock(name="server_parameters")

        # Act
        client = MCPClient(server_parameters, elicitation_handler=handler)

        # Assert MCPAdapt was constructed with our handler forwarded
        assert calls["kwargs"].get("elicitation_handler") is handler

        # Cleanup
        client.disconnect()

    def test_elicitation_handler_adapter_kwargs_forwarded(self):
        # Arrange
        calls = _install_fake_mcpadapt()
        from smolagents.mcp_client import MCPClient

        handler = MagicMock(name="elicitation_handler")
        server_parameters = MagicMock(name="server_parameters")

        # Act
        client = MCPClient(server_parameters, adapter_kwargs={"elicitation_handler": handler})

        # Assert
        assert calls["kwargs"].get("elicitation_handler") is handler

        client.disconnect()

    def test_elicitation_handler_param_overrides_adapter_kwargs(self):
        # Arrange
        calls = _install_fake_mcpadapt()
        from smolagents.mcp_client import MCPClient

        handler1 = MagicMock(name="adapter_kwargs_handler")
        handler2 = MagicMock(name="explicit_param_handler")
        server_parameters = MagicMock(name="server_parameters")

        # Act
        client = MCPClient(
            server_parameters,
            adapter_kwargs={"elicitation_handler": handler1},
            elicitation_handler=handler2,
        )

        # Assert explicit param wins
        assert calls["kwargs"].get("elicitation_handler") is handler2

        client.disconnect()
