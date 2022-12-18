import configparser

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from VK_search import get_people, personal_search
from VK_bot import write_msg, upload_photo, request_dict
from keyboards import keyboard_next, keyboard_welcome, keyboard_answer, keyboard_help
import re
from insert_tables import insert_searchers, insert_requests, insert_dislikes, insert_likes, select_likes


config = configparser.ConfigParser()
config.read('token.ini')
bot_token = config['Bot_token']['bot_token']

vk_session = vk_api.VkApi(token=bot_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
upload = VkUpload(vk)


def main_bot():
	"""
	Основная логика бота ВК
	:return:
	"""
	# message_id = None  # Пока id сообщения не нужен
	pattern_param_search = r'\\(\D*)\\(\d)\\(\d*)\\(\d*)'  # Регулярка которая разбирает формат поиска по параметрам
	search_result = None
	result = None
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
					result = personal_search(user_id)
					print(result)
					if result:
						write_msg(
							user_id,
							[str(result.get('name')) + '\n' + str(result.get('url'))],
							keyboard_answer(),
							[upload_photo(photo) for photo in result.get('photo')]
						)
					else:
						write_msg(
								user_id,
								'Ваша страница закрыта. Откройте страницу для поиска или воспользуйтесь поиском по параметрам\n',
								keyboard=keyboard_welcome()
						)

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
							keyboard_answer(),
							[upload_photo(photo) for photo in result.get('photo')]
						)
					except IndexError:
						write_msg(user_id, 'Продолжаем поиск?', keyboard=keyboard_next())
				elif request == "продолжаем":  # Продолжение поиска. Происходит смещение результатов поиска
					write_msg(user_id, 'Продолжаю поиск...')
					offset += 20  # Смещаем поиск на следующие 20 людей
					search_result = get_people(city, age_from, age_to, sex, offset=offset)
					result = search_result.pop(0)
					write_msg(
						user_id,
						[str(result.get('name')) + '\n' + str(result.get('url'))],
						keyboard_answer(),
						[upload_photo(photo) for photo in result.get('photo')]
					)
				elif request in list(request_dict.keys()):
					write_msg(
						user_id,
						request_dict.get(request)[0],
						request_dict.get(request)[1]
					)
				elif find_param_search and find_param_search:  # Поиск по параметрам
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
							keyboard_answer(),
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
						keyboard_help()
					)
			except vk_api.exceptions.ApiError as er:
				print(er)  # здесь можно залогировать ошибки
				write_msg(
					user_id,
					'Что то пошло не так. Попробуй заново или воспользуйся командой HELP',
					keyboard_help()
				)


if __name__ == '__main__':
	main_bot()
