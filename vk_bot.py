import requests
import pickle
import re
import os
import time
import logging
from requests.exceptions import RequestException
from lxml import html as lxml

logger = logging.getLogger("VkontakteBot")
logger.setLevel(logging.WARNING)
# ======================================================================================================================
# create console handler and set level to info
handler_log = logging.StreamHandler()
handler_log.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler_log.setFormatter(formatter)
logger.addHandler(handler_log)


class VKBot:

    AUTH_URL = 'https://vk.com/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.COOKIE_FILE = 'vk_' + self.login + '_cookies.txt'
        #  Cookies expire 12 months since the last modification

    def get_cookies(self):
        try:
            session = requests.session()
            data = session.get(self.AUTH_URL, headers=self.HEADERS)
            page = lxml.fromstring(data.content)
            form = page.forms[0]
            form.fields['email'] = self.login
            form.fields['pass'] = self.password
            session.post(form.action, data=form.form_values())
            cookies = session.cookies
            remixusid = re.search(r'remixusid', str(cookies))  # vk cookie parameter
            remixlhk = re.search(r'remixlhk', str(cookies))    # vk cookie parameter
            if remixusid and not remixlhk:
                with open(self.COOKIE_FILE, 'wb') as f:
                    pickle.dump(cookies, f)
            else:
                logger.warning('Invalid login or password | Account blocked')
            session.close()
            return cookies
        except RequestException:
            logger.warning('VK host not responding')

    def load_cookies(self):
        check_file_exists = os.path.isfile(self.COOKIE_FILE)
        if check_file_exists:
            with open(self.COOKIE_FILE, 'rb') as f:
                cookies = pickle.load(f)
                expiry = list(cookie for cookie in cookies)[-1].expires
                if expiry < time.time():
                    cookies = self.get_cookies()
                return cookies
        else:
            logger.warning(f'Cookie file not found, getting... new cookie file')
            cookies = self.get_cookies()
            return cookies


if __name__ == "__main__":
    user = ''
    password = ''
    bot = VKBot(user, password)
    print(bot.get_cookies())
