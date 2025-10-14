from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from custom_components.mobilus.const import DOMAIN
from custom_components.mobilus.switch import MobilusSwitch, async_setup_entry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

@pytest.fixture
def mock_async_add_entities() -> Mock:
    return Mock()

async def test_async_setup_entry(
    hass: HomeAssistant,
    mock_client: Mock,
    mock_coordinator: Mock,
    mock_config_entry: MockConfigEntry,
    mock_async_add_entities: Mock,
) -> None:
    device_cosmo = {
        "id": "1",
        "name": "Device COSMO",
        "type": 2,
    }
    device_switch = {
        "id": "0",
        "name": "Device SWITCH",
        "type": 5,
    }
    device_switch_np = {
        "id": "1",
        "name": "Device SWITCH_NP",
        "type": 6,
    }

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][mock_config_entry.entry_id] = {
        "client": mock_client,
        "coordinator": mock_coordinator,
        "devices": [
            device_cosmo,
            device_switch,
            device_switch_np,
        ],
    }

    await async_setup_entry(hass, mock_config_entry, mock_async_add_entities)

    assert mock_async_add_entities.call_with(
        [
            MobilusSwitch(device_switch, mock_client, mock_coordinator),
            MobilusSwitch(device_switch_np, mock_client, mock_coordinator),
        ],
    )


def test_switch_init(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert switch.coordinator == mock_coordinator
    assert switch.device == device
    assert switch.client == mock_client


def test_switch_unique_id(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert switch.unique_id == "mobilus_3"


def test_switch_name(mock_client: Mock, mock_coordinator: Mock) -> None:
    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert switch.name == "Test Switch"


def test_switch_is_on_true(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.is_on = True
    mock_coordinator.data.devices = {
        "3": device_status,
    }

    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert switch.is_on


def test_switch_is_on_false(mock_client: Mock, mock_coordinator: Mock) -> None:
    device_status = Mock()
    device_status.is_on = False
    mock_coordinator.data.devices = {
        "3": device_status,
    }

    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert not switch.is_on


def test_switch_is_on_no_device_status(mock_client: Mock, mock_coordinator: Mock) -> None:
    mock_coordinator.data.devices = {}

    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert not switch.is_on


def test_switch_is_on_none_device_status(mock_client: Mock, mock_coordinator: Mock) -> None:
    mock_coordinator.data.devices = {
        "3": None,
    }

    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)

    assert not switch.is_on


async def test_switch_async_turn_on(
    hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock,
) -> None:
    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)
    switch.hass = hass

    await switch.async_turn_on()

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "ON"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_switch_async_turn_off(
    hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock,
) -> None:
    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)
    switch.hass = hass

    await switch.async_turn_off()

    mock_client.call.assert_called_once_with(
        [("call_events", {"device_id": "3", "value": "OFF"})],
    )
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_switch_async_added_to_hass(
    hass: HomeAssistant, mock_client: Mock, mock_coordinator: Mock,
) -> None:
    device = {
        "id": "3",
        "name": "Test Switch",
        "type": 5,
    }
    switch = MobilusSwitch(device, mock_client, mock_coordinator)
    switch.hass = hass

    with patch.object(switch, "async_on_remove", new=Mock()) as mock_async_on_remove:
        await switch.async_added_to_hass()

        mock_coordinator.async_add_listener.assert_called_once_with(
            switch.async_write_ha_state,
        )
        mock_async_on_remove.assert_called_once_with(
            mock_coordinator.async_add_listener.return_value,
        )

