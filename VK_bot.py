import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import token

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
"""Кнопки для добавления в избранное и в ЧС"""
keyboard_answer = VkKeyboard(one_time=True)
keyboard_answer.add_button('DISLIKE', color=VkKeyboardColor.NEGATIVE)
keyboard_answer.add_button('LIKE', color=VkKeyboardColor.POSITIVE)

"""Кнопки для определения критериев поиска"""
keyboard_welcome = VkKeyboard(one_time=True)
keyboard_welcome.add_button('По моему профилю', color=VkKeyboardColor.PRIMARY)
keyboard_welcome.add_button('По параметрам', color=VkKeyboardColor.PRIMARY)


# С этой кнопкой надо разобраться
# keyboard_welcome.add_callback_button('Иной', color=VkKeyboardColor.POSITIVE, payload='кнопка')


def write_msg(user_id, message, keyboard=None):  # Передавать методы для API VK
	"""
	В kwargs передавать методы API VK
	:param user_id: ID пользователя
	:param message: Сообщение которое отправит бот
	:param keyboard: Клавиатура (по умолчанию None)
	:return:
	"""
	params = {
		'user_id': user_id,
		'message': message,
		'random_id': randrange(10 ** 7)
	}
	if keyboard:
		vk.method('messages.send', params | {'keyboard': keyboard})  # Слияние двух словарей
	else:
		vk.method('messages.send', params)


"""
Словарь запросов со списками ответов.
Там где не нужно вызывать кнопки ставми None.
Во всех остальных случаях необходимо указывать нужные кнопки.
"""
request_dict = {
	'старт': ["Как будем искать?", keyboard_welcome.get_keyboard()],
	'кнопка': ["Добавить в избранное?", keyboard_answer.get_keyboard()],
	'like': ['Добавлено', None],  # Вызвать нужную функцию при ответе like
	'dislike': ['Удалено', None]  # Вызвать нужную функцию при ответе dislike
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
					request_dict.get(request)[1]  # Вызов кнопок
				)
			else:
				write_msg(event.user_id, 'Не поняла ваш запрос')


if __name__ == '__main__':
	main_bot()
