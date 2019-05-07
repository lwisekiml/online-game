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
