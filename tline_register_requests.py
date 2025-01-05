import requests
import hashlib
import urllib.parse
import json
from fake_useragent import UserAgent
import random
import string
import re

class TLineRegistrator:
    def __init__(self, key_code, proxies=None):
        self.session = requests.Session()
        self.ua = UserAgent().random
        print(self.ua)
        self.v_rnd = random.randint(100,128)
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-HK,en;q=0.9,zh;q=0.8,zh-TW;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.tline.website',
            'priority': 'u=1, i',
            'referer': 'https://www.tline.website/auth/login?type=register',
            'sec-ch-ua': f'"Not/A)Brand";v="8", "Chromium";v="{self.v_rnd}", "Google Chrome";v="{self.v_rnd}"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.ua,
            'x-requested-with': 'XMLHttpRequest'
        }
        self.key_code = key_code
        self.proxies = proxies if proxies else {}  # 使用传入的代理配置，默认为{}
        self.question_url = 'https://www.tline.website/anno/restful/questions'
        self.user_url = 'https://www.tline.website/user'  # user页面URL

    def generate_random_name(self):
        """生成符合规则的随机用户名"""
        prefix = random.choice(['T', 'W'])
        digits = ''.join(random.choice(string.digits) for _ in range(8))
        return prefix + digits

    def generate_random_password(self):
        """生成符合规则的随机密码"""
        chars = string.digits + string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(9))

    def json_to_sorted_query_string(self, data):
        """将 JSON 对象转换为排序后的查询字符串"""
        sorted_keys = sorted(data.keys())
        params = []
        for key in sorted_keys:
            if key != 'sign':
                params.append((key, str(data[key])))
        return urllib.parse.urlencode(params)

    def calculate_sign(self, data):
        """计算 sign 值"""
        query_string = self.json_to_sorted_query_string(data)
        string_to_hash = query_string + self.key_code
        md5_hash = hashlib.md5(string_to_hash.encode()).hexdigest()
        return md5_hash

    def _fetch_questions(self):
        """从服务器获取问题列表"""
        question_headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': 'lang=zh-cn',
            'priority': 'u=1, i',
            'referer': 'https://www.tline.website/auth/login?type=register',
            'sec-ch-ua': f'"Google Chrome";v="{self.v_rnd}", "Chromium";v="{self.v_rnd}", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.ua,
            'x-requested-with': 'XMLHttpRequest'
        }
        response = self.session.get(self.question_url, headers=question_headers, proxies=self.proxies)
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"无法解析问题列表JSON: {response.text}")
            return []

    def register(self, name, passwd):
        """注册用户"""
        questions = self._fetch_questions()
        if not questions:
            return None, None
        question_data = random.choice(questions['data'])
        question = question_data['question']
        answer = passwd

        params = {
            "name": name,
            "email": name,
            "passwd": passwd,
            "question": question,
            "answer": answer,
            "code": "",
        }

        sign = self.calculate_sign(params)
        data = {
            **params,
            "sign": sign
        }

        response = self.session.post(
            'https://www.tline.website/auth/register',
            headers=self.headers,
            data=data,
            proxies=self.proxies
        )

        try:
            response_json = response.json()
            if response_json.get("ret") == 1 and response_json.get("msg") == "注册成功":
                return name, passwd
                # login_success = self.login(name, passwd)
                # if login_success:
                #     return name, passwd
                # else:
                #     print(f"注册成功, 登录失败: {name}")
                #     return None, None
            else:
                print(f"注册失败: {response_json}")
                return None, None
        except json.JSONDecodeError:
            print(f"无法解析JSON, 原始数据: {response.text}")
            return None, None

    def login_and_fetch_user(self, email, passwd):
        """登录用户, 并获取用户页面内容"""
        login_data = {
            "email": email,
            "passwd": passwd,
        }

        login_headers = self.headers.copy()
        login_headers['accept'] = 'application/json, text/javascript, */*; q=0.01'  # 设置为json

        login_response = self.session.post(
            'https://www.tline.website/auth/login',
            headers=login_headers,
            data=login_data,
            proxies=self.proxies
        )

        if login_response.status_code == 200:  # 登录成功返回200
            user_response = self.session.get(self.user_url, headers=self.user_headers, proxies=self.proxies)
            return login_response.text, user_response.text

        return login_response.text, None

    @property
    def user_headers(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=0, i',
            'referer': 'https://www.tline.website/auth/login?type=register',
            'sec-ch-ua': f'"Google Chrome";v="{self.v_rnd}", "Chromium";v="{self.v_rnd}", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.ua
        }

    @staticmethod
    def _extract_links(user_text):
        """从用户页面 HTML 中提取 Clash 和 V2RayNG 链接"""
        clash_match = re.search(r'data-clipboard-text="([^"]*?clash=1[^"]*)"', user_text)
        v2ray_match = re.search(r'data-clipboard-text="([^"]*?sub=3[^"]*)"', user_text)

        clash_link = clash_match.group(1) if clash_match else None
        v2ray_link = v2ray_match.group(1) if v2ray_match else None

        return clash_link, v2ray_link

if __name__ == '__main__':
    key_code = "MLE!^Re4XcsrxBbR&!DvenL$"  # 测试密钥，实际应用中应从服务器获取

    proxies = {'http': 'http://127.0.0.1:10809','https': 'http://127.0.0.1:10809'}  # 请替换为你的代理地址

    registrator_with_proxy = TLineRegistrator(key_code, proxies=proxies)
    name = registrator_with_proxy.generate_random_name()
    passwd = registrator_with_proxy.generate_random_password()
    name_res, passwd_res = registrator_with_proxy.register(name, passwd)
    if name_res and passwd_res:
        print(f"成功注册并登录用户: name={name_res}, password={passwd_res}")
        login_text, user_text = registrator_with_proxy.login_and_fetch_user(name_res, passwd_res)
        if user_text:
            clash_link, v2ray_link = registrator_with_proxy._extract_links(user_text)
            print(f"Clash 链接： {clash_link}")
            print(f"V2RayNG 链接： {v2ray_link}")
