from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mobilus import async_migrate_entry, async_setup_entry, async_unload_entry
from custom_components.mobilus.const import DOMAIN, PLATFORMS

if TYPE_CHECKING:
    from collections.abc import Generator

    from homeassistant.core import HomeAssistant

@pytest.fixture
def mock_forward_entry_setups(hass: HomeAssistant) -> Generator[AsyncMock, None, None]:
    with patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()) as mock_forward_entry_setups:
        yield mock_forward_entry_setups

@pytest.fixture
def mock_unload_platforms(hass: HomeAssistant) -> Generator[AsyncMock, None, None]:
    with patch.object(hass.config_entries, "async_unload_platforms", new=AsyncMock()) as mock_unload_platforms:
        yield mock_unload_platforms

@pytest.fixture
def mock_logger() -> Generator[Mock, None, None]:
    with patch("custom_components.mobilus._LOGGER", autospec=True) as mock_logger:
        yield mock_logger

@pytest.fixture
def mock_config_entry_v1() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data = {
            "host": "test_host",
            "username": "test_user",
            "password": "test_pass",
        },
    )

async def test_async_setup_entry(
        hass: HomeAssistant, mock_client: Mock, mock_config_entry: MockConfigEntry,
        mock_coordinator: Mock, mock_forward_entry_setups: AsyncMock) -> None:

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

    result = await async_setup_entry(hass, mock_config_entry)

    assert result
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 1
    mock_forward_entry_setups.assert_called_once_with(mock_config_entry, PLATFORMS)
    assert(hass.data[DOMAIN][mock_config_entry.entry_id]) == {
        "client": mock_client,
        "coordinator": mock_coordinator,
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
                "id": "7", "name": "Device COSMO_MZR",
                "type": 8,
            },
            {
                "id": "8",
                "name": "Device SENSO_Z",
                "type": 9,
            },
        ],
    }

async def test_async_setup_entry_no_devices(
        hass: HomeAssistant, mock_client: Mock, mock_config_entry: MockConfigEntry,
        mock_coordinator: Mock, mock_forward_entry_setups: AsyncMock, mock_logger: Mock) -> None:

    mock_client.call.return_value = json.dumps([])

    result = await async_setup_entry(hass, mock_config_entry)

    assert not result
    mock_logger.warning.assert_called_once_with("No devices found in response.")
    assert(hass.data[DOMAIN]) == {}
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 0
    assert mock_forward_entry_setups.call_count == 0


async def test_async_setup_entry_no_device_in_response(
        hass: HomeAssistant, mock_client: Mock, mock_config_entry: MockConfigEntry,
        mock_coordinator: Mock, mock_forward_entry_setups: AsyncMock, mock_logger: Mock) -> None:

    mock_client.call.return_value = json.dumps(
        [
          {
            "devices": [],
          },
        ],
    )

    await async_setup_entry(hass, mock_config_entry)

    mock_logger.warning.assert_called_once_with("No devices found in the devices list.")
    assert(hass.data[DOMAIN]) == {}
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 0
    assert mock_forward_entry_setups.call_count == 0

async def test_async_setup_entry_no_supported_devices(
        hass: HomeAssistant, mock_client: Mock, mock_config_entry: MockConfigEntry,
        mock_coordinator: Mock, mock_forward_entry_setups: AsyncMock, mock_logger: Mock) -> None:

    mock_client.call.return_value = json.dumps(
        [
          {
            "devices": [
              {
                "id": "0",
                "name": "Device CGR",
                "type": 4,
              },
          ]},
        ],
    )

    result = await async_setup_entry(hass, mock_config_entry)

    assert not result
    mock_logger.warning.assert_called_once_with("No supported devices found in the devices list.")
    assert mock_coordinator.async_config_entry_first_refresh.call_count == 0
    assert mock_forward_entry_setups.call_count == 0

async def test_async_setup_unload_entry(
        hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_unload_platforms: AsyncMock) -> None:

    mock_unload_platforms.return_value = True
    hass_domain = {
        "client": Mock(),
        "coordinator": Mock(),
        "devices": [],
    }
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][mock_config_entry.entry_id] = hass_domain

    result = await async_unload_entry(hass, mock_config_entry)

    assert result
    assert mock_unload_platforms.call_count == 1
    assert not hass.data[DOMAIN]

async def test_async_setup_unload_entry_false(
        hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_unload_platforms: AsyncMock) -> None:

    mock_unload_platforms.return_value = False
    hass_domain = {
        "client": Mock(),
        "coordinator": Mock(),
        "devices": [],
    }
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][mock_config_entry.entry_id] = hass_domain

    result = await async_unload_entry(hass, mock_config_entry)

    assert not result
    assert mock_unload_platforms.call_count == 1
    assert hass.data[DOMAIN][mock_config_entry.entry_id] == hass_domain

async def test_async_migrate_entry(
        hass: HomeAssistant, mock_config_entry_v1: MockConfigEntry) -> None:

    mock_config_entry_v1.add_to_hass(hass)

    result = await async_migrate_entry(hass, mock_config_entry_v1)

    assert result
    assert mock_config_entry_v1.data == {
        "host": "test_host",
        "username": "test_user",
        "password": "test_pass",
        "refresh_interval": 600,
    }
