# online-game
### simple_httpd.py
  * CGI  
    웹 서버와 비즈니스 로직을 처리하는 프로그램과의 연결을 위한 인터페이스 중 하나  
    -> cgi-bin 디렉터리 하위에 위치하는 .py 파일들을 URL을 통해 접슨하여 실행할 수 있는 구조
  
  * WSGI  
    WSGI 서버는 요청이 들어오면 등록된 메서드(hello_world)로 제어권을 넘김  
    해당 메서드는 요청정보와 Response 객체를 받아 이를 처리하는 구조
    
  * MultiThread  
    WSGI는 싱글 쓰레드만 지원 -> 멀티 쓰레드 지원으로 동작하도록  
    ThreadingMixln을 WSGIServer와 함께 상속한 새로운 서버 클래스 제작
    
  * POST / GET method  
  
  * Logging  
    기존 WSGIServer에서 콘솔로 내보내는 로그 문자열을 내가 원하는 형식으로 바꿔 파일로 출력하도록 변경  
    핸들러의 log_message 메서드를 재정의


### simple_router.py
  * URL routing  
    클라이언트가 http://simple-online-game.com/start 라고 호출시  
    특정 디렉토리 하위에 있는 start.py 파일 내에 있는 함수에서  
    이 요청을 처리하도록 라우팅(경로 배정)하는 것이다.
    
  * import_module  
    다른 파이썬 파일을 불러오기 위해서는 import_module 이라는 파이썬 모듈 필요
    
  * static resource
    client가 단순히 정적 리소스(html, css, js, jpg, gif 등)를 요청했을 경우,  
    예로 http://simple-online-game/index.html 와 같은 요청도 처리할 수 있어야 한다

------------------------------------------------------------------------------------
파이썬은 __ pycache __ 폴더에 .pyc 파일(또는 .pyo 파일)로 바이트 코드의 사본을 생성한다.  
프로그램을 조금 더 빨리 시작하는 것뿐이다.
