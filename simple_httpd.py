'''
CGI : 웹 서버와 비즈니스 로직을 처리하는 프로그램과의 연결을 위한 인터페이스 중 하나
    -> cgi-bin 디렉터리 하위에 위치하는 *.py 파일들을 URL을 통해 접슨하여 실행할 수 있는 구조
    ex) http://simple-online-game.com/cgi-bin/start.py

    -> 매 요청마다 새로운 프로세스 생성하여 처리 - 사용량이 많을 경우 성능에 매우 취약
'''    
from CGIHTTPServer import CGIHTTPRequestHandler
from BaseHTTPServer import HTTPServer

server_address = ( '', 80)
httpd = HTTPServer( server_address, CGIHTTPRequestHandler )
httpd.serve_forever()

'''
WSGI : CGI 보다 개선된 인터페이스

WSGI 서버는 요청이 들어오면 등록된 메서드(hello_world)로 제어권을 넘김
해당 메서드는 요청정보와 Response 객체를 받아 이를 처리하는 구조
'''
from wsgiref.simple_server import make_server, WSGIServer

def hello_world(environ, start_respons):
    start_response('200 OK', [('Content-Type', 'text/json;charset=utf-8')])

httpd = make_server('', 80, hello_world, ThreadedWSGIServer)
httpd.serve_forever()

###################################################################################

'''
1. 멀티 쓰레드 지원
WSGI는 싱글 쓰레드만 지원 -> 멀티 쓰레드 지원으로 동작하도록
ThreadingMixln을 WSGIServer와 함께 상속한 새로운 서버 클래스 제작
'''
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn

def hello_world(environ, start_respons):
    start_response('200 OK', [('Content-Type', 'text/json;charset=utf-8')])

class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
    pass

httpd = make_server('', 80, hello_world, ThreadedWSGIServer)
httpd.serve_forever()

###################################################################################

'''
2. POST 메서드 처리
우리 서버는 GET 메서드만 지원 -> POST 메서드 추가 구현
서버의 상세 제어를 맡고 있는 핸들러에서 구현
(기본적으로 파이썬 서버는 핸들러를 하나씩 가지고 있고, 각 핸들러에 따라 동작 방식 변화)
핸들러는 기본 WSGI 핸들러인 WSGIRequestHandler를 상속받아 만들고,
하위 메서드를 오버라이드 하여 동작을 변경
핸들러를 maker_server의 파라미터로 넘기면 서버에 마운트 되어 작동

WSGIRequestHandler의 get_environ 메서드는 client의 요청정보를 리턴
이 메서드를 재정의하여 GET과 POST의 분기 처리를 넣으면 되고,
이렇게 만들어진 요청정보는 hello_world의 environ 파라미터로 전달받게 된다.
'''
from wsgiref.simple_server import make_server, WSGIServer
class SimpleRequestHandler(WSGIRequestHandler):
    def get_environ(self):
        ...

httpd = make_server('', 80, hello_world, ThreadedWSGIServer)
httpd.serve_forever()

###################################################################################

import json, urllib.parse

encoding = 'utf-8'

class SimpleRequestHandler(WSGIRequestHandler):
    '''
    부모 클래스의 원본 메서드를 호출하여 요청정보를 받아온다.
    GET/POST에 따라 각각 요청 파라미터를 정제
    기존 요청정보에 request_payload를 키로 데이터를 삽입
    GET/POST 구분은 핸들러의 command 변수에 저장되어 들어온다.
    
    HTTP  스펙에 따라
        GET : 요청 파라미터가 URL에 포함되어 쿼리 스트링 형태로 들어온다.
            (QUERY_STRING 값을 뽑아 구분자(&, =)로 분리해 내면 간단)
            
            parameters의 이름으로 요청 파라미터를 넘겼을 경우,
            client가 JSON형태로 인코딩 하여 전송했다는 가정하게 JSON으로 파싱하여 저장

        POST : 요청 파라미터가 요청 본문에 포함되어 들어온다.
            WSGIRequestHandler에서는 아래와 같이 처리하여 값을 얻어올 수 있다.

            length = int(self.headers.get('content-length'))
            json.loads(urllib.parse.unquote(self.rfile.read(length).decode('utf-8)))
    '''
    def get_environ(self):
        environ = super(SimpleRequestHandler, self).get_environ()
        request_payload = {}

        if self.command == 'GET':
            for item in environ.get('QUERY_STRING').split('&'):
                if item:
                    request_payload[item.split('=')[0]] == item.split('=')[1]

            if 'parameters' in request_payload:
                request_payload = json.loads(urllib.parse.unquote(request_payload['parameters']))
        
        elif self.command == 'POST':
            length = int(self.headers.get('content-length'))

            if length > 0:
                request_payload = json.loads(urllib.parse.unquote(self.rfile.read(length).decode(encoding)))

        environ['REQUEST_PAYLOAD'] = request_payload

        return environ

###################################################################################
'''
로깅 기능
기존 WSGIServer에서 콘솔로 내보내는 로그 문자열을 내가 원하는 형식으로 바꿔 파일로 출력하도록 변경
핸들러의 log_message 메서드를 재정의
'''
log_file = open('log/simple.log', 'a')

class SimpleRequestHandler(WSGIRequestHandler):
    def get_environ(self):
        ...
    def log_message(self, format, *args):
        log_file.write('%s -- [%s] %s\n' % (self.address_string(), self.log_data_time_string(), format%args))

try:
    httpd = make_server('', 80, hello_world, ThreadedWSGIServer, SimpleRequestHandler)
    print('Starting simple_httpd on port' + str(httpd.server_port))
    httpd.serve_forever()
except KeyboardInterrupt:
    print('Shutting down simple_httpd')
    log_file.close()
    httpd.socket.close()
