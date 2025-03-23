from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .device_state import MobilusDeviceState, MobilusDeviceStateList

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from mobilus_client.app import App as MobilusClientApp

_LOGGER = logging.getLogger(__name__)


class MobilusCoordinator(DataUpdateCoordinator[MobilusDeviceStateList]):
    def __init__(self, hass: HomeAssistant, client: MobilusClientApp, refresh_interval: int) -> None:
        self.client = client

        _LOGGER.info("Coordinator initialized with refresh interval %s", refresh_interval)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=refresh_interval),
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
                device_state["deviceId"]: MobilusDeviceState(
                    device_id=device_state["deviceId"],
                    event_number=device_state["eventNumber"],
                    value=device_state["value"],
                )
                for device_state in device_states
            },
        )
