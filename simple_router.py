# '''
# URL 라우팅

# 클라이언트가 http://simple-online-game.com/start 라고 호출시
# 특정 디렉토리 하위에 있는 start.py 파일 내에 있는 함수에서
# 이 요청을 처리하도록 라우팅(경로 배정)하는 것이다.

# 이렇게 처리하지 않으면
# 현재 버전의 우리 서버는 어떤 요청이 들어오던지 한 가지 처리밖에 하지 못하게 된다.
# '''

# def route(environ, start_response):
#     # hello_world 함수와 같은 구조
#     # 파라미터로 들어온 environ에서 요청 URL을 가져와 분석하고, 그에 알맞은 라우팅을 하면 된다.
#     # URL 중 앞의 프로토콜이라던지 호스트 부분은 필요없다.
#     # 뒤에 리소스를 나타내는 부분(URL중 /start) 필요 --> environ에 PATH_INFO 라는 이름으로 저장
#     # 가져온 PATH정보를 가지고 알맞은 .py 파일을 불러와 처리
#     # 다른 파이썬 파일을 불러오기 위해서는 import_module 이라는 파이썬 모듈 필요

# ###########################################################################################

# from importlib import import_module

# """
# 폴더 구조
# simple
#     └ online
#         └ game.py
# """
# import_module( 'simple.online.game' )

# # 파라미터에 목표로 하는 .py 파일 경로를 적는다.
# # 경로 구분은 "."으로 한다.
# # 이렇게 실행된 import_module은 해당 파일(모듈) 내부의 클래스/함수/변수 등에 바로 접근 가능

# ###########################################################################################

# from io import StringIO
# from importlib import import_module

# base_package = 'cgi-bin'
# encoding = 'utf-8'

# class Response:
#     def __init__(self, stdout):
#         self.stdout = stdout
#     def write(self, contents):
#         print(contents, file = self.stdout)

# def route(environ, start_response):
#     stdout = StringIO()
#     path = environ.get('PATH_INFO')[1:]
#     import_module(base_package + '.' + path.replace('/', '.')).process(environ.get('REQUEST_PAYLOAD'), Response(stdout))
#     # 이 서버에서 라우팅 당해 사용되려면 타켓 xxx.py 파일 내에 process(request, response): 형식으로 함수를 하나 구현해야만 한다.
#     # 따라서 어떤 모듈이 import 될지는 모르겠지만 그 안에 process 함수를 가지고 있다는 것은 자명하기 때문에(제가 만든 프로젝트이니 무조건 이렇게 가정) 
#     # process 함수를 호출하고 인자를 넘겨준다.
#     # 인자로는 이 전에 simple_httpd.py 에서 처리했던 REQUEST_PAYLOAD 와 직접 만든 Response 객체를 넘겨준다. 
#     # 라우팅 된 모듈의 process 함수에서 Request 정보를 이용해서 알맞은 일을 처리하고 Response 객체에 응답 결과를 작성해 준다.
#     start_response('200 OK', [('Content-Type', 'text/json;charset=' + encoding)])
#     return [(stdout.getvalue().encode(encoding))]

# ###########################################################################################

# import json

# def process(request, response):
#     result = select_users(request['name'])
#     response.write(json.dumps(result))
# # select_user 는 설명을 위한 임의의 함수

# # StringIO는 문자열을 파일 객체처럼 다룰 수 있게 해주는 파이썬IO 함수
# # 사용하는 이유는 Response 객체의 write 메서드에서 print 함수의 file인자에 넘겨주기 위함
# # 전달된 Response 객체의 write 함수를 통해 응답결과를 작성하면 StrigIO()를 통해 생성된 문자열 파일 객체에 응답결과가 저장되고,
# # 이 문자열 파일 객체의 getvalue 메서드를 호출하여 리턴된 값을 client로 전송

# ###########################################################################################

# '''
# 정적 리소스 처리
# 지금까지 비즈니스 로직을 처리할 수 있게 특정 파일의 process 함수를 호출하여 응답결과를 받아 client에 전달했다.
# 하지만 client가 단순히 정적 리소스(html, css, js, jpg, gif 등)를 요청했을 경우,
# 예로 http://simple-online-game/index.html 와 같은 요청도 처리할 수 있어야 한다.

# 정적 리소스를 분별하여 처리할 수 있을까? 확장자
# 이런 정적 파일들은 확장자를 통해 구별
# 브라우저에서 지원하는 확장자 set을 가지고 있다가 PATH 정보에서 확장자를 구하고
# 이와 비교하여 알맞은 확장자라면 해당 경로대로 파일을 찾아와 파일 내용을 client에 보내면 된다.
# '''
# default_page = 'index.html'
# extensions_map = {
#     'html':'text/html',
#     'htm':'text/html',
#     'ico':'image/x-icon',
#     'js':'text/javascript',
#     'css':'text/css',
#     'jpg':'image/jpeg',
#     'png':'image/png',
#     'gif':'image/gif',
#     'mp4':'video/mp4',
#     'avi':'video/avi'
# }

# def route(environ, start_response):
#     stdout = StringIO()
#     path = environ.get('PATH_INFO')[1:] or default_page
#     extension = path[path.rfind('.') + 1:]

