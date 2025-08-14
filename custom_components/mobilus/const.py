from homeassistant.const import Platform

from .device import MobilusDevice

DOMAIN = "mobilus"

PLATFORMS = [Platform.COVER, Platform.SWITCH]

NOT_SUPPORTED_DEVICES = (
    MobilusDevice.CGR,
)
# Urządzenia typu C-SW, C-SWP (Cosmo Switch, Cosmo Switch Plug)
SWITCH_DEVICES = (
    MobilusDevice.CSW,
    MobilusDevice.CSWP,
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
