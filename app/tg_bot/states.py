from aiogram.fsm.state import StatesGroup, State


class AddTarget(StatesGroup):
    waiting_for_name = State()
    waiting_for_domain = State()