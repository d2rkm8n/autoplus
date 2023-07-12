from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import config, support
from aiogram import Bot, Dispatcher, executor, types
from keyboards import ikb_nearest_service, request_a_call, ikb_vin_number, ikb_take_order, key_cancel, ikb_take_order_from_photo
from db import Database
from FSM import DoOrder, SendBackMessage, DoOrderFromVin, CarRepair, DoOrderFromTechPassport
from datetime import datetime


storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)
db = Database('database.db')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        stic_hello = open('stickers/stichello.webp', 'rb')
        await bot.send_sticker(message.chat.id, stic_hello)
        await bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}.\nДобро пожаловать в Автоплюс!',
                               reply_markup=ReplyKeyboardRemove())
        await message.delete()


@dp.message_handler(commands=['Отмена'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await bot.send_message(message.chat.id, 'Вы отменили заказ', reply_markup=ReplyKeyboardRemove())
    await message.delete()


@dp.message_handler(content_types=['contact'])
async def get_phone_number(message: types.Message):
    if message.chat.type == 'private':
        sticker = open('stickers/st_ill_call_you.webp', 'rb')
        await bot.send_sticker(message.chat.id, sticker)
        await bot.send_message(message.chat.id, 'Спасибо, наш менеджер скоро свяжется с Вами!')
        for admin in config.ADMINS:
            await bot.send_message(admin, f'📎 НОВЫЙ ЗАПРОС!\n\n'
                                          f'Пользователь {message.from_user.full_name} '
                                          f'оставил запрос на обратный звонок\n'
                                          f'+{message.contact.phone_number}', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['sendall'])
async def send_to_all_users(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id in config.ADMINS:
            text = message.text[9:]
            for user in db.get_users():
                try:
                    await bot.send_message(user[0], text)
                    if int(user[1]) != 1:
                        db.set_active(user[0], 1)
                except:
                    db.set_active(user[0], 0)

            await bot.send_message(message.from_user.id, 'Рассылка произошла успешно!')


@dp.message_handler(commands=['order'])
async def send_order(message: types.Message):
    await bot.send_message(message.chat.id, 'Введите марку Вашего автомобиля:', reply_markup=key_cancel)
    await DoOrder.car_make.set()
    await message.delete()


@dp.message_handler(commands=['get_users'])
async def send_users_count(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == support.CREATOR:
            result = [user[0] for user in db.get_users()]
            await bot.send_message(support.CREATOR, f'Пользователей в базе данных: {len(result)}')


@dp.message_handler(commands=['nearest_service'])
async def send_nearest_service(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.from_user.id, 'Выбирите город где Вам будет удобно нас посетить',
                               reply_markup=ikb_nearest_service)
        await message.delete()


@dp.callback_query_handler(lambda callback: callback.data.startswith('nearest'))
async def callback_access(callback: types.CallbackQuery):
    #sticker = open('stickers/st_wait_you.webp', 'rb')
    if callback.data == 'nearest_Mozyr':
        await bot.send_location(callback.message.chat.id, latitude=52.047454, longitude=29.255804)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Адрес: улица Пушкина 44а, телефон: МТС/А1 6643939', reply_markup=None)
        #await bot.send_sticker(callback.message.chat.id, sticker)

    if callback.data == 'nearest_Kalinkovichi':
        await bot.send_location(callback.message.chat.id, latitude=52.132859, longitude=29.329223)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Адрес: Первомайская 42, телефон: МТС/А1 6643939', reply_markup=None)
        #await bot.send_sticker(callback.message.chat.id, sticker)


@dp.message_handler(commands=['request_a_call'])
async def request_call(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.chat.id, "Для запроса звонка, нажмите кнопку <отправить номер телефона> .",
                               reply_markup=request_a_call)
        await message.delete()


@dp.message_handler(commands=['find_out_information'])
async def send_info(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.chat.id, 'У нас Вы можете приобрести автозапчасти и аксессуары;\n'
                                                     'Заказать бесплатную доставку по городу.\n'
                                                     'Мы работаем с 8:30 до 19:00 без выходных.\n'
                                                     'телефон для справок МТС/А1 664 39 39\n\n'
                                                     'Будем рады Вас видеть у нас в сервисе.')
        await message.delete()


@dp.message_handler(state=DoOrder.car_make)
async def load_car_make(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Марка авто'] = message.text
    await bot.send_message(message.chat.id, 'Введите модель вашего автомобиля')
    await DoOrder.next()


@dp.message_handler(state=DoOrder.car_model)
async def load_car_model(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Модель'] = message.text
    await bot.send_message(message.chat.id, 'Укажите тип и объем двигателя')
    await DoOrder.next()


@dp.message_handler(state=DoOrder.car_engine)
async def load_car_year(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Двигатель'] = message.text
    await bot.send_message(message.chat.id, 'Укажите год выпуска автомобиля')
    await DoOrder.next()


@dp.message_handler(lambda message: not message.text.isdigit() or int(message.text) not in range(1980, datetime.now().year + 1),
                    state=DoOrder.car_year)
async def check_digits(message: types.Message):
    await message.reply('Введите более правдоподобную дату')


@dp.message_handler(state=DoOrder.car_year)
async def load_car_year(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Год выпуска'] = message.text
    await bot.send_message(message.chat.id, 'Какая запчасть Вас интересует?')
    await DoOrder.next()


@dp.message_handler(state=DoOrder.car_part)
async def load_car_part(message: types.Message, state: FSMContext):
    stic = open('stickers/st_ill_call_you.webp', 'rb')
    async with state.proxy() as data:
        data['Запчасть'] = message.text
    await bot.send_sticker(message.chat.id, stic)
    await bot.send_message(message.chat.id, 'Спасибо, Ваш заказ принят, наш менеджер скоро свяжется с Вами!')
    result_order = '\n'.join([f"{k}: {v}" for k, v in data.items()])
    user_info = f'\nПользователь: {message.from_user.first_name}, ID: {message.from_user.id}'
    for admin in config.ADMINS:
        await bot.send_message(admin, f"📝 НОВЫЙ ЗАКАЗ!\n\n" + result_order + user_info, reply_markup=ikb_take_order)
    await state.finish()


@dp.callback_query_handler(lambda callback: callback.data.startswith('sendback'))
async def sendback(callback: types.CallbackQuery, state=FSMContext):
    if callback.data == 'sendback_order':
        await bot.edit_message_text(chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    text=callback.message.text,
                                    reply_markup=None)
        await SendBackMessage.user_id.set()
        async with state.proxy() as data:
            data['user_id'] = callback.message.text.split()[-1]
        await bot.send_message(callback.message.chat.id, 'Напишите ответ пользователю: {}'.format(data['user_id']))
        await SendBackMessage.next()

    if callback.data == 'sendback_vin_order_photo':
        await bot.edit_message_caption(callback.message.chat.id,
                                       callback.message.message_id,
                                       caption=callback.message.caption,
                                       reply_markup=None)
        print(callback)
        await SendBackMessage.user_id.set()
        async with state.proxy() as data:
            data['user_id'] = callback.message.caption.split()[-1]
        await bot.send_message(callback.message.chat.id, 'Напишите ответ пользователю: {}'.format(data['user_id']))
        await SendBackMessage.next()


@dp.message_handler(state=SendBackMessage.back_message)
async def send_back_massage(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['ответ'] = message.text
    back_message = '📌 ОТВЕТ НА ВАШ ЗАПРОС!\n\n'
    await bot.send_message(data['user_id'], back_message + data['ответ'] + '\n\nСпасибо что выбираете нас!')
    await state.finish()
    await bot.send_message(message.chat.id, '✅ ЗАПРОС ОБРАБОТАН!')


@dp.message_handler(commands=['order_vin'])
async def send_vin_number(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.from_user.id, 'Как вам удобно указать VIN номер автомобиля?',
                               reply_markup=ikb_vin_number)
        await message.delete()


@dp.callback_query_handler(lambda callback: callback.data.startswith('order'))
async def order(callback: types.CallbackQuery):
    if callback.data == 'order_from_vin':
        await bot.send_message(callback.message.chat.id, 'Укажите VIN номер автомобиля', reply_markup=key_cancel)
        await bot.edit_message_text(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id,
            text=callback.message.text, reply_markup=None)
        await DoOrderFromVin.car_vin_number.set()
    if callback.data == 'order_from_tech_passport':
        await bot.send_message(callback.message.chat.id, 'Пришлите фото техпаспорта', reply_markup=key_cancel)
        await bot.edit_message_text(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id,
            text=callback.message.text, reply_markup=None)
        await DoOrderFromTechPassport.car_tech_passport.set()


@dp.message_handler(state=DoOrderFromVin.car_vin_number)
async def load_vin_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['VIN номер'] = message.text
    await bot.send_message(message.chat.id, 'Какая запчасть Вас интересует?')
    await DoOrderFromVin.next()


@dp.message_handler(state=DoOrderFromVin.car_part_vin)
async def load_car_part_vin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Запчасть'] = message.text
    result_order = '\n'.join([f"{k}: {v}" for k, v in data.items()])
    user_info = f'\nПользователь: {message.from_user.first_name}, ID: {message.from_user.id}'
    stic = open('stickers/st_ill_call_you.webp', 'rb')
    await bot.send_sticker(message.chat.id, stic)
    await bot.send_message(message.chat.id, 'Спасибо, Ваш заказ принят, наш менеджер скоро свяжется с Вами!',
                           reply_markup=ReplyKeyboardRemove())
    for admin in config.ADMINS:
        await bot.send_message(admin, f"📝 НОВЫЙ ЗАКАЗ!\n\n" + result_order + user_info, reply_markup=ikb_take_order)
    await state.finish()


@dp.message_handler(content_types=['photo'], state=DoOrderFromTechPassport.car_tech_passport)
async def do_order_from_tech_passport(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Фото'] = message.photo[0].file_id
    await bot.send_message(message.chat.id, 'Какая запчасть Вас интересует?')
    await DoOrderFromTechPassport.next()


@dp.message_handler(state=DoOrderFromTechPassport.car_part)
async def load_car_part_vin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Запчасть'] = message.text
    user_info = f'\nПользователь: {message.from_user.first_name}, ID: {message.from_user.id}'
    stic = open('stickers/st_ill_call_you.webp', 'rb')
    await bot.send_sticker(message.chat.id, stic)
    await bot.send_message(message.chat.id, 'Спасибо, Ваш заказ принят, наш менеджер скоро свяжется с Вами!',
                           reply_markup=ReplyKeyboardRemove())
    for admin in config.ADMINS:
        await bot.send_photo(admin, photo=data['Фото'],
                             caption=f"📝 НОВЫЙ ЗАКАЗ!\n\nЗапчасть: {data['Запчасть']}" + user_info,
                             reply_markup=ikb_take_order_from_photo)
    await state.finish()


@dp.message_handler(commands=['repair_cost'])
async def repair_cost(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.chat.id, "Опишите Вашу проблему.\n"
                                                "<Например: BMW E60, замена двигателя>", reply_markup=key_cancel)
        await message.delete()
        await CarRepair.info.set()


@dp.message_handler(state=CarRepair.info)
async def car_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['инфо'] = message.text
    stic = open('stickers/st_ill_call_you.webp', 'rb')
    await bot.send_sticker(message.chat.id, stic)
    await bot.send_message(message.chat.id, 'Спасибо, Ваш заказ принят, наш менеджер скоро свяжется с Вами!',
                           reply_markup=ReplyKeyboardRemove())
    user_info = f'\nПользователь: {message.from_user.first_name}, ID: {message.from_user.id}'
    for admin in config.ADMINS:
        await bot.send_message(admin, f"📝 НОВЫЙ ЗАКАЗ - УЗНАТЬ СТОИМОСТЬ РЕМОНТА!\n\n" + data['инфо'] + user_info,
                               reply_markup=ikb_take_order)
    await state.finish()


@dp.message_handler(content_types=['text'])
async def unknown_message(message: types.Message):
    if message.chat.type == 'private':
        stic_ti_cho = open('stickers/sticker1.webp', 'rb')

        await bot.send_message(config.ADMIN, message)
        await bot.send_sticker(message.chat.id, stic_ti_cho)
        await bot.send_message(message.chat.id, 'Извините, я не понимаю Вас пока-что, но обязательно научусь.')
        await message.delete()


async def on_startup(_):
    print('Бот запущен!')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)