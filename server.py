from cgi import parse_qs, escape
from wsgiref.simple_server import make_server
from spider import Spider
import json
import re
from pymongo import MongoClient
from bson import json_util

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
    if method == 'POST' or method == 'PUT':
        request_body_size = int(environ['CONTENT_LENGTH'])
        request_body = environ['wsgi.input'].read(request_body_size)
        d = json.loads(request_body)
    elif method == 'GET' or method == 'DELETE':
        d = parse_qs(environ['QUERY_STRING'])
        for query in d:
            d[query] = d[query][0]
    return [d, method]

def getArticle(type):
    pass

def handleData(dict_data):
    response_json = json.dumps(dict_data)
    return bytes(response_json, encoding = "utf8")

def application(environ, start_response):
    status = '200 OK' # HTTP Status  
    headers = [('Content-Type', 'application/json'),('Access-Control-Allow-Origin', '*')] # HTTP Headers
    # 开始响应
    start_response(status, headers)
    # 获取参数 params [data, method]
    params = getParams(environ)
    # 抓取并返回数据
    try:
        set_headers = setHeaders()
        if params[0].get('url'):
            # 网络请求
            response = spider(url = params[0].get('url'), method = params[0].get('method'), headers = set_headers)
            response_json = bytes(response, encoding = "utf8")
        elif params[0].get('db'):
            # 服务端数据库操作
            db_name = params[0].get('db')
            collection_name = params[0].get('collection')
            # 建立连接
            client = MongoClient('localhost', 27017)
            db = client[db_name]
            collection = db[collection_name]
            if params[1] == 'POST':
                pass
            if params[1] == 'DELETE':
                pass
            if params[1] == 'GET':
                dict_res = collection.find_one()
                del dict_res['_id']
                json_str_res = json_util.dumps(dict_res)
            if params[1] == 'PUT':
                pass
            # 关闭连接
            client.close()
            response = json.loads(json_str_res)
            # response = getArticle(params.get('db'))
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