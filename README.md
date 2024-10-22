## Mobilus Cosmo GTW Home Assistant Integration

This integration allows you to control Mobilus Cosmo GTW devices from Home Assistant, specifically the Mobilus COSMO 2WAY shutters. Internally, it uses the [Mobilus client library](https://github.com/zpieslak/mobilus-client) to communicate with the Mobilus Cosmo GTW.

## Prerequisites

- Home Assistant installation.
- Local access to the Mobilus Cosmo GTW IP address and valid login credentials.

## Installation

Locate Your Home Assistant configuration directory (this is typically found at `/var/lib/home_assistant`, depending on your installation method).

Copy the `mobilus_client` folder into the `custom_components` directory within your Home Assistant configuration directory. If the `custom_components` directory doesn't exist, create it.

```ruby
cp -r custom_components/mobilus_client /var/lib/home_assistant/custom_components/
```

## Configuration

Add the following to your `configuration.yaml` file:

```yaml
cover:
  - platform: mobilus_client
    host: MOBILUS_COSMO_GTW_IP
    username: MOBILUS_COSMO_GTW_USERNAME
    password: MOBILUS_COSMO_GTW_PASSWORD
```

Example:

```yaml
cover:
  - platform: mobilus_client
    host: 192.168.2.1
    username: admin
    password: mypassword
```

## Caveats

Currently, the integration is tested only with Mobilus COSMO 2WAY shutters.

The Mobilus COSMO 2WAY shutters do not report their state. As a result, the cover entities in Home Assistant will not reflect the actual position of the shutters after they are moved.

## Usage

Once configured, you can control your shutters through the Home Assistant UI or include them in automations and scripts.

## Debugging

To enable debug logs, add the following to your `configuration.yaml` file:

```yaml
logger:
  default: warning
  logs:
    custom_components.mobilus_client: debug
    mobilus_client: debug
```
