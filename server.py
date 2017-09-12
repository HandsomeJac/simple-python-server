from cgi import parse_qs, escape
from wsgiref.simple_server import make_server
from spider import Spider
import json
import re
from pymongo import MongoClient, DESCENDING, ASCENDING
from bson import json_util
from bson.objectid import ObjectId

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
    print(method)
    if method == 'POST' or method == 'PUT':
        request_body_size = int(environ['CONTENT_LENGTH'])
        request_body = environ['wsgi.input'].read(request_body_size)
        str_request_body = str(request_body, encoding = "utf-8")
        if re.search(r'url', str_request_body):
            d = json.loads(str_request_body)
        else:
            d = parse_qs(str_request_body)
            for query in d:
              d[query] = d[query][0]
    elif method == 'GET' or method == 'DELETE' or method == 'OPTIONS':
        d = parse_qs(environ['QUERY_STRING'])
        for query in d:
            d[query] = d[query][0]
    return [d, method]

def getArticle(type):
    pass

def handleData(dict_data):
    response_json = json.dumps(dict_data)
    return bytes(response_json, encoding = "utf8")
def handleJsonData(collection, data, method):
    # 文章
    if data.get('db') == 'article_db':
        temp = {
            'title': data.get('title'),
            'time': data.get('time'),
            'content': data.get('content')
        }
    if method == 'POST':
        collection.insert_one(temp)
    elif method == 'PUT':
        orign = collection.find_one({"_id": ObjectId(data.get('id'))})
        replace = temp
        collection.update(orign, replace)
def application(environ, start_response):
    status = '200 OK' # HTTP Status  
    headers = [('Content-Type', 'application/json'),('Access-Control-Allow-Origin', '*'), ('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')] # HTTP Headers
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
                handleJsonData(collection, params[0], 'POST')
                json_str_res = '[]'
            if params[1] == 'DELETE':
                temp = collection.find_one({"_id": ObjectId(params[0].get('id'))})
                collection.delete_one(temp)
                json_str_res = '[]'
            if params[1] == 'GET':
                dict_res = list(collection.find().sort('time', ASCENDING))
                json_str_res = json_util.dumps(dict_res)
            if params[1] == 'PUT':
                handleJsonData(collection, params[0], 'PUT')
                json_str_res = '[]'
            if params[1] == 'OPTIONS':
                json_str_res = '[]'
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