from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import voluptuous
from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import config_validation

from mobilus_client.app import App as MobilusClientApp
from mobilus_client.config import Config as MobilusClientConfig

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = voluptuous.Schema(
    {
        voluptuous.Required(CONF_HOST): config_validation.string,
        voluptuous.Required(CONF_USERNAME): config_validation.string,
        voluptuous.Required(CONF_PASSWORD): config_validation.string,
    },
    extra=voluptuous.ALLOW_EXTRA,
)

async def async_setup_platform(
    _hass: HomeAssistant,
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
    devices = json.loads(
        client.call([("devices_list", {})]),
    )

    if not devices:
        LOGGER.warning("No devices found in response. Exiting platform setup.")
        return

    covers = [MobilusClientCover(client, device) for device in devices[0].get("devices")]

    async_add_entities(covers)

class MobilusClientCover(CoverEntity): # type: ignore[misc]
    def __init__(self, client: MobilusClientApp, device: dict[str, Any]) -> None:
        self.client = client
        self.device_name = str(device["name"])
        self.device_id = str(device["id"])

    @property
    def name(self) -> str:
        return self.device_name

    @property
    def unique_id(self) -> str:
        return f"mobilus_client_{self.device_id}"

    @property
    def supported_features(self) -> CoverEntityFeature:
        return (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.SET_POSITION
            | CoverEntityFeature.STOP
        )

    @property
    def is_closed(self) -> bool | None:
        """NOTE: Shutter does not report its current position."""
        return None

    async def async_open_cover(self, **_kwargs: Any) -> None: # noqa: ANN401
        await self.async_set_cover_position(position=100)

    async def async_close_cover(self, **_kwargs: Any) -> None: # noqa: ANN401
        await self.async_set_cover_position(position=0)

    async def async_stop_cover(self, **_kwargs: Any) -> None: # noqa: ANN401
        LOGGER.info("Stopping cover %s", self.device_name)

        self.client.call(
            [("call_events", {"device_id": self.device_id, "value": "STOP"})],
        )

    async def async_set_cover_position(self, position: int, **_kwargs: Any) -> None: # noqa: ANN401
        LOGGER.info("Setting cover %s position to %s", self.device_name, position)

        self.client.call(
            [("call_events", {"device_id": self.device_id, "value": f"{position}%"})],
        )
