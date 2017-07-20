import requests
import re
import json
import os

class Spider:
    """
        [Config]:
            require params: (url, method)
            choice params: (params, pattern)
        [Usage]:
            # init
                test = Spider('http://www.baidu.com', 'get', {'key': 'value'}, r'<title>(.+)</title>')
            # send request
                test.get_info()
    """
    def __init__(self, url, method, params = None, pattern = None, headers = None):
        self.url = url
        self.method = method
        self.params = params
        self.pattern = pattern
        self.headers = headers
    def get_info(self):
        def get():
            if self.params:
                r = requests.get(url = self.url, params = self.params, headers = self.headers)
            else:
                r = requests.get(url = self.url, headers = self.headers)
            return r
        def post():
            if self.params:
                r = requests.post(url = self.url, data = self.params, headers = self.headers)
            else:
                r = requests.post(url = self.url, headers = self.headers)
            return r
        switcher = {'GET': get(), 'POST': post(), 'get': get(), 'post': post()}
        try:
            response = switcher.get(self.method, 'none')
            p = self.pattern
            origin_data = response.text
            if self.pattern:
                r = re.findall(p, origin_data)
                return r
            else:
                return origin_data
        except Exception as err:
            print(err)
            return 'null'
        finally:
            print('************finish***********')
# test
if __name__ == '__main__':
    # url = 'http://127.0.0.1:7777/data/artarticle.json'
    # method = 'GET'
    # test = Spider(url, method)
    # data = test.get_info()
    # data = json.loads(data)
    # data = json.dumps(data, sort_keys = True, indent = 4, separators=(',', ': '))
    # print(data)
    path = os.path.abspath('.')
    with open('%s/data/artarticle.json' % path, 'r', encoding='utf-8') as f:
        print(f.read())