from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from mobilus_client.app import App as MobilusClientApp

_LOGGER = logging.getLogger(__name__)

@dataclass
class MobilusDeviceStateList:
    devices: dict[str, MobilusDeviceState]

@dataclass
class MobilusDeviceState:
    data: dict[str, Any]

    @cached_property
    def position(self) -> int | None:
        if self.data["value"].endswith("%"):
            return int(self.data["value"].rstrip("%"))

        # To prevent additonal polling to get the current position,
        # assume that opening shutter will be 100% and closing will be 0%.
        # If stop is sent the status will be synchronized
        if self.data["value"] == "UP":
            return 100
        if self.data["value"] == "DOWN":
            return 0

        return None

class MobilusCoordinator(DataUpdateCoordinator[MobilusDeviceStateList]):
    def __init__(self, hass: HomeAssistant, client: MobilusClientApp) -> None:
        self.client = client

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=600),
        )

    async def _async_update_data(self) -> MobilusDeviceStateList:
        response = await self.hass.async_add_executor_job(
            lambda: json.loads(self.client.call([("current_state", {})])),
        )

        if not response:
            raise UpdateFailed

        device_states = response[0].get("events", [])

        return MobilusDeviceStateList(
            {
                device_state["deviceId"]: MobilusDeviceState(device_state)
                for device_state in device_states
            },
        )
