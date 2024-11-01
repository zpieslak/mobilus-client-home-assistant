from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

import voluptuous
from homeassistant.components.cover import CoverDeviceClass, CoverEntity, CoverEntityFeature
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import config_validation
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from mobilus_client.app import App as MobilusClientApp
from mobilus_client.config import Config as MobilusClientConfig

from .const import DOMAIN, POSITION_SUPPORTED_DEVICES, SUPPORTED_DEVICES
from .coordinator import MobilusCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = voluptuous.Schema(
    {
        voluptuous.Required(CONF_HOST): config_validation.string,
        voluptuous.Required(CONF_USERNAME): config_validation.string,
        voluptuous.Required(CONF_PASSWORD): config_validation.string,
    },
    extra=voluptuous.ALLOW_EXTRA,
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    _discovery_info: DiscoveryInfoType | None = None,
) -> None:

    client_config = MobilusClientConfig(
        gateway_host=config[CONF_HOST],
        user_login=config[CONF_USERNAME],
        user_password=config[CONF_PASSWORD],
    )
    client = MobilusClientApp(client_config)

    # Retrieve devices list
    response = await hass.async_add_executor_job(
        lambda: json.loads(client.call([("devices_list", {})])),
    )

    if not response:
        _LOGGER.warning("No devices found in response. Exiting platform setup.")
        return

    devices = response[0].get("devices", [])

    if not devices:
        _LOGGER.warning("No devices found in the devices list.")
        return

    # Currently non cover devices are not supported
    supported_devices = [
        device for device in devices
        if device["type"] in SUPPORTED_DEVICES
    ]

    if not supported_devices:
        _LOGGER.warning("No supported devices found in the devices list.")
        return

    coordinator = MobilusCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
      [MobilusCover(device, client, coordinator) for device in supported_devices],
    )

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
        return CoverDeviceClass.SHUTTER

    @property
    def supported_features(self) -> CoverEntityFeature:
        supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
        )

        if self.device["type"] in POSITION_SUPPORTED_DEVICES:
            supported_features |= CoverEntityFeature.SET_POSITION

        return supported_features

    @property
    def is_closed(self) -> bool | None:
        device_status = self.coordinator.data.devices.get(self.device["id"])

        if not device_status or not isinstance(device_status.position, int):
          return None

        return device_status.position == 0

    @property
    def current_cover_position(self) -> int | None:
        device_status = self.coordinator.data.devices.get(self.device["id"])

        if not device_status or not isinstance(device_status.position, int):
          return None

        return device_status.position

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

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state),
        )
