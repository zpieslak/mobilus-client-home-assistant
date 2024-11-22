import datetime
import json
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.mobilus.coordinator import MobilusCoordinator
from custom_components.mobilus.device_state import MobilusDeviceStateList


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
                    {"deviceId": "device00", "value": "45%", "eventNumber": 8},
                    {"deviceId": "device01", "value": "50%:12$", "eventNumber": 7},
                    {"deviceId": "device02", "value": "50%:12$", "eventNumber": 8},
                    {"deviceId": "device03", "value": "UP", "eventNumber": 8},
                    {"deviceId": "device04", "value": "UP:49$", "eventNumber": 7},
                    {"deviceId": "device05", "value": "UP:49$", "eventNumber": 8},
                    {"deviceId": "device06", "value": "DOWN", "eventNumber": 8},
                    {"deviceId": "device07", "value": "DOWN:32$", "eventNumber": 7},
                    {"deviceId": "device08", "value": "DOWN:32$", "eventNumber": 8},
                    {"deviceId": "device09", "value": "56%:$", "eventNumber": 8},
                    {"deviceId": "device10", "value": "UNKNOWN", "eventNumber": 8},
                ],
            },
        ],
    )

    coordinator = MobilusCoordinator(hass, mock_client)
    data = await coordinator._async_update_data() # noqa: SLF001

    assert isinstance(data, MobilusDeviceStateList)
    assert len(data.devices) == 11
    assert data.devices["device00"].cover_position == 45
    assert data.devices["device01"].cover_position == 12
    assert data.devices["device02"].cover_position == 50
    assert data.devices["device03"].cover_position == 100
    assert data.devices["device04"].cover_position == 100
    assert data.devices["device05"].cover_position == 100
    assert data.devices["device06"].cover_position == 0
    assert data.devices["device07"].cover_position == 0
    assert data.devices["device08"].cover_position == 0
    assert data.devices["device09"].cover_position == 56
    assert data.devices["device10"].cover_position is None

    assert data.devices["device00"].tilt_position is None
    assert data.devices["device01"].tilt_position == 50
    assert data.devices["device02"].tilt_position == 12
    assert data.devices["device03"].tilt_position is None
    assert data.devices["device04"].tilt_position == 49
    assert data.devices["device05"].tilt_position == 49
    assert data.devices["device06"].tilt_position is None
    assert data.devices["device07"].tilt_position == 32
    assert data.devices["device08"].tilt_position == 32
    assert data.devices["device09"].tilt_position is None
    assert data.devices["device10"].tilt_position is None
