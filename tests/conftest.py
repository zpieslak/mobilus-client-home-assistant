from collections.abc import Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mobilus.const import DOMAIN


@pytest.fixture
def mock_client() -> Generator[Mock, None, None]:
    with patch("custom_components.mobilus.MobilusClientApp", autospec=True) as mock_client_class:
        mock_instance = mock_client_class.return_value
        yield mock_instance

@pytest.fixture
def mock_coordinator() -> Generator[Mock, None, None]:
    with patch("custom_components.mobilus.MobilusCoordinator") as mock_coordinator_class:
        mock_instance = mock_coordinator_class.return_value
        mock_instance.async_config_entry_first_refresh = AsyncMock()
        mock_instance.async_request_refresh = AsyncMock()
        mock_instance.async_add_listener = Mock()
        yield mock_instance

@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data = {
            "host": "test_host",
            "username": "test_user",
            "password": "test_pass",
            "refresh_interval": 600,
        },
    )
