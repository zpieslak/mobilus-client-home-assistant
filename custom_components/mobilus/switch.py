from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MobilusCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from mobilus_client.app import App as MobilusClientApp

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    devices = hass.data[DOMAIN][entry.entry_id]["switch_devices"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        [MobilusSwitch(device, client, coordinator) for device in devices],
    )


class MobilusSwitch(CoordinatorEntity[MobilusCoordinator], SwitchEntity):
    def __init__(self, device: dict[str, Any], client: MobilusClientApp, coordinator: MobilusCoordinator) -> None:
        self.client = client
        self.coordinator = coordinator
        self.device = device

        self._attr_name = device["name"]
        self._attr_unique_id = f"{DOMAIN}_{device['id']}"
        self._attr_icon = "mdi:power-socket-eu" if "plug" in device["name"].lower() else "mdi:toggle-switch"

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self.device['id']}"

    @property
    def name(self) -> str:
        return str(self.device["name"])

    @property
    def is_on(self) -> bool:
        device_status = self.coordinator.data.devices.get(self.device["id"])
        return device_status and device_status.state == "ON"

    async def async_turn_on(self, **kwargs: Any) -> None:
        _LOGGER.info("Turning ON switch %s", self.device["name"])
        try:
            await self.hass.async_add_executor_job(
                self.client.call,
                [("call_events", {"device_id": self.device["id"], "value": "ON"})],
            )
        except Exception as e:
            _LOGGER.error("Error turning ON switch %s: %s", self.device["name"], e)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        _LOGGER.info("Turning OFF switch %s", self.device["name"])
        try:
            await self.hass.async_add_executor_job(
                self.client.call,
                [("call_events", {"device_id": self.device["id"], "value": "OFF"})],
            )
        except Exception as e:
            _LOGGER.error("Error turning OFF switch %s: %s", self.device["name"], e)
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        coordinator_listener = self.coordinator.async_add_listener(self.async_write_ha_state)
        self.async_on_remove(coordinator_listener)
