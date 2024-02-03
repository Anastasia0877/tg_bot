from aiogram.fsm.state import StatesGroup, State


class MakeQueryStates(StatesGroup):
    fieldname = State()
    value = State()
    show_full = State()
    full_choice = State()


class AddMoneyStates(StatesGroup):
    amount = State()


class TalkAIStates(StatesGroup):
    talk = State()


class AddPeopleStates(StatesGroup):
    text = State()


class ChangeAdStates(StatesGroup):
    text = State()


class ChangeQueryAmountStates(StatesGroup):
    amount = State()


class ChangeGoalStates(StatesGroup):
    amount = State()
