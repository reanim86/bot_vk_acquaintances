import configparser
import vk_api
from random import randrange
from vk_api.longpoll import VkLongPoll
from vk_api.upload import VkUpload
import requests
from io import BytesIO


config = configparser.ConfigParser()
config.read('token.ini')
bot_token = config['Bot_token']['bot_token']

vk_session = vk_api.VkApi(token=bot_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
upload = VkUpload(vk)


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


if __name__ == '__main__':
	pass
