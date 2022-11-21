import configparser
import requests
from pprint import pprint

url_search = 'https://api.vk.com/method/users.search'
url_cities = 'https://api.vk.com/method/database.getCities'
version_api_vk = '5.131'
config = configparser.ConfigParser()
config.read('token.ini')
token = 'vk1.a.4rMLp2mA-rlTCDs0hji7cYfzQSpTlDeEeyVDMGRjhIo1CDk9U_Us7xtH_-dx_78J_wmd42dfZjkHy_nWOiWt2ieLgQf6HFG0NfCQt26n4h0Es4LAoRolSeg6uKso4iF1qAvu2gErR1YIftoudbSYi7fDn0eAsqUyoAoqtATjuAO05JvWmeBIE3BTZ76GLsAMf-Wq_PNAdOXLhypJcrSmSw'
# token = config['UserID']['vk_token']
params_search = {
        'access_token': token,
        'v': version_api_vk,
        'city': 1
}
params_cities = {
        'access_token': token,
        'v': version_api_vk
}
response = requests.get(url=url_cities, params=params_cities)
pprint(response.json())