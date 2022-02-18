# 1) Написать приложение, которое будет проходиться по указанному списку
#    двух и/или более пользователей и собирать данные об их подписчиках и подписках.
# 2) По каждому пользователю, который является подписчиком или на которого подписан
#    исследуемый объект нужно извлечь имя, id, фото
#    (остальные данные по желанию). Фото можно дополнительно скачать.
# 4) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать, чтобы:
# 5) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
# 6) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

import settings
# from tkinter import Variable
from scrapy.http import HtmlResponse
import scrapy
from items import InstapiderItem
import re
from urllib.parse import urlencode
import json
from copy import deepcopy
from pprint import pprint


class InstieSpider(scrapy.Spider):

    name = 'instie'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    login_link = 'https://instagram.com/accounts/login/ajax/'
    user_name = 'Onliskill_Udm'

    magic = settings.magic
    magic_spell = settings.magic_spell
    # users_to_parse = 'onliskill_udm', 'onliskill_udm'
    users_to_parse = 'hoogon2020', 'onliskill_udm'
    hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace('"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"'), text[-1].split('"')[-2]

    def parse(self, response: HtmlResponse):
        # getting csrf token
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.user_name,
                                           self.magic: self.magic_spell},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user_to_parse in self.users_to_parse:
                yield response.follow(
                    # we're visiting account page
                    f'/{user_to_parse}/',  # instagram.com/current_user
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user_to_parse})

    def user_data_parse(self, response: HtmlResponse, username):
        # getting user id
        user_id = self.fetch_user_id(response.text, username)
        # setting variables for links
        # 1. https://i.instagram.com/api/v1/fbsearch/accounts_recs/?target_user_id=8496186979&include_friendship_status=true
        # - все фолловеры, в т.ч. бывшие !
        # 2. https://i.instagram.com/api/v1/friendships/8496186979/following/
        variables = {'target_user_id': user_id,
                     'include_friendship_status': True}

        followers_url = 'https://i.instagram.com/api/v1/fbsearch/accounts_recs/?'
        get_followers_url = f'{followers_url}&{urlencode(variables)}'
        yield response.follow(get_followers_url,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

        get_followed_url = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/'
        yield response.follow(get_followed_url,
                              callback=self.user_followed_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id})

    def user_followers_parse(self, response: HtmlResponse, username, user_id):
        # извлекаем;
        # для получения списков фолловеров надо распарсить
        j_data = response.json()
        users = j_data.get('users')
        for user in users:
            item = InstapiderItem(
                following_user_id=user.get('pk'),
                user_name=user.get('username'),
                target_user_id=user_id,
                target_user_name=username,
                user_id=user.get('pk'),
                user_pic=user.get('profile_pic_url')
            )
            yield item

    def user_followed_parse(self, response: HtmlResponse, username, user_id):
        # извлекаем;
        # для получения списков подписок надо распарсить
        j_data = response.json()
        users = j_data.get('users')
        for user in users:
            item = InstapiderItem(
                target_user_id=user.get('pk'),
                user_name=user.get('username'),
                following_user_id=user_id,
                following_user_name=username,
                user_id=user.get('pk'),
                user_pic=user.get('profile_pic_url')
            )
            yield item
