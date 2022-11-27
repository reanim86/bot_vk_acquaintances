import configparser

import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.upload import VkUpload
from VK_search import get_user_info, get_people, messages_search
import requests
from io import BytesIO
import re

config = configparser.ConfigParser()
config.read('token.ini')
bot_token = config['Bot_token']['bot_token']

vk_session = vk_api.VkApi(token=bot_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
upload = VkUpload(vk)

"""Кнопки для добавления в избранное и в ЧС"""
keyboard_answer = VkKeyboard(one_time=True)
keyboard_answer.add_button('DISLIKE', color=VkKeyboardColor.NEGATIVE)
keyboard_answer.add_button('LIKE', color=VkKeyboardColor.POSITIVE)

"""Кнопки для ответа продолжения поиска"""
keyboard_YN = VkKeyboard(one_time=True)
keyboard_YN.add_button('Давай закончим', color=VkKeyboardColor.NEGATIVE)
keyboard_YN.add_button('Продолжаем', color=VkKeyboardColor.POSITIVE)

"""Кнопки для определения поиска"""
keyboard_welcome = VkKeyboard(one_time=True)
keyboard_welcome.add_button('Персонализированный', color=VkKeyboardColor.PRIMARY)
keyboard_welcome.add_button('Заданными параметрами', color=VkKeyboardColor.PRIMARY)

"""Кнопка для вызова help"""
keyboard_help = VkKeyboard(one_time=True)
keyboard_help.add_button('HELP', color=VkKeyboardColor.PRIMARY)


def write_msg(user_id, message, keyboard=None, attachment=None):
	"""
	Функция отправки сообщений ботом
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


def upload_photo(url):
	"""
	Функция загружает фото на сервер ВК. Возвращает строку в формате,
	который необходим для отправки ботом в сообщения
	:param url: Ссылка на фото из интернета
	:type url: str
	:return: str
	"""
	img = requests.get(url).content
	f = BytesIO(img)  # Сначала загружаем в ОЗУ

	response = upload.photo_messages(f)[0]  # Загружаем на сервер ВК
	owner_id = response['owner_id']
	photo_id = response['id']
	access_key = response['access_key']

	return f'photo{owner_id}_{photo_id}_{access_key}'


def main_bot():
	"""
	Основная логика бота ВК
	:return:
	"""
	# Словарь с вспомогательными ответами. Вторым значением в списке указывать нужные кнопки.
	request_dict = {
		'давай закончим': ["До скорых встреч", None],
		'заданными параметрами': [
			'Введи параметры поиска в формате:\n'
			r'\Город\Пол\Возраст ОТ\Возраст ДО''\n'
			r'--> Возраст ОТ и ДО указывать в цифрах (например 20\24)' '\n'
			'--> Пол указывать в формате:\n'
			'1-женский\n '
			'2-мужской\n '
			'0-любой \n'
			'Выбери как будем искать', None],
		'help': [
			'Я бот который поможет найти друзей или пару.\n'
			'Персонализированный поиск найдет сверстника(сверстницу) из вашего города противоположного пола.\n'
			'По поиску с заданными параметрами вы можете сами выбрать параметры поиска в формате:\n'
			r'\Город\Пол\Возраст ОТ\Возраст ДО''\n'
			r'--> Возраст ОТ и ДО указывать в цифрах (например \20\24)' '\n'
			'--> Пол указывать в формате:\n'
			'1-женский\n '
			'2-мужской\n '
			'0-любой \n'
			'Выбери как будем искать',
			keyboard_welcome.get_keyboard()
		]
	}
	pattern_param_search = r'\\(\D*)\\(\d)\\(\d*)\\(\d*)'  # Регулярка которая разбирает формат поиска по параметрам
	search_result = None
	message_id = None
	city = None
	sex = None
	age_from = None
	age_to = None
	offset = 20
	for event in longpoll.listen():
		user_id = event.peer_id
		if event.type == VkEventType.MESSAGE_NEW and event.to_me:
			request = event.text.lower()
			find_param_search = re.search(pattern_param_search, request)
			try:

				if request == "персонализированный":
					message_id = event.message_id
					write_msg(user_id, 'Сейчас найдем ...')
					search_result = get_user_info(user_id)
					result = search_result.pop(0)
					write_msg(
						user_id,
						[result.get('name'), '\n', result.get('url')],
						keyboard_answer.get_keyboard(),
						[upload_photo(photo) for photo in result.get('photo')]
					)
				elif request in ['like', 'dislike']:  # Отклик на лайк и дислайк
					result = search_result.pop(0)
					write_msg(
						user_id,
						[result.get('name'), '\n', result.get('url')],
						keyboard_answer.get_keyboard(),
						[upload_photo(photo) for photo in result.get('photo')]
					)
				elif request == "продолжаем":  # Продолжение поиска. Происходит смещение результатов поиска
					write_msg(user_id, 'Продолжаю поиск...')
					offset += 20  # Смещаем поиск на следующие 20 людей
					if messages_search(user_id, message_id) == "персонализированный":  # Проверяем последний формат поиска
						search_result = get_user_info(user_id, offset=offset)
						result = search_result.pop(0)
						write_msg(
							user_id,
							[result.get('name'), '\n', result.get('url')],
							keyboard_answer.get_keyboard(),
							[upload_photo(photo) for photo in result.get('photo')]
						)
					else:
						search_result = get_people(city, age_from, age_to, sex, offset)
						result = search_result.pop(0)
						write_msg(
							user_id,
							[result.get('name'), '\n', result.get('url')],
							keyboard_answer.get_keyboard(),
							[upload_photo(photo) for photo in result.get('photo')]
						)
				elif request in list(request_dict.keys()):
					write_msg(
						user_id,
						request_dict.get(request)[0],
						request_dict.get(request)[1]
					)
				elif find_param_search and bool(find_param_search):  # Поиск по параметрам
					city = find_param_search.group(1)
					sex = find_param_search.group(2)
					age_from = find_param_search.group(3)
					age_to = find_param_search.group(4)
					search_result = get_people(city, age_from, age_to, sex, offset=offset)
					result = search_result.pop(0)
					write_msg(
						user_id,
						[result.get('name'), '\n', result.get('url')],
						keyboard_answer.get_keyboard(),
						[upload_photo(photo) for photo in result.get('photo')]
					)
				else:
					write_msg(
						user_id,
						'Неверная команда или формат сообщения для поиска\nНажми HELP чтоб увидеть возможные команды',
						keyboard_help.get_keyboard()
					)
			except IndexError:
				write_msg(user_id, 'Продолжаем поиск?', keyboard=keyboard_YN.get_keyboard())
			except AttributeError:
				write_msg(
					user_id,
					'Ваша страница закрыта. Откройте страницу для поиска или воспользуйтесь поиском по параметрам\n',
					keyboard=keyboard_welcome.get_keyboard())


if __name__ == '__main__':
	main_bot()
