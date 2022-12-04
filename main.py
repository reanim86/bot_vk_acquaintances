import configparser

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.upload import VkUpload
from VK_search import get_user_info, get_people
from VK_bot import write_msg, upload_photo
import re
from datetime import datetime as dt
from insert_tables import insert_searchers, insert_requests, insert_dislikes, insert_likes, select_likes


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


def main_bot():
	"""
	Основная логика бота ВК
	:return:
	"""
	# Словарь с вспомогательными ответами. Вторым значением в списке указывать нужные кнопки.
	request_dict = {
		'давай закончим': ["До скорых встреч", None],
		'стоп': ["Надеюсь вам понравилось)) возвращайтесь скорей", None],
		'заданными параметрами': [
			'Введи параметры поиска в формате:\n'
			r'\Город\Пол\Возраст ОТ\Возраст ДО''\n'
			r'--> Возраст ОТ и ДО указывать в цифрах (например 20\24)' '\n'
			'--> Пол указывать в формате:\n'
			'1-женский\n '
			'2-мужской\n '
			'0-любой \n'
			'ВНИМАНИЕ! Если будет введен пол отличный от указанных чисел, поиск будет осуществляться без пола.',
			None],
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
			'\n'
			r'Командой "\favorit" сможете увидеть список людей, которым вы поставили лайк '
			'\n'
			'Выбери как будем искать',
			keyboard_welcome.get_keyboard()
		]
	}
	pattern_param_search = r'\\(\D*)\\(\d)\\(\d*)\\(\d*)'  # Регулярка которая разбирает формат поиска по параметрам
	search_result = None
	result = None
	# message_id = None  # Пока id сообщения не нужен
	city = None
	sex = None
	age_from = None
	age_to = None
	offset = 20
	for event in longpoll.listen():
		if event.type == VkEventType.MESSAGE_NEW and event.to_me:
			user_id = event.user_id
			request = event.text.lower()
			find_param_search = re.search(pattern_param_search, request)
			try:
				if request == "персонализированный":
					# message_id = event.message_id  # id сообщения пока не нужен
					insert_searchers(user_id)
					insert_requests(user_id)
					write_msg(user_id, 'Сейчас найдем ...')
					user_info = get_user_info(user_id)
					try:
						city = user_info[1]
						age_from = dt.today().year - int(user_info[2][-4:])
						age_to = age_from
						if user_info[3] == 1:
							sex = 2
						elif user_info[3] == 2:
							sex = 1
						else:
							sex = None
						search_result = get_people(city, age_from, age_to, sex, offset=offset)
						result = search_result.pop(0)
						write_msg(
							user_id,
							[str(result.get('name')) + '\n' + str(result.get('url'))],
							keyboard_answer.get_keyboard(),
							[upload_photo(photo) for photo in result.get('photo')]
						)
					except Exception as error:
						print(error)  # здесь можно залогировать ошибки или отбирать пользователей с закрытой страницей
						write_msg(
							user_id,
							'Ваша страница закрыта. Откройте страницу для поиска или воспользуйтесь поиском по параметрам\n',
							keyboard=keyboard_welcome.get_keyboard())
				elif request in ['like', 'dislike'] and result:  # Отклик на лайк и дислайк
					if request == 'like':
						insert_likes(user_id, result)
					elif request == 'dislike':
						insert_dislikes(user_id, result)
					try:
						result = search_result.pop(0)
						write_msg(
							user_id,
							[str(result.get('name')) + '\n' + str(result.get('url'))],
							keyboard_answer.get_keyboard(),
							[upload_photo(photo) for photo in result.get('photo')]
						)
					except IndexError:
						write_msg(user_id, 'Продолжаем поиск?', keyboard=keyboard_YN.get_keyboard())
				elif request == "продолжаем":  # Продолжение поиска. Происходит смещение результатов поиска
					write_msg(user_id, 'Продолжаю поиск...')
					offset += 20  # Смещаем поиск на следующие 20 людей
					search_result = get_people(city, age_from, age_to, sex, offset=offset)
					result = search_result.pop(0)
					write_msg(
						user_id,
						[str(result.get('name')) + '\n' + str(result.get('url'))],
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
					insert_searchers(user_id)
					insert_requests(user_id)
					city = find_param_search.group(1)
					sex = find_param_search.group(2)
					age_from = find_param_search.group(3)
					age_to = find_param_search.group(4)
					search_result = get_people(city, age_from, age_to, sex, offset=offset)
					if search_result:
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
							f'Неверный формат сообщения для поиска или ошибка в запросе\n\n'
							f'{request_dict.get("заданными параметрами")[0]}',
						)
				elif request == r'\favorit':
					favorits = select_likes(user_id)
					write_msg(
						user_id,
						"\n".join(favorits))
				else:
					write_msg(
						user_id,
						'Неверная команда или формат сообщения для поиска\nНажми HELP чтоб увидеть возможные команды',
						keyboard_help.get_keyboard()
					)
			except vk_api.exceptions.ApiError:
				write_msg(
					user_id,
					'Что то пошло не так. Попробуй заново или воспользуйся командой HELP',
					keyboard_help.get_keyboard()
				)


if __name__ == '__main__':
	main_bot()
