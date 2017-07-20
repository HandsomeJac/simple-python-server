from cgi import parse_qs, escape
from wsgiref.simple_server import make_server
from spider import Spider
import json
import os
import re

def setHeaders():
    headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    return headers

def spider(url, method, data = None, headers = None):
    print('url: %s' % url)
    print('method: %s' % method)
    test = Spider(url, method, headers)
    data = test.get_info()
    return data

def getParams(environ):
    method = environ['REQUEST_METHOD']
    if method == 'POST':
        request_body_size = int(environ['CONTENT_LENGTH'])
        request_body = environ['wsgi.input'].read(request_body_size)
        d = json.loads(request_body)
        return d
    elif method == 'GET':
        d = parse_qs(environ['QUERY_STRING'])

def openFile(file):
    path = os.path.abspath('.')
    with open('%s/server/data/%s' % (path, file), 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def handleData(dict_data):
    response_json = json.dumps(dict_data)
    return bytes(response_json, encoding = "utf8")

def application(environ, start_response):
    status = '200 OK' # HTTP Status  
    headers = [('Content-Type', 'application/json'),('Access-Control-Allow-Origin', '*')] # HTTP Headers
    # 开始响应
    start_response(status, headers)
    # 获取参数
    params = getParams(environ)
    # 抓取并返回数据
    try:
        set_headers = setHeaders()
        if params.get('url'):
            # 网络请求
            response = spider(url = params.get('url'), method = params.get('method'), headers = set_headers)
            response_json = bytes(response, encoding = "utf8")
        elif params.get('file'):
            # 服务端文件操作
            response = openFile(params.get('file'))
            response_dict = {
                'status': 200,
                'errorMsg': None,
                'data': response
            }
            response_json = handleData(response_dict);
        return [response_json]
    except Exception as err:
        print(err)
        response_dict = {
            'status': 404,
            'errorMsg': '请求失败',
            'data': []
        }
        response_json = handleData(response_dict);
        return [response_json]

httpd = make_server('', 7777, application)
print("Serving on port 7777...")

# Serve until process is killed
httpd.serve_forever()