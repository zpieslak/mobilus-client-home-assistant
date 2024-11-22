from homeassistant.const import Platform

from .device import MobilusDevice

DOMAIN = "mobilus"

PLATFORMS = [Platform.COVER]

NOT_SUPPORTED_DEVICES = (
    MobilusDevice.CGR,
    MobilusDevice.SWITCH,
    MobilusDevice.SWITCH_NP,
)

POSITION_SUPPORTED_DEVICES = (
    MobilusDevice.SENSO,
    MobilusDevice.SENSO_Z,
)

TILT_SUPPORTED_DEVICES = (
    MobilusDevice.COSMO_CZR,
)

SUPPORTED_DEVICES = (
    MobilusDevice.CMR,
    MobilusDevice.COSMO,
    MobilusDevice.COSMO_CZR,
    MobilusDevice.COSMO_MZR,
    MobilusDevice.SENSO,
    MobilusDevice.SENSO_Z,
)
