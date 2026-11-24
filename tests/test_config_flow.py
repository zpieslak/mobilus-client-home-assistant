from __future__ import annotations

from typing import TYPE_CHECKING, Any, get_type_hints
from unittest.mock import patch

import pytest
import voluptuous as vol
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER, ConfigFlow
from homeassistant.data_entry_flow import FlowResultType

from custom_components.mobilus.config_flow import MobilusConfigFlow

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.fixture
def flow(hass: HomeAssistant) -> MobilusConfigFlow:
    config_flow = MobilusConfigFlow()
    config_flow.hass = hass
    config_flow.context = {"source": SOURCE_USER}
    return config_flow


@pytest.fixture
def user_input() -> dict[str, Any]:
    return {
        "host": "GATEWAY_HOST",
        "username": "USER_LOGIN",
        "password": "USER_PASSWORD",
        "refresh_interval": 600,
    }


async def test_user_form(flow: MobilusConfigFlow, user_input: dict[str, Any]) -> None:
    result = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = result["data_schema"]
    assert schema is not None
    assert isinstance(schema, get_type_hints(ConfigFlow.async_show_form)["data_schema"])
    assert {key.schema for key in schema.schema} == set(user_input)
    assert all(isinstance(key, vol.Required) for key in schema.schema)
    assert schema({key: value for key, value in user_input.items() if key != "refresh_interval"}) == user_input


@pytest.mark.parametrize("field", ["host", "username", "password", "refresh_interval"])
async def test_user_form_rejects_invalid_types(
    flow: MobilusConfigFlow, user_input: dict[str, Any], field: str,
) -> None:
    result = await flow.async_step_user()
    schema = result["data_schema"]
    assert schema is not None
    user_input[field] = []

    with pytest.raises(vol.Invalid):
        schema(user_input)


async def test_create_entry(flow: MobilusConfigFlow, user_input: dict[str, Any]) -> None:
    result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "GATEWAY_HOST"
    assert result["data"] == user_input
    assert result["version"] == 2


async def test_reconfigure_form(
    hass: HomeAssistant, flow: MobilusConfigFlow, mock_config_entry: MockConfigEntry,
) -> None:
    mock_config_entry.add_to_hass(hass)
    flow.context = {"source": SOURCE_RECONFIGURE, "entry_id": mock_config_entry.entry_id}

    result = await flow.async_step_reconfigure()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    schema = result["data_schema"]
    assert schema is not None
    assert isinstance(schema, get_type_hints(ConfigFlow.async_show_form)["data_schema"])
    assert schema({}) == dict(mock_config_entry.data)


async def test_reconfigure_entry(
    hass: HomeAssistant, flow: MobilusConfigFlow, mock_config_entry: MockConfigEntry,
    user_input: dict[str, Any],
) -> None:
    mock_config_entry.add_to_hass(hass)
    flow.context = {"source": SOURCE_RECONFIGURE, "entry_id": mock_config_entry.entry_id}
    user_input["refresh_interval"] = 120

    with patch.object(hass.config_entries, "async_schedule_reload") as reload_entry:
        result = await flow.async_step_reconfigure(user_input)

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert dict(mock_config_entry.data) == user_input
    reload_entry.assert_called_once_with(mock_config_entry.entry_id)


async def test_reconfigure_missing_entry(flow: MobilusConfigFlow) -> None:
    flow.context = {"source": SOURCE_RECONFIGURE, "entry_id": "missing_entry"}

    result = await flow.async_step_reconfigure()

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "entry_not_found"
