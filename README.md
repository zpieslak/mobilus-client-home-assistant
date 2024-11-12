## Mobilus Cosmo GTW Home Assistant Integration

![test workflow](https://github.com/zpieslak/mobilus-client-home-assistant/actions/workflows/test.yml/badge.svg)
![hassfest workflow](https://github.com/zpieslak/mobilus-client-home-assistant/actions/workflows/hassfest.yml/badge.svg)

This integration allows you to control Mobilus Cosmo GTW devices from Home Assistant, specifically the Mobilus COSMO 2WAY shutters. Internally, it uses the [Mobilus client library](https://github.com/zpieslak/mobilus-client) to communicate with the Mobilus Cosmo GTW.

## Prerequisites

- Home Assistant installation version `2024.4.0` or later (earlier versions are available in older releases - see `hacs.json` for details).
- Local access to the Mobilus Cosmo GTW IP address and valid login credentials. Internet access is not required and can be disabled on the Mobilus Cosmo GTW device.

## Installation

### HACS

Install through [custom repositories in HACS](https://www.hacs.xyz/docs/faq/custom_repositories/), using the following details:

- Repository: `https://github.com/zpieslak/mobilus-client-home-assistant`
- Category: `Integration`

### Manual

Locate Your Home Assistant configuration directory (this is typically found at `/var/lib/home_assistant`, depending on your installation method).

Copy the `mobilus` folder into the `custom_components` directory within your Home Assistant configuration directory. If the `custom_components` directory doesn't exist, create it.

```ruby
cp -r custom_components/mobilus /var/lib/home_assistant/custom_components/
```

## Configuration

Once installed, add the integration to your Home Assistant instance through UI (Settings -> Devices & Services -> Add Integration -> Mobilus COSMO GTW) and follow the UI configure setup.

If needed the setup can be reconfigured through "Reconfigure" in the integration settings.

Example configuration:

    host: 192.168.2.1
    username: admin
    password: mypassword


## Caveats

Currently, the integration supports Mobilus COSMO 2WAY shutters (CMR, COSMO, COSMO_CZR, COSMO_MZR, SENSO, and SENSO_Z). Other devices compatible with the Mobilus Cosmo GTW (CGR, SWITCH, SWITCH_NP) are not supported by this plugin at this time, as they do not provide the Mobilus shutter API and I am unable to test them.

The Mobilus COSMO 2WAY shutters state is updated every 10 minutes or on each action (open, close, stop).

If state updates are not working, please restart COSMO GTW device, it looks like it forcefully refreshes the state on each boot.

## Usage

Once configured, you can control your shutters through the Home Assistant UI or include them in automations and scripts.

## Debugging

To enable debug logs, add the following to your `configuration.yaml` file:

```yaml
logger:
  default: warning
  logs:
    custom_components.mobilus: debug
    mobilus_client: debug
```
