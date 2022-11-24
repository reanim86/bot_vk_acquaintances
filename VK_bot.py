import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import token

vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

"""Кнопки для добавления в избранное и в ЧС"""
keyboard_answer = VkKeyboard(one_time=True)
keyboard_answer.add_button('DISLIKE', color=VkKeyboardColor.NEGATIVE)
keyboard_answer.add_button('LIKE', color=VkKeyboardColor.POSITIVE)

"""Кнопки для определения критериев поиска"""
keyboard_welcome = VkKeyboard(one_time=True)
keyboard_welcome.add_button('Персонализированный', color=VkKeyboardColor.PRIMARY)
keyboard_welcome.add_button('Заданными параметрами', color=VkKeyboardColor.PRIMARY)

"""Кнопка для вызова help"""
keyboard_help = VkKeyboard(one_time=True)
keyboard_help.add_button('HELP', color=VkKeyboardColor.PRIMARY)


# С этой кнопкой надо разобраться
# keyboard_welcome.add_callback_button('Иной', color=VkKeyboardColor.POSITIVE, payload='кнопка')


def write_msg(user_id, message, keyboard=None, attachment=None):  # Передавать методы для API VK
	"""
	В kwargs передавать методы API VK
	:param user_id: ID пользователя
	:param message: Сообщение которое отправит бот
	:param keyboard: Клавиатура (по умолчанию None)
	:param attachment: Вложение (по умолчанию None)
	:return:
	"""
	vk.messages.send(
		user_id=user_id,
		message=message,
		keyboard=keyboard,
		attachment=attachment,
		random_id=randrange(10 ** 7)
	)


"""
Словарь запросов со списками ответов.
Там где не нужно вызывать кнопки ставми None.
Во всех остальных случаях необходимо указывать нужные кнопки.
"""
request_dict = {
	'старт': ["Как будем искать?", keyboard_welcome.get_keyboard(), None],
	'кнопка': ["Добавить в избранное?", keyboard_answer.get_keyboard(), None],
	# TODO: Дописать нужную функции для ответов
	'like': ['Вставить функцию которая вернет след результат поиска', None, None],  # Вызвать нужную функцию при ответе like
	'dislike': ['Вставить функцию которая вернет след результат поиска', None, None],  # Вызвать нужную функцию при ответе dislike
	'персонализированный': ['Вставить функцию которая вернет результат поиска', None, None],
	'заданными параметрами': ['Вставить функцию которая вернет результат поиска', None, None],

	'help': [
		'Я бот который поможет найти друзей или пару.\n'
		'Персонализированный поиск найдет сверстника(сверстницу) из вашего города противоположного пола.\n'
		'По поиску с заданными параметрами вы можете сами выбрать параметры поиска:\n'
		'-Город\n -Пол\n -Возраст\n'
		'Выбери как будем искать',
		keyboard_welcome.get_keyboard(), ['photo1_456264771', 'photo1_376599151']
	]
	# Прописать иные команды
}


def main_bot():
	for event in longpoll.listen():
		if event.type == VkEventType.MESSAGE_NEW and event.to_me:
			request = event.text.lower()
			# try:  # Нужно будет обработать возможные ошибки
			if request_dict.get(request):
				write_msg(
					event.user_id,  # ID пользователя
					request_dict.get(request)[0],  # Сообщение
					request_dict.get(request)[1],  # Вызов кнопок
					request_dict.get(request)[2],  # Вложение
				)
			else:
				write_msg(
					event.user_id,
					'Неверная команда\nНажми HELP чтоб увидеть возможные команды',
					keyboard_help.get_keyboard()
						)


if __name__ == '__main__':
	main_bot()
