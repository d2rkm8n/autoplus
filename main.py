from aiogram.types import ReplyKeyboardRemove

import config, support
from aiogram import Bot, Dispatcher, executor, types
from keyboards import ikb_nearest_service, request_a_call
from db import Database


bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
db = Database('database.db')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        stic_hello = open('stickers/stichello.webp', 'rb')
        await bot.send_sticker(message.chat.id, stic_hello)
        await bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}.\nДобро пожаловать в Автоплюс!')
        await message.delete()


@dp.message_handler(content_types=['contact'])
async def get_phone_number(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.chat.id, 'Спасибо, наш менеджер скоро свяжется с Вами!')
        for admin in config.ADMINS:
            await bot.send_message(admin, f'Пользователь {message.from_user.full_name} оставил запрос на обратный звонок\n'
                                          f'+{message.contact.phone_number}', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['sendall'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id in config.ADMINS:
            text = message.text[9:]
            for user in db.get_users():
                try:
                    await bot.send_message(user[0], text)
                    if int(user[1]) != 1:
                        db.set_active(user[0], 1)
                except:
                    db.set_active(user, 0)

            await bot.send_message(message.from_user.id, 'Рассылка произошла успешно!')


@dp.message_handler(commands=['get_users'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == support.CREATOR:
            result = [user[0] for user in db.get_users()]
            await bot.send_message(support.CREATOR, f'Пользователь в базе данных: {len(result)}')


@dp.message_handler(commands=['nearest_service'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.from_user.id, 'Выбирите город где Вам будет удобно нас посетить',
                               reply_markup=ikb_nearest_service)
        await message.delete()


@dp.callback_query_handler(lambda callback: callback.data.startswith('nearest'))
async def callback_access(callback: types.CallbackQuery):
    if callback.data == 'nearest_Mozyr':
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Адрес: улица Пушкина 44а, телефон: МТС/А1 6643939', reply_markup=None)
    if callback.data == 'nearest_Kalinkovichi':
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Адрес: Первомайская 42, телефон: МТС/А1 6643939', reply_markup=None)


@dp.message_handler(commands=['request_a_call'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.chat.id, "Для запроса звонка, нажмите кнопку <отправить номер телефона> .",
                               reply_markup=request_a_call)
        await message.delete()


@dp.message_handler(commands=['find_out_information'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_message(message.chat.id, 'У нас Вы можете приобрести автозапчасти и аксессуары;\n'
                                                     'Заказать бесплатную доставку по городу.\n'
                                                     'Мы работаем с 8:30 до 19:00 без выходных.\n'
                                                     'телефон для справок МТС/А1 664 39 39\n\n'
                                                     'Будем рады Вас видеть у нас в сервисе.')
        await message.delete()


@dp.message_handler(content_types=['text'])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        stic_ti_cho = open('stickers/sticker1.webp', 'rb')
        await bot.send_sticker(message.chat.id, stic_ti_cho)
        await bot.send_message(message.chat.id, 'Извините, я не понимаю Вас пока-что, но обязательно научусь.')
        await message.delete()


async def on_startup(_):
    print('Бот запущен!')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)