#     if extension in extensions_map.keys():
#         return do_static(path, extension, start_response)

#     return do_dynamic(path, environ, start_response, stdout)

# def do_static(path, extension, start_response):
#     ...

# def do_dynamic(path, environ, start_response, stdout):
#     import_module(base_package + '.' + path.replace('/', '.')).process(environ.get('REQUEST_PAYLOAD'), Response(stdout))
#     start_response('200 OK', [('Content-Type', 'text/json; charset' + encoding)])

#     return [stdout.getvalue().encode(encoding)]

# # default_page 를 정의해서 PATH 정보가 없을 경우 index.html 로 지정
# # 그리고 확장자를 분리하여 미리 정의해 놓은 확장자 set(extensions_map)내에 포함되면 정적 리소스로 처리(do_static)하고
# # 아니면 기존 처리 방식(do_dynamic)으로 진행
# # 확장자 set은 확장자가 KEY가 되고, 브라우저가 인식하는 Content-Type을 값으로 하는 딕셔너리로 구성

# ###########################################################################################

# import os, time, sys

# sys.path.append('./')

# weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
# monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# def do_static(path, extension, start_response):
#     try:
#         f = open(path, 'rb')
#     except OSError:
#         start_response('404 File not found', [])
#         return []

#     try:
#         fs = os.fstat(f.fileno())
#         start_response('200 OK', [('Content-Type', get_ctype(extension)), ('Content-Length', str(fs[6])), ('Last-Modified', date_time_string(fs.st_mtime))])
#         return f.readlines()
#     except:
#         f.close()
#         raise

#     def get_ctype(extension):
#         return extensions_map.get(extension, '')

#     def date_time_string(self, timestamp=None):
#         if timestamp is None:
#             timestamp = time.time()

#         year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)

#         s = '%s, %02d %03s %4d %02d:%02d:%02d GMT' % (weekdayname[wd], day, monthname[month], year, hh, mm, ss)

#         return s

# '''
# 정적 리소스의 경우 client에 파일 내용을 그대로 내려주고 Content-Type을 통해 브라우저가 인식하게 하는 방식
# 따라서 해당 경로의 파일을 열어 readlines()로 파일내용을 전달하고,
# start_respons 객체에 Content-type과 Content-Length
# 그리고 새롭게 수정된 파일은 브라우저가 캐시를 사용하지 않도록 하기위한 Last-Modified 날짜를 보내줍니다.
# 파일의 수정된 날짜를 구하기 위해 파이썬의 os.fstat을 사용하여 파일 정보를 가져옴
# 파일이 존재하지 않을 경우 404 File not found를 전달

# 이것으로 파이썬으로 만든 HTTP 웹 서버가 완성
# 파이썬에서 기본적으로 제공하는 WSGI 구현체를 이용하여 멀티 쓰레드에 GET/POST 요청도 처리할 수 있고,
# 로깅/URL 라우팅/정적 리소스 처리까지 기본적인 웹 서버 & WAS가 하는 일을 처리할 수 있는 훌륭한 서버가 되었다.

# '''

###########################################################################################
'''
완성 코드
'''

import os, time, sys
from io import StringIO
from importlib import import_module

sys.path.append('./')

base_package = 'cgi-bin'
encoding = 'utf-8'
default_page = 'index.html'
extensions_map = {
	"html" : "text/html",
	"htm" : "text/html",
	"ico" : "image/x-icon",
	"js" : "text/javascript",
	"css" : "text/css",
	"jpg" : "image/jpeg",
	"png" : "image/png",
	"gif" : "image/gif",
	"mp4" : "video/mp4",
	"avi" : "video/avi"
}
weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

class Response:
    def __init__(self, stdout):
        self.stdout = stdout
    def write(self, contents):
        print(contents, file = self.stdout)

def route(environ, start_response):
    stdout = StringIO()
    path = environ.get('PATH_INFO')[1:] or default_page
    extension = path[path.rfind('.') + 1:]

    if extension in extensions_map.keys():
        return do_static(path, extension, start_response)

    return do_dynamic(path, environ, start_response, stdout)

def do_static(path, extension, start_response):
    try:
        f = open(path, 'rb')
    except OSError:
        start_response('404 File not found', [])
        return []

    try:
        fs = os.fstat(f.fileno())
        start_response('200 OK', [('Content-Type', get_ctype(extension)), ('Content-Length', str(fs[6])), ('Last-Modified', date_time_string(fs.st_mtime))])
        return f.readlines()
    except:
        f.close()
        raise

def do_dynamic(path, environ, start_response, stdout):
    import_module(base_package + '.' + path.replace('/', '.')).process(environ.get('REQUEST_PAYLOAD'), Response(stdout))
    start_response('200 OK', [('Content-Type', 'text/json; charset' + encoding)])

    return [stdout.getvalue().encode(encoding)]

def get_ctype(extension):
    return extensions_map.get(extension, '')

def date_time_string(self, timestamp=None):
    if timestamp is None:
        timestamp = time.time()

    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)

    s = '%s, %02d %3s %4d %02d:%02d:%02d GMT' % (weekdayname[wd], day, monthname[month], year, hh, mm, ss)

    return s
