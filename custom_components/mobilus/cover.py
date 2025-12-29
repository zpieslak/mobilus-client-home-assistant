from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.cover import CoverDeviceClass, CoverEntity, CoverEntityFeature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COVER_DEVICES, COVER_POSITION_DEVICES, COVER_TILT_DEVICES, DOMAIN
from .coordinator import MobilusCoordinator
from .device import MobilusDevice

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
    devices = hass.data[DOMAIN][entry.entry_id]["devices"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        MobilusCover(device, client, coordinator)
        for device in devices if device["type"] in COVER_DEVICES
    ])

class MobilusCover(CoordinatorEntity[MobilusCoordinator], CoverEntity):
    def __init__(self, device: dict[str, Any], client: MobilusClientApp, coordinator: MobilusCoordinator) -> None:
        self.client = client
        self.coordinator = coordinator
        self.device = device

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self.device['id']}"

    @property
    def name(self) -> str:
        return str(self.device["name"])

    @property
    def device_class(self) -> CoverDeviceClass:
        if self.device["type"] == MobilusDevice.CGR:
            return CoverDeviceClass.GARAGE
        return CoverDeviceClass.SHUTTER

    @property
    def supported_features(self) -> CoverEntityFeature:
        supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
        )

        if self.device["type"] in COVER_POSITION_DEVICES:
            supported_features |= CoverEntityFeature.SET_POSITION

        if self.device["type"] in COVER_TILT_DEVICES:
            supported_features |= (
                CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
            )

        return supported_features

    @property
    def is_closed(self) -> bool | None:
        device_status = self.coordinator.data.devices.get(self.device["id"])

        if not device_status or not isinstance(device_status.cover_position, int):
          return None

        return device_status.cover_position == 0

    @property
    def current_cover_position(self) -> int | None:
        device_status = self.coordinator.data.devices.get(self.device["id"])

        if not device_status or not isinstance(device_status.cover_position, int):
          return None

        return device_status.cover_position

    @property
    def current_tilt_position(self) -> int | None:
        device_status = self.coordinator.data.devices.get(self.device["id"])

        if not device_status or not isinstance(device_status.tilt_position, int):
            return None

        return device_status.tilt_position

    async def async_open_cover(self, **_kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Opening cover %s", self.device["name"])

        await self.hass.async_add_executor_job(
            self.client.call,
            [("call_events", {"device_id": self.device["id"], "value": "UP"})],
        )
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **_kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Closing cover %s", self.device["name"])

        await self.hass.async_add_executor_job(
            self.client.call,
            [("call_events", {"device_id": self.device["id"], "value": "DOWN"})],
        )
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **_kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Stopping cover %s", self.device["name"])

        await self.hass.async_add_executor_job(
            self.client.call,
            [("call_events", {"device_id": self.device["id"], "value": "STOP"})],
        )

        # Added arbitrary delay as proper state is returned after a while
        await asyncio.sleep(15)
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Setting cover %s position to %s", self.device["name"], kwargs["position"])

        await self.hass.async_add_executor_job(
            self.client.call,
            [("call_events", {"device_id": self.device["id"], "value": f"{kwargs['position']}%"})],
        )

        await self.coordinator.async_request_refresh()

    async def async_open_cover_tilt(self, **_kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Opening tilt for cover %s", self.device["name"])
        await self.async_set_cover_tilt_position(tilt_position=100)

    async def async_close_cover_tilt(self, **_kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Closing tilt for cover %s", self.device["name"])
        await self.async_set_cover_tilt_position(tilt_position=0)

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None: # noqa: ANN401
        _LOGGER.info("Setting tilt position for cover %s to %s", self.device["name"], kwargs["tilt_position"])

        await self.hass.async_add_executor_job(
            self.client.call,
            [("call_events", {"device_id": self.device["id"], "value": f"{kwargs['tilt_position']}%"})],
        )
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        # Add a listener to the coordinator to update the entity's state on data changes
        coordinator_listener = self.coordinator.async_add_listener(self.async_write_ha_state)

        # Register the listener for cleanup when the entity is removed from Home Assistant
        self.async_on_remove(coordinator_listener)
