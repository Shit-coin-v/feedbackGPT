from telebot import types


# СОЗДАЕМ КЛАВИАТУРУ ДЛЯ ВЫБОРА ДЛИТЕЛЬНОСТИ ПОДПИСКИ 
sub_keyboard = types.InlineKeyboardMarkup()

# Создаем кнопки для разных вариантов подписки
sub_1_month = types.InlineKeyboardButton('1 месяц', callback_data='sub_1_month')
sub_3_month = types.InlineKeyboardButton('3 месяца', callback_data='sub_3_month')

# Добавляем кнопки в первый ряд клавиатуры
sub_keyboard.row(sub_1_month, sub_3_month)

# Создаем кнопки для разных вариантов подписки
sub_6_month = types.InlineKeyboardButton('6 месяцев', callback_data='sub_6_month')
sub_1_year = types.InlineKeyboardButton('1 год', callback_data='sub_1_year')

# Добавляем кнопки во второй ряд клавиатуры
sub_keyboard.row(sub_6_month, sub_1_year)


# СОЗДАЕМ КЛАВИАТУРУ ДЛЯ СТАРТОВОГО ЭКРАНА
custom_keyboard = types.InlineKeyboardMarkup()

# Добавляем кнопку для инструкции с ссылкой
btn_instruction = types.InlineKeyboardButton('Видео инструкция', url='https://youtu.be/RpiWnPNTeww')
add_api = types.InlineKeyboardButton('Добавить API токен', callback_data='add_api')
custom_keyboard.row(btn_instruction, add_api)