from aiogram.dispatcher.filters.state import StatesGroup, State


class DoOrder(StatesGroup):

    car_make = State()
    car_model = State()
    car_engine = State()
    car_year = State()
    car_part = State()


class DoOrderFromVin(StatesGroup):

    car_vin_number = State()
    car_part_vin = State()


class DoOrderFromTechPassport(StatesGroup):

    car_tech_passport = State()
    car_part = State()


class SendBackMessage(StatesGroup):

    user_id = State()
    back_message = State()


class CarRepair(StatesGroup):

    info = State()
