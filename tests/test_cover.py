from __future__ import annotations

import json
from typing import TYPE_CHECKING, Generator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.cover import CoverDeviceClass, CoverEntityFeature
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from custom_components.mobilus.cover import (
    MobilusCover,
    async_setup_platform,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_logger() -> Generator[Mock, None, None]:
    with patch("custom_components.mobilus.cover._LOGGER", autospec=True) as mock_logger:
        yield mock_logger

@pytest.fixture
def mock_client() -> Generator[Mock, None, None]:
    with patch("custom_components.mobilus.cover.MobilusClientApp", autospec=True) as mock_client_class:
        mock_instance = mock_client_class.return_value
        yield mock_instance

@pytest.fixture
def mock_config() -> dict[str, str]:
    return {
        CONF_HOST: "test_host",
        CONF_USERNAME: "test_user",
        CONF_PASSWORD: "test_pass",
    }

@pytest.fixture
def mock_coordinator() -> Generator[Mock, None, None]:
    with patch("custom_components.mobilus.cover.MobilusCoordinator") as mock_coordinator_class:
        mock_instance = mock_coordinator_class.return_value
        mock_instance.async_config_entry_first_refresh = AsyncMock()
        mock_instance.async_request_refresh = AsyncMock()
        mock_instance.async_add_listener = Mock()
        yield mock_instance

@pytest.fixture
def mock_asyncio_sleep() -> Generator[Mock, None, None]:
    with patch("asyncio.sleep", return_value=None) as mock_sleep:
        yield mock_sleep

async def test_async_setup_platform(
        hass: HomeAssistant, mock_client: Mock, mock_config: dict[str, str], mock_coordinator: Mock) -> None:
    mock_client.call.return_value = json.dumps(
        [
          {
            "devices": [
              {
                "id": "0",
                "name": "Device SENSO",
                "type": 1,
              },
              {
                "id": "1",
                "name": "Device COSMO",
                "type": 2,
              },
              {
                "id": "2",
                "name": "Device CMR",
                "type": 3,
              },
              {
                "id": "3",
                "name": "Device CGR",
                "type": 4,
              },
              {
                "id": "4",
                "name": "Device SWITCH",
                "type": 5,
              },
              {
                "id": "5",
                "name": "Device SWITCH_NP",
                "type": 6,
              },
              {
                "id": "6",
                "name": "Device COSMO_CZR",
                "type": 7,
              },
              {
                "id": "7",
                "name": "Device COSMO_MZR",
                "type": 8,
              },
              {
                "id": "8",
                "name": "Device SENSO_Z",
                "type": 9,
              },
          ]},
        ],
    )

    async_add_entities = Mock()

    await async_setup_platform(hass, mock_config, async_add_entities)

    assert async_add_entities.call_count == 1
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 1

    entities = async_add_entities.call_args[0][0]
    assert len(entities) == 6
    assert isinstance(entities[0], MobilusCover)
    assert entities[0].device["id"] == "0"
    assert entities[1].device["id"] == "1"
    assert entities[2].device["id"] == "2"
    assert entities[3].device["id"] == "6"
    assert entities[4].device["id"] == "7"
    assert entities[5].device["id"] == "8"


async def test_async_setup_platform_no_devices(
        hass: HomeAssistant, mock_client: Mock, mock_config: dict[str, str],
        mock_coordinator: Mock, mock_logger: Mock) -> None:
    mock_client.call.return_value = json.dumps([])

    async_add_entities = Mock()
    await async_setup_platform(hass, mock_config, async_add_entities)

    mock_logger.warning.assert_called_once_with("No devices found in response. Exiting platform setup.")
    assert async_add_entities.call_count == 0
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 0


async def test_async_setup_platform_no_device_in_response(
        hass: HomeAssistant, mock_client: Mock, mock_config: dict[str, str],
        mock_coordinator: Mock, mock_logger: Mock) -> None:
    mock_client.call.return_value = json.dumps(
        [
          {
            "devices": [],
          },
        ],
    )

    async_add_entities = Mock()
    await async_setup_platform(hass, mock_config, async_add_entities)

    mock_logger.warning.assert_called_once_with("No devices found in the devices list.")
    assert async_add_entities.call_count == 0
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 0

async def test_async_setup_platform_no_supported_devices(
        hass: HomeAssistant, mock_client: Mock, mock_config: dict[str, str],
        mock_coordinator: Mock, mock_logger: Mock) -> None:

    mock_client.call.return_value = json.dumps(
        [
          {
            "devices": [
              {
                "id": "0",
                "name": "Device SWITCH",
                "type": 5,
              },
          ]},
        ],
    )

    async_add_entities = Mock()
    await async_setup_platform(hass, mock_config, async_add_entities)

    mock_logger.warning.assert_called_once_with("No supported devices found in the devices list.")
    assert async_add_entities.call_count == 0
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 0


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

def test_cover_is_closed_true(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.position = 0

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
    device_status.position = 100

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
    device_status.position = None

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
    device_status.position = 50

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
    device_status.position = None

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

async def test_cover_async_added_to_hass(hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Device SENSO",
        "type": 1,
    }
    cover = MobilusCover(device, mock_client, mock_coordinator)
    cover.hass = hass

    with patch.object(cover, "async_on_remove", new=AsyncMock()) as mock_async_on_remove:
        await cover.async_added_to_hass()

        mock_coordinator.async_add_listener.assert_called_once_with(cover.async_write_ha_state)
        mock_async_on_remove.assert_called_once_with(mock_coordinator.async_add_listener.return_value)
