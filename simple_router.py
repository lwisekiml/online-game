'''
URL 라우팅

클라이언트가 http://simple-online-game.com/start 라고 호출시
특정 디렉토리 하위에 있는 start.py 파일 내에 있는 함수에서
이 요청을 처리하도록 라우팅(경로 배정)하는 것이다.

이렇게 처리하지 않으면
현재 버전의 우리 서버는 어떤 요청이 들어오던지 한 가지 처리밖에 하지 못하게 된다.
'''

def route(environ, start_response):
    # hello_world 함수와 같은 구조
    # 파라미터로 들어온 environ에서 요청 URL을 가져와 분석하고, 그에 알맞은 라우팅을 하면 된다.
    # URL 중 앞의 프로토콜이라던지 호스트 부분은 필요없다.
    # 뒤에 리소스를 나타내는 부분(URL중 /start) 필요 --> environ에 PATH_INFO 라는 이름으로 저장
    # 가져온 PATH정보를 가지고 알맞은 .py 파일을 불러와 처리
    # 다른 파이썬 파일을 불러오기 위해서는 import_module 이라는 파이썬 모듈 필요

###########################################################################################

from importlib import import_module

"""
폴더 구조
simple
    └ online
        └ game.py
"""
import_module( 'simple.online.game' )

# 파라미터에 목표로 하는 .py 파일 경로를 적는다.
# 경로 구분은 "."으로 한다.
# 이렇게 실행된 import_module은 해당 파일(모듈) 내부의 클래스/함수/변수 등에 바로 접근 가능

###########################################################################################

from io import StringIO
from importlib import import_module

base_package = 'cgi-bin'
encoding = 'utf-8'

class Response:
    def __init__(self, stdout):
        self.stdout = stdout
    def write(self, contents):
        print(contents, file = self.stdout)

def route(environ, start_response):
    stdout = StringIO()
    path = environ.get('PATH_INFO')[1:]
    import_module(base_package + '.' + path.replace('/', '.')).process(environ.get('REQUEST_PAYLOAD'), Response(stdout))
    # 이 서버에서 라우팅 당해 사용되려면 타켓 xxx.py 파일 내에 process(request, response): 형식으로 함수를 하나 구현해야만 한다.
    # 따라서 어떤 모듈이 import 될지는 모르겠지만 그 안에 process 함수를 가지고 있다는 것은 자명하기 때문에(제가 만든 프로젝트이니 무조건 이렇게 가정) 
    # process 함수를 호출하고 인자를 넘겨준다.
    # 인자로는 이 전에 simple_httpd.py 에서 처리했던 REQUEST_PAYLOAD 와 직접 만든 Response 객체를 넘겨준다. 
    # 라우팅 된 모듈의 process 함수에서 Request 정보를 이용해서 알맞은 일을 처리하고 Response 객체에 응답 결과를 작성해 준다.
    start_response('200 OK', [('Content-Type', 'text/json;charset=' + encoding)])
    return [(stdout.getvalue().encode(encoding))]

###########################################################################################

import json

def process(request, response):
    result = select_users(request['name'])
    response.write(json.dumps(result))
# select_user 는 설명을 위한 임의의 함수

# StringIO는 문자열을 파일 객체처럼 다룰 수 있게 해주는 파이썬IO 함수
# 사용하는 이유는 Response 객체의 write 메서드에서 print 함수의 file인자에 넘겨주기 위함
# 전달된 Response 객체의 write 함수를 통해 응답결과를 작성하면 StrigIO()를 통해 생성된 문자열 파일 객체에 응답결과가 저장되고,
# 이 문자열 파일 객체의 getvalue 메서드를 호출하여 리턴된 값을 client로 전송
