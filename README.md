## Mobilus Cosmo GTW Home Assistant Integration

This integration allows you to control Mobilus Cosmo GTW from Home Assistant.
More information about Mobilus Cosmo GTW integration can be found [here](https://github.com/zpieslak/mobilus-client)

## Installation

Copy `custom_components/mobilus_client` folder to your Home Assistant configuration folder (typically `/var/lib/home_assistant/`).

For example:

    cp -r custom_components/mobilus_client /var/lib/home_assistant/custom_components/

## Configuration

Add the following to your `configuration.yaml` file:

    cover:
      - platform: mobilus_client
        host: MOBILUS_COSMO_GTW_IP
        username: MOBILUS_COSMO_GTW_USERNAME
        password: MOBILUS_COSMO_GTW_PASSWORD

For example:

    cover:
      - platform: mobilus_client
        host: 192.168.2.1
        username: admin
        password: mypassword

## Caveats

Currently, the integration is tested with Mobilus COSMO 2WAY shutters. Please note that the shutters do not report their state, and therefore the state is not updated in Home Assistant.

## Debugging

To enable debug logs, add the following to your `configuration.yaml` file:

    logger:
      default: warning
      logs:
        custom_components.mobilus_client: debug
        mobilus_client: debug
