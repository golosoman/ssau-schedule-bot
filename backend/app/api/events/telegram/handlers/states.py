from aiogram.fsm.state import State, StatesGroup


class ArgPromptStates(StatesGroup):
    """Состояния ожидания аргумента команды (после ForceReply-промпта)."""

    subgroup = State()
    notify = State()
