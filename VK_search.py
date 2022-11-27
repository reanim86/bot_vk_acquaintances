import configparser
import requests
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
    result = []
    url_search = 'https://api.vk.com/method/users.search'
    version_api_vk = '5.131'
    params_search = {
        'access_token': token,
        'v': version_api_vk,
        'count': count,
        'hometown': city,
        'sex': sex,
        'age_from': age_from,
        'age_to': age_to,
        'has_photo': 1,
        'offset': offset
    }
    response = requests.get(url=url_search, params=params_search)
    print(response.json())
    for people in tqdm(response.json()['response']['items']):
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


def vk_get_photo(user_id):
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


def get_user_info(user_id, offset=None):
    try:
        user_info = vk.get_api().users.get(
            user_ids=user_id,
            fields=['city', 'sex', 'bdate']
        )
        for item in user_info:
            # if item.get('is_closed'):
            year = dt.today().year
            bdate = item.get('bdate')

            city = item.get('city').get('title')
            sex = item.get('sex')
            if sex == 1:
                sex = 2
            elif sex == 2:
                sex = 1
            else:
                return None

            if len(bdate) > 9 and city:
                age = year - int(bdate[-4:])
                return get_people(city=city, age_from=age, age_to=age, sex=sex, count=20, offset=offset)
            else:
                return None
    except vk_api.exceptions.ApiError or AttributeError or TypeError as error:
        print(error)
        return None


def messages_search(user_id, message_id):
    params = {
        'peer_id': user_id,
        'date': dt.today().date().strftime('%d%m%Y')
    }
    for items in reversed(bot_vk.method('messages.search', params).get('items')):
        if items.get('id') == message_id:
            return items.get('text')


if __name__ == '__main__':
    pass
