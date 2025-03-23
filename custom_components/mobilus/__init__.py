from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from mobilus_client.app import App as MobilusClientApp
from mobilus_client.config import Config as MobilusClientConfig

from .const import DOMAIN, PLATFORMS, SUPPORTED_DEVICES
from .coordinator import MobilusCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client_config = MobilusClientConfig(
        gateway_host=entry.data["host"],
        user_login=entry.data["username"],
        user_password=entry.data["password"],
    )
    client = MobilusClientApp(client_config)

    # Retrieve devices list
    response = await hass.async_add_executor_job(
        lambda: json.loads(client.call([("devices_list", {})])),
    )

    if not response:
        _LOGGER.warning("No devices found in response.")
        return False

    devices = response[0].get("devices", [])

    if not devices:
        _LOGGER.warning("No devices found in the devices list.")
        return False

    # Currently non cover devices are not supported
    supported_devices = [
        device for device in devices
        if device["type"] in SUPPORTED_DEVICES
    ]

    if not supported_devices:
        _LOGGER.warning("No supported devices found in the devices list.")
        return False

    coordinator = MobilusCoordinator(hass, client, entry.data["refresh_interval"])

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
        "devices": supported_devices,
    }

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    if config_entry.version == 1:
        data = dict(config_entry.data)

        if "refresh_interval" not in data:
            data["refresh_interval"] = 600

    hass.config_entries.async_update_entry(config_entry, data=data)

    return True
