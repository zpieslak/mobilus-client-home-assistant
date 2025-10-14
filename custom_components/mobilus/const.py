from homeassistant.const import Platform

from .device import MobilusDevice

DOMAIN = "mobilus"

PLATFORMS = [Platform.COVER, Platform.SWITCH]

NOT_SUPPORTED_DEVICES = (
    MobilusDevice.CGR,
)

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

SWITCH_DEVICES = (
    MobilusDevice.SWITCH,
    MobilusDevice.SWITCH_NP,
)
