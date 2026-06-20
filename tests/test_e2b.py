"""Tests for E2BProvider."""
import pytest
from unittest.mock import MagicMock, patch


class TestE2BProvider:
    @pytest.fixture
    def provider(self):
        with patch("orchestrator.providers.e2b.Sandbox") as mock_sandbox:
            from orchestrator.providers.e2b import E2BProvider
            provider = E2BProvider(api_key="test-key")
            provider.sandboxes = {}
            yield provider

    def test_init_raises_on_missing_key(self):
        with patch("orchestrator.providers.e2b.os.getenv", return_value=None):
            from orchestrator.providers.e2b import E2BProvider
            with pytest.raises(ValueError, match="E2B API key is required"):
                E2BProvider()

    def test_create_sandbox(self, provider):
        with patch("orchestrator.providers.e2b.Sandbox") as mock_sandbox:
            mock_instance = MagicMock()
            mock_instance.sandbox_id = "sandbox-abc"
            mock_sandbox.return_value = mock_instance

            result = provider.create_sandbox("session-1")
            assert result == "sandbox-abc"
            assert "session-1" in provider.sandboxes
            assert provider.sandboxes["session-1"] is mock_instance

    def test_get_sandbox_exists(self, provider):
        provider.sandboxes["session-1"] = "sandbox-instance"
        assert provider.get_sandbox("session-1") == "sandbox-instance"

    def test_get_sandbox_nonexistent(self, provider):
        assert provider.get_sandbox("nope") is None

    def test_close_sandbox(self, provider):
        mock_sb = MagicMock()
        provider.sandboxes["session-1"] = mock_sb
        provider.close_sandbox("session-1")
        mock_sb.kill.assert_called_once()
        assert "session-1" not in provider.sandboxes

    def test_close_sandbox_nonexistent(self, provider):
        provider.close_sandbox("nope")

    def test_cleanup_all(self, provider):
        mock_sb1, mock_sb2 = MagicMock(), MagicMock()
        provider.sandboxes["s1"] = mock_sb1
        provider.sandboxes["s2"] = mock_sb2
        provider.cleanup_all()
        assert provider.sandboxes == {}
        mock_sb1.kill.assert_called_once()
        mock_sb2.kill.assert_called_once()
