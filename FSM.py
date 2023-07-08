from aiogram.dispatcher.filters.state import StatesGroup, State


class DoOrder(StatesGroup):

    car_make = State()
    car_model = State()
    car_engine = State()
    car_year = State()
    car_part = State()


class DoOrderFromVin(StatesGroup):

    car_part_vin = State()



class SendBackMessage(StatesGroup):

    back_message = State()