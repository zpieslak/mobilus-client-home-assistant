from homeassistant.const import Platform

from .device import MobilusDevice

DOMAIN = "mobilus"

PLATFORMS = [Platform.COVER, Platform.SWITCH]

COVER_DEVICES = (
    MobilusDevice.CMR,
    MobilusDevice.COSMO,
    MobilusDevice.COSMO_CZR,
    MobilusDevice.COSMO_MZR,
    MobilusDevice.SENSO,
    MobilusDevice.SENSO_Z,
)

COVER_POSITION_DEVICES = (
    MobilusDevice.SENSO,
    MobilusDevice.SENSO_Z,
)

COVER_TILT_DEVICES = (
    MobilusDevice.COSMO_CZR,
)

GARAGE_DEVICES = (
    MobilusDevice.CGR,
)

SWITCH_DEVICES = (
    MobilusDevice.SWITCH,
    MobilusDevice.SWITCH_NP,
)
