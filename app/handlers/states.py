from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AlertCreationStates(StatesGroup):
    waiting_for_target_price = State()
