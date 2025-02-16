import telebot
from telebot import types
import os
from config import TOKEN
from logic import get_class
from cars_data import cars_dict

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    message_text = ''
    if message.text == '/start':
        message_text = f'Привет, {message.from_user.first_name}!\n'

    message_text += 'Я бот, который знает все про машины. Отправь фото машины, чтобы узнать о ней больше'

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name = file_info.file_path.split('/')[-1]

        downloaded_file = bot.download_file(file_info.file_path)
        with open(f'images/{file_name}', 'wb') as new_file:
            new_file.write(downloaded_file)


        car_name, percentage = get_class(image_path=file_name)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(f'Узнать больше о {car_name}..', callback_data=f'find_more_{car_name}'))

        bot.send_message(message.chat.id, f'С вероятностью {percentage}% на фото {car_name.lower()}', reply_markup=keyboard)

        os.remove(f'images/{file_name}')

    except Exception:
        bot.send_message(message.chat.id, 'Кажется, возникли проблемы. Попробуйте еще раз загрузить фото машины.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('find_more_'))
def handler_car(call):
    car_model = call.data.replace('find_more_', '')
    cars = cars_dict[car_model]
    for car in cars:
        try:
            bot.send_photo(chat_id=call.message.chat.id,
                           photo=cars[car]['photo'],
                           caption=f'{car.upper()}\n\n{cars[car]['info']}')
        except Exception:
            bot.send_message(call.message.chat.id, f'Возникла ошибка при попытке отправки информации о {car.upper()}')

bot.infinity_polling()
