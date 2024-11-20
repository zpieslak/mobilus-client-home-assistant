from __future__ import annotations

import json
import logging
import re
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

    # The position of the device.
    # "50%" -> 50
    # "UP" -> 100
    # "DOWN" -> 0
    # "UP:56$" -> 100
    # "50%:56$" -> 50
    @cached_property
    def position(self) -> int | None:
        match = re.search(r"^(\d+)%", self.data["value"])

        if match:
            return int(match.group(1))

        # To prevent additonal polling to get the current position,
        # assume that opening shutter will be 100% and closing will be 0%.
        # If stop is sent the status will be synchronized
        if "UP" in self.data["value"]:
            return 100

        if "DOWN" in self.data["value"]:
            return 0

        return None

    # The tilt position of the device.
    # "50%:100$" -> 100
    # "DOWN:49$" -> 49
    @cached_property
    def tilt_position(self) -> int | None:
        match = re.search(r":(\d+)\$", self.data["value"])

        if match:
            return int(match.group(1))

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
