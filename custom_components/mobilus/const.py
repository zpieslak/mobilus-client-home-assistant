from .device import MobilusDevice

DOMAIN = "mobilus"

NOT_SUPPORTED_DEVICES = (
    MobilusDevice.CGR,
    MobilusDevice.SWITCH,
    MobilusDevice.SWITCH_NP,
)

POSITION_SUPPORTED_DEVICES = (
    MobilusDevice.SENSO,
    MobilusDevice.SENSO_Z,
)

SUPPORTED_DEVICES = (
    MobilusDevice.CMR,
    MobilusDevice.COSMO,
    MobilusDevice.COSMO_CZR,
    MobilusDevice.COSMO_MZR,
    MobilusDevice.SENSO,
    MobilusDevice.SENSO_Z,
)
