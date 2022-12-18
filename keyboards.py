from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def keyboard_answer():
	# Кнопки для добавления в избранное и в ЧС"""
	answer_kb = VkKeyboard(one_time=True)
	answer_kb.add_button('DISLIKE', color=VkKeyboardColor.NEGATIVE)
	answer_kb.add_button('LIKE', color=VkKeyboardColor.POSITIVE)
	answer_kb.add_button('Стоп', color=VkKeyboardColor.PRIMARY)
	return answer_kb.get_keyboard()


def keyboard_next():
	# Кнопки для ответа продолжения поиска
	next_kb = VkKeyboard(one_time=True)
	next_kb.add_button('Стоп', color=VkKeyboardColor.NEGATIVE)
	next_kb.add_button('Продолжаем', color=VkKeyboardColor.POSITIVE)
	return next_kb.get_keyboard()


def keyboard_welcome():
	# Кнопки для определения поиска
	welcome_kb = VkKeyboard(one_time=True)
	welcome_kb.add_button('Персонализированный', color=VkKeyboardColor.PRIMARY)
	welcome_kb.add_button('Заданными параметрами', color=VkKeyboardColor.PRIMARY)
	return welcome_kb.get_keyboard()


def keyboard_help():
	# Кнопка для вызова help
	help_kb = VkKeyboard(one_time=True)
	help_kb.add_button('HELP', color=VkKeyboardColor.PRIMARY)
	return help_kb.get_keyboard()
