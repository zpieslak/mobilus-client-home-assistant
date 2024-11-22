from __future__ import annotations

from typing import TYPE_CHECKING, Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.cover import CoverDeviceClass, CoverEntityFeature

from custom_components.mobilus.const import DOMAIN
from custom_components.mobilus.cover import MobilusCover, async_setup_entry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_async_add_entities() -> Mock:
    return Mock()

@pytest.fixture
def mock_asyncio_sleep() -> Generator[Mock, None, None]:
    with patch("asyncio.sleep", return_value=None) as mock_sleep:
        yield mock_sleep

async def test_async_setup_entry(
        hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock,
        mock_config_entry: MockConfigEntry, mock_async_add_entities: Mock) -> None:

    device_senso = {
        "id": "0",
        "name": "Device SENSO",
        "type": 1,
    }
    device_cosmo = {
        "id": "1",
        "name": "Device COSMO",
        "type": 2,
    }

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][mock_config_entry.entry_id] = {
        "client": mock_client,
        "coordinator": mock_coordinator,
        "devices": [
            device_senso,
            device_cosmo,
        ],
    }

    await async_setup_entry(hass, mock_config_entry, mock_async_add_entities)

    assert mock_async_add_entities.call_with(
      [
          MobilusCover(device_senso, mock_client, mock_coordinator),
          MobilusCover(device_cosmo, mock_client, mock_coordinator),
      ],
    )

def test_cover_init(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "0",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.coordinator == mock_coordinator
    assert cover.device == device
    assert cover.client == mock_client

def test_cover_unique_id(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.unique_id == "mobilus_3"

def test_cover_name(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.name == "Device SENSO"

def test_cover_device_class(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.device_class == CoverDeviceClass.SHUTTER

def test_cover_supported_features(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device CMR",
        "type": 3,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.supported_features == (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
    )

def test_cover_supported_features_senso(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.supported_features == (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

def test_cover_supported_features_senso_z(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO_Z",
        "type": 9,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.supported_features == (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

def test_cover_supported_features_cosmo_czr(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.supported_features == (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.OPEN_TILT
        | CoverEntityFeature.CLOSE_TILT
        | CoverEntityFeature.SET_TILT_POSITION
    )

def test_cover_is_closed_true(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.cover_position = 0

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.is_closed

def test_cover_is_closed_false(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.cover_position = 100

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert not cover.is_closed

def test_cover_is_closed_no_device_status(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = None

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert not cover.is_closed

def test_cover_is_closed_no_position(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.cover_position = None

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert not cover.is_closed

def test_cover_current_cover_position(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.cover_position = 50

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.current_cover_position == 50

def test_cover_current_cover_position_no_device_status(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = None

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.current_cover_position is None

def test_cover_current_cover_position_no_position(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.cover_position = None

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.current_cover_position is None

def test_cover_current_tilt_position(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.tilt_position = 50

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.current_tilt_position == 50

def test_cover_current_tilt_position_no_device_status(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = None

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.current_tilt_position is None

def test_cover_current_tilt_position_no_tilt_position(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.tilt_position = None

    mock_coordinator.data.devices = {
        "3": device_status,
    }
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)

    assert cover.current_tilt_position is None

async def test_cover_async_open_cover(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    await cover.async_open_cover()

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "UP"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()

async def test_cover_async_close_cover(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    await cover.async_close_cover()

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "DOWN"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()

@pytest.mark.usefixtures("mock_asyncio_sleep")
async def test_cover_async_stop_cover(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    await cover.async_stop_cover()

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "STOP"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()

async def test_cover_async_set_cover_position(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    await cover.async_set_cover_position(position=50)

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "50%"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()

async def test_cover_async_open_cover_tilt(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    with patch.object(cover, "async_set_cover_tilt_position", new=AsyncMock()) as mock_async_set_cover_tilt_position:
        await cover.async_open_cover_tilt()

        mock_async_set_cover_tilt_position.assert_called_once_with(tilt_position=100)

async def test_cover_async_close_cover_tilt(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    with patch.object(cover, "async_set_cover_tilt_position", new=AsyncMock()) as mock_async_set_cover_tilt_position:
        await cover.async_close_cover_tilt()

        mock_async_set_cover_tilt_position.assert_called_once_with(tilt_position=0)

async def test_cover_async_set_cover_tilt_position(
        hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device COSMO_CZR",
        "type": 7,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    await cover.async_set_cover_tilt_position(tilt_position=50)

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "50%"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()

async def test_cover_async_added_to_hass(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    with patch.object(cover, "async_on_remove", new=Mock()) as mock_async_on_remove:
        await cover.async_added_to_hass()

        mock_coordinator.async_add_listener.assert_called_once_with(cover.async_write_ha_state)
        mock_async_on_remove.assert_called_once_with(mock_coordinator.async_add_listener.return_value)
