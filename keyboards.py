from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

ikb_nearest_service = InlineKeyboardMarkup(row_width=2)
key_Mozyr = InlineKeyboardButton('Мозырь', callback_data='nearest_Mozyr')
key_Kaliki = InlineKeyboardButton('Калинковичи', callback_data='nearest_Kalinkovichi')
ikb_nearest_service.add(key_Mozyr, key_Kaliki)

request_a_call = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отправить номер телефона',
                                                                              request_contact=True))

key_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/Отмена'))

ikb_vin_number = InlineKeyboardMarkup(row_width=2)
key_send_vin = InlineKeyboardButton('Написать VIN-номер', callback_data='order_from_vin')
key_send_tech_passport = InlineKeyboardButton('Отправить фото', callback_data='order_from_tech_passport')
ikb_vin_number.add(key_send_vin, key_send_tech_passport)

ikb_take_order = InlineKeyboardMarkup(row_width=1)
key_send_back_order = InlineKeyboardButton('Ответить на заказ', callback_data='sendback_order')
ikb_take_order.add(key_send_back_order)

ikb_take_order_from_photo = InlineKeyboardMarkup(row_width=1)
key_send_back_order_photo = InlineKeyboardButton('Ответить на заказ', callback_data='sendback_vin_order_photo')
ikb_take_order_from_photo.add(key_send_back_order_photo)