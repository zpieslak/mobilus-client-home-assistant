from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property

_LOGGER = logging.getLogger(__name__)

@dataclass
class MobilusDeviceStateList:
    devices: dict[str, MobilusDeviceState]

@dataclass
class MobilusDeviceState:
    EVENT_NUMBER_MOVING = 7

    device_id: str
    event_number: int
    value: str

    @cached_property
    def cover_position(self) -> int | None:
        if self._main_position == "UP":
            return 100

        if self._main_position == "DOWN":
            return 0

        # Reject STOP or other non-numeric position for cover
        if isinstance(self._main_position, str):
            return None

        # When tilt is moving cover position is additional position
        if self._is_moving and self._additional_position is not None:
            return self._additional_position

        return self._main_position

    @property
    def state(self) -> str | None:
        # Stan jako tekst: ON, OFF, UP, DOWN, STOP, itd.
        if isinstance(self._main_position, str):
            return self._main_position
        return None

    @cached_property
    def tilt_position(self) -> int | None:
        if isinstance(self._main_position, str):
            return self._additional_position

        # When tilt is moving tilt position is main position
        if self._is_moving:
            return self._main_position

        return self._additional_position

    @cached_property
    def _is_moving(self) -> bool:
        return self.event_number == self.EVENT_NUMBER_MOVING

    @cached_property
    def _additional_position(self) -> int | None:
        _main, _separtator, additional = self.value.partition(":")

        if not additional:
            return None

        if additional.endswith("$") and len(additional) > 1:
            return int(additional[:-1])

        return None

    @cached_property
    def _main_position(self) -> str | int:
        main, _separtator, _additional = self.value.partition(":")

        if main.endswith("%") and len(main) > 1:
            return int(main[:-1])

        return main

