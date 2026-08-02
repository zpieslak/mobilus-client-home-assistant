# AGENTS.md

Project-specific rules for agents working in `mobilus-client-home-assistant`.

## Core Constraints

- This is a Home Assistant custom integration for controlling a user-provided local Mobilus Cosmo GTW gateway through `mobilus-client`; do not add cloud, public-internet, or vendor-hosted runtime behavior.
- Preserve Home Assistant integration compatibility: domain `mobilus`, `iot_class` `local_polling`, config flow setup/reconfigure, and platforms in `const.py`.
- Keep config keys compatibility-sensitive: `host`, `username`, `password`, and `refresh_interval`; preserve the default refresh interval `600` unless intentionally changing user-visible behavior.
- Keep Home Assistant and `mobilus-client` version requirements synchronized across `pyproject.toml`, `custom_components/mobilus/manifest.json`, `hacs.json`, and README when they change.
- Maintain 100% coverage for non-generated integration code; ensure changed modules are imported by tests so coverage cannot hide untested files, and keep Hassfest expectations green for manifest, metadata, translations, and platform changes.

## Architecture

```text
Home Assistant config flow (config_flow.py) creates ConfigEntry
  -> __init__.py creates MobilusClientApp, loads devices_list, stores hass.data, forwards platforms
  -> MobilusCoordinator polls current_state via DataUpdateCoordinator
       -> device_state.py parses Mobilus values into HA-facing state
  -> cover.py and switch.py expose entities and send call_events commands
  <-> local Mobilus Cosmo GTW gateway through mobilus-client
```

Keep setup/unload/migration and client creation in `__init__.py`, polling in `coordinator.py`, Mobilus value parsing in `device_state.py`, entity behavior in platform modules, and device type grouping in `const.py`. Run blocking `mobilus-client` calls through `hass.async_add_executor_job`.

## Hard Boundaries

- Never expose or commit real gateway hosts, Home Assistant secrets, credentials, gateway IPs, or payloads captured from a real installation.
- Keep tests fully mocked/local; do not contact a real Home Assistant instance, Mobilus gateway, MQTT broker, cloud service, public internet, or vendor-hosted runtime.
- Use synthetic placeholders in docs/tests/examples, including README snippets, such as `GATEWAY_HOST`, `USER_LOGIN`, and `USER_PASSWORD`.
- Do not broaden public config flow, supported platforms, domain, dependencies, Home Assistant compatibility, HACS metadata, release behavior, or cloud behavior unless the task requires it.

## Checks

Install dev deps if needed:

```bash
pip install -e ".[test]"
```

CI runs on Python 3.14; prefer matching that interpreter locally for compatibility-sensitive validation.

Use narrow checks while iterating:

```bash
pytest tests/test_cover.py -v
ruff check custom_components/mobilus/cover.py tests/test_cover.py
mypy custom_components/mobilus/cover.py
```

Full local gate:

```bash
ruff check --output-format=github .
mypy .
coverage run -m pytest -v
coverage report --fail-under=100
```

For dependency, manifest, HACS, config flow, translation, or platform changes, also account for the Hassfest workflow in `.github/workflows/hassfest.yml`; if it cannot be run locally, validate JSON/schema consistency and report that Hassfest remains CI-only.

## Task Routes

- Config flow or reconfigure behavior: inspect `config_flow.py`, `strings.json`, translations, `tests/test_config_flow.py` if present, and add/update config-flow tests when behavior changes; preserve setup keys and default `refresh_interval`.
- Setup, unload, migration, client creation, or devices-list loading: start with `__init__.py`, then `coordinator.py` and `tests/test_init.py`.
- Polling or state parsing: inspect `coordinator.py`, `device_state.py`, and `tests/test_coordinator.py`.
- Cover or garage-door behavior: inspect `cover.py`, device groups in `const.py`, and `tests/test_cover.py`; preserve supported features and generated `call_events` values.
- Switch behavior: inspect `switch.py`, `SWITCH_DEVICES` in `const.py`, and `tests/test_switch.py`; preserve `ON`/`OFF` `call_events` values.
- Device type/support changes: inspect `device.py`, `const.py`, the relevant platform module, README supported-device text, and focused tests for classification, entity behavior, and generated `call_events` values.
- Metadata, dependency, packaging, or Home Assistant compatibility changes: update `pyproject.toml`, `manifest.json`, `hacs.json`, README, and workflows where applicable.
- User-visible behavior: update README plus config strings/translations and focused tests together.

## Code And Tests

- Keep Ruff, mypy, coverage, pytest, package, and dependency settings in `pyproject.toml`; do not duplicate thresholds/rules here.
- Use pytest with `pytest-homeassistant-custom-component` and `pytest-asyncio`; `asyncio_mode` is `auto`.
- Keep Home Assistant APIs async where Home Assistant expects async methods; keep blocking Mobilus calls in executor jobs.
- Use `tests/conftest.py` fixtures, `MockConfigEntry`, `AsyncMock` for Home Assistant async APIs, and `Mock`/`patch` for Mobilus client calls, sleeps, logging, coordinator listeners, and executor seams.
- When adding, renaming, removing, or changing persisted `ConfigEntry` data, bump config-flow versioning as needed, implement/update `async_migrate_entry`, and test both new entries and migrated legacy entries.
- Platform setup tests should assert entities passed to `async_add_entities` with `assert_called_once*` or `call_args`, including supported/unsupported device filtering; entity tests should assert HA-facing properties, supported features, generated `call_events` commands, and coordinator refresh calls.
- State parsing tests should cover `UP`, `DOWN`, `ON`, percentages, tilt suffixes such as `50%:12$`, unknown values, and empty responses.
- Keep tests credential-free; avoid coverage-only assertions/branches.

## Manifest, HACS, And Translations

- Keep `custom_components/mobilus/manifest.json` valid for Hassfest and synchronized with runtime dependencies and integration metadata.
- Keep `hacs.json` synchronized with the supported Home Assistant version from README and `pyproject.toml`.
- When adding or renaming config flow fields or error reasons, update `strings.json` and every file under `custom_components/mobilus/translations/`; verify matching config/error key paths across all of them before handoff.

## Handoff

Call out validation and any user-visible, config flow, platform, entity behavior, translation, manifest/HACS, dependency, CI, release, or Home Assistant compatibility impact.
