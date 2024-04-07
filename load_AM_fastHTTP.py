# -*- coding: utf-8 -*-
"""command to start test: locust -f load_AM_fastHTTP.py --host=http://localhost:8089"""

from locust.contrib.fasthttp import FastHttpUser
from locust import User, HttpUser, constant, TaskSet, task
from random import randint
from lxml import html
from users import all_snils_dev
import requests

client_secret = "***client_secret_token***"
host = "https://am-dev.bars.group"

connection_timeout = 10.0

catch_response = True  # Логировать (в отчет) ответы


def get_token():
    url = f"{host}/realms/master/protocol/openid-connect/token"

    payload = f'grant_type=client_credentials&client_id=covid_test&client_secret={client_secret}'
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    global token
    token = response.json()["access_token"]
    # print(response)
    return token


def get_new_snils():
    import random
    snils_list = []
    control_sum = 0
    str_control_sum = ""
    for i in range(9):
        if i == 2 or i == 5:
            snils_list.append(random.randint(1, 9))
        else:
            snils_list.append(random.randint(0, 9))
    for y in range(3):
        yy = y * 3
        if snils_list[yy] == snils_list[yy + 1] == snils_list[yy + 2]:
            get_new_snils()
    for i in range(len(snils_list)):
        control_sum += (9 - i) * snils_list[i]
    if control_sum == 100 or control_sum == 101 or control_sum % 101 == 100:
        str_control_sum = "00"
    else:
        if control_sum < 10:
            str_control_sum = "0" + str(control_sum)
        if 10 <= control_sum < 100:
            str_control_sum = str(control_sum)
        if control_sum > 101:
            if control_sum % 101 < 10:
                str_control_sum = "0" + str(control_sum % 101)
            else:
                if control_sum % 101 == 100:
                    str_control_sum = "00"
                else:
                    str_control_sum = str(control_sum % 101)
    snils_format = []
    snils_list = [str(i) for i in snils_list]
    for y in range(9):
        if y in (2, 5):
            a = snils_list[y] + "-"
        elif y == 8:
            a = snils_list[y] + " "
        else:
            a = snils_list[y]
        snils_format.append(a)

    # snilsstr = "".join(snils_list) + str_control_sum
    snils_format_str = "".join(snils_format) + str_control_sum
    return snils_format_str


class MyUserBehavor(FastHttpUser):
    wait_time = constant(0)

    @task(50)
    def autorization(self):
        i = randint(0, 19)
        user = all_snils_dev[0][0]
        password = all_snils_dev[0][1]

        payload = 'username=' + user + '&password=' + password
        url1 = f"{host}/realms/master/protocol/openid-connect/auth?client_id=account&redirect_uri={host}/realms/master/account&response_type=code"

        with self.client.get(url1, name="1. Start page and get redirect", catch_response=catch_response) as response:
            tree = html.fromstring(response.text)
        url2 = tree.xpath('//*[@id = "kc-form-login"]/@action')[0]
        user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (XHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'am-dev.bars.group',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent_val
        }
        request_name = "2. Authorization Post login/password " + user
        with self.client.post(url2, name=request_name, data=payload, headers=headers,
                              catch_response=catch_response) as response2:
            pass
        url_logout = f'{host}/realms/master/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fam-dev.bars.group%2Frealms%2Fmaster%2Faccount%2F'
        with self.client.get(url_logout, name="3. Goto Logout page", catch_response=True) as response:
            pass

    # @task(100)  # Проверка утечки памяти при ошибочной авторизации (включить-разкомментить)
    def autorization_err(self):
        
        user = get_new_snils()
        # password = all_snils_dev[i][1]

        payload = 'username=' + user + '&password=' + "error"
        url1 = f"{host}/realms/master/protocol/openid-connect/auth?client_id=account&redirect_uri={host}/realms/master/account&response_type=code"

        with self.client.get(url1, name="1. Start page and get redirect", catch_response=True) as response:
            tree = html.fromstring(response.text)
        url2 = tree.xpath('//*[@id = "kc-form-login"]/@action')[0]
        user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (XHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'am-dev.bars.group',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent_val
        }
        request_name = "2. Authorization Post login/password " + user
        with self.client.post(url2, name=request_name, data=payload, headers=headers, catch_response=True) as response2:
            pass
        url_logout = f'{host}/realms/master/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2Fia.rt-eu.ru%2Frealms%2Fmaster%2Faccount%2F'
        with self.client.get(url_logout, name="3. Goto Logout page", catch_response=True) as response:
            pass

    @task(1)
    def get_user_info(self):
        url = f"{host}/realms/master/user/057-084-668 82"

        payload = {}
        # payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + get_token()

        }

        with self.client.get(url, name="Get user info", catch_response=True, headers=headers) as response:
            pass
