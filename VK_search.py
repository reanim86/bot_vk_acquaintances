import configparser
from datetime import datetime as dt
from tqdm import tqdm
import vk_api


config = configparser.ConfigParser()
config.read('token.ini')
token = config['UserID']['vk_token']
bot_token = config['Bot_token']['bot_token']
vk = vk_api.VkApi(token=token)
bot_vk = vk_api.VkApi(token=bot_token)


def get_people(city, age_from, age_to, sex=0, count=20, offset=None):
    """
    Функция возвращает людей по заданным параметрам
    :param city: Город
    :param sex: пол
    :param age_from: возраст от
    :param age_to: возраст до
    :param count: количество возвращаемых результатов поиска
    :param offset: смещение результатов поиска
    :return: список с выборкой
    """

    try:
        result = []
        response = vk.get_api().users.search(
            hometown=city,
            age_from=age_from,
            age_to=age_to,
            sex=sex,
            count=count,
            offset=offset
        )
        for people in tqdm(response['items']):
            people_dict = dict()
            people_dict['name'] = f"{people['first_name']} {people['last_name']}"
            people_dict['url'] = f"https://vk.com/id{people['id']}"
            photos = vk_get_photo(people['id'])
            if photos:
                people_dict['photo'] = photos
                result.append(people_dict)
            else:
                continue
        return result
    except vk_api.exceptions.ApiError or AttributeError or TypeError:
        return []


def vk_get_photo(user_id):
    """
    Функция поиска фотографий по ID пользователя VK
    :param user_id: id пользователя
    :type user_id: int
    :return:
    """
    params = {
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': '1',
    }
    photos = []
    photos_url = []

    try:
        vk_photos = vk.method('photos.get', params)
        for items in vk_photos.get('items'):
            likes_photos = dict()
            likes_photos['photo'] = items.get('sizes')[-1].get('url')
            likes_photos['likes'] = items.get('likes').get('count')
            photos.append(likes_photos)
        photos.sort(key=lambda x: x['likes'])
        for photo in photos:
            photos_url.append(photo['photo'])
        return photos_url[-3:]
    except vk_api.exceptions.ApiError:
        return None


def get_user_info(user_id):
    """
    Функция получения информации со страницы пользователя ВК.
    :param user_id: id пользователя ВК
    :return: [user_id, city, bdate, sex] or None
    """
    try:
        user_info = vk.get_api().users.get(
            user_ids=user_id,
            fields=['city', 'sex', 'bdate']
        )
        for item in user_info:
            bdate = item.get('bdate')
            city = item.get('city').get('title')
            sex = item.get('sex')
            return [user_id, city, bdate, sex]
    except AttributeError:
        return None


def messages_search(user_id, message_id):
    """
    Функция поиска сообщений в диалоге ВК по id сообщения.
    :param user_id: id пользователя ВК
    :type user_id: int
    :param message_id: id сообщения
    :type message_id: int
    :return:
    """
    params = {
        'peer_id': user_id,
        'date': dt.today().date().strftime('%d%m%Y')
    }
    for items in reversed(bot_vk.method('messages.search', params).get('items')):
        if items.get('id') == message_id:
            return items.get('text')


if __name__ == '__main__':
    pass
