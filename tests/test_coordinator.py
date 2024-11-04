import datetime
import json
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    UpdateFailed,
)

from custom_components.mobilus.coordinator import (
    MobilusCoordinator,
    MobilusDeviceStateList,
)


@pytest.fixture
def mock_client() -> Generator[Mock, None, None]:
    with patch("mobilus_client.app.App", autospec=True) as mock_client_class:
        mock_instance = mock_client_class.return_value
        yield mock_instance

def test_coordinator_init(hass: HomeAssistant, mock_client: Mock) -> None:
    coordinator = MobilusCoordinator(hass, mock_client)

    assert coordinator.client == mock_client
    assert coordinator.name == "mobilus_coordinator"
    assert coordinator.update_interval == datetime.timedelta(seconds=600)

async def test_coordinator_async_update_data_no_devices(hass: HomeAssistant, mock_client: Mock) -> None:
    mock_client.call.return_value = json.dumps([])

    coordinator = MobilusCoordinator(hass, mock_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data() # noqa: SLF001


async def test_coordinator_async_update_data_success(hass: HomeAssistant, mock_client: Mock) -> None:
    mock_client.call.return_value = json.dumps(
        [
            {
                "events": [
                    {"deviceId": "device1", "value": "50%"},
                    {"deviceId": "device2", "value": "UP"},
                    {"deviceId": "device3", "value": "DOWN"},
                    {"deviceId": "device4", "value": "UNKNOWN"},
                ],
            },
        ],
    )

    coordinator = MobilusCoordinator(hass, mock_client)
    data = await coordinator._async_update_data() # noqa: SLF001

    assert isinstance(data, MobilusDeviceStateList)
    assert len(data.devices) == 4
    assert data.devices["device1"].position == 50
    assert data.devices["device2"].position == 100
    assert data.devices["device3"].position == 0
    assert data.devices["device4"].position is None

