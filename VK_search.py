import configparser
import requests
from pprint import pprint

def get_people(city, sex, age_from, age_to):
    result = []
    url_search = 'https://api.vk.com/method/users.search'
    version_api_vk = '5.131'
    config = configparser.ConfigParser()
    config.read('token.ini')
    token = config['UserID']['vk_token']
    params_search = {
        'access_token': token,
        'v': version_api_vk,
        'count': '1000',
        'hometown': city,
        'sex': sex,
        'age_from': age_from,
        'age_to': age_to
    }
    response = requests.get(url=url_search, params=params_search)
    for men in response.json()['response']['items']:
        people_dict = {}
        people_dict['name'] = f"{men['first_name']} {men['last_name']}"
        people_dict['url'] = f"https://vk.com/id{men['id']}"
        result.append(people_dict)
    return result

def get_vk_photo(id):
    """
    Функция возвращает информацию о фото в виде словаря, на  вход подаем id пользователя и id альбома, если id альбома
    не передать, то берем фото профиля
    """
    url_vk = 'https://api.vk.com/method/photos.get'
    version_api_vk = '5.131'
    config = configparser.ConfigParser()
    config.read('token.ini')
    token = config['UserID']['vk_token']
    all_photo = []
    params = {
        'access_token': token,
        'v': version_api_vk,
        'owner_id': id,
        'album_id': 'profile',
        'extended': '1',
        'photo_sizes': '1'

    }
    response = requests.get(url=url_vk, params=params)
    for photo_dict in response.json()['response']['items']:
        temp_dict_photo = {}
        temp_dict = {}
        temp_dict['likes'] = photo_dict['likes']['count']
        for photo in photo_dict['sizes']:
            temp_dict_photo[photo['type']] = photo['url']
        if 'w' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['w']
        elif 'z' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['z']
        elif 'y' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['y']
        elif 'x' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['x']
        elif 'r' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['r']
        elif 'q' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['q']
        elif 'p' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['p']
        elif 'o' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['o']
        elif 'm' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['m']
        elif 's' in temp_dict_photo:
            temp_dict['url'] = temp_dict_photo['s']
        all_photo.append(temp_dict)
    return all_photo
