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