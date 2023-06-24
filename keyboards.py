from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

ikb_nearest_service = InlineKeyboardMarkup(row_width=2)
key_Mozyr = InlineKeyboardButton('Мозырь', callback_data='nearest_Mozyr')
key_Kaliki = InlineKeyboardButton('Калинковичи', callback_data='nearest_Kalinkovichi')
ikb_nearest_service.add(key_Mozyr, key_Kaliki)

request_a_call = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отправить номер телефона',
                                                                              request_contact=True))


