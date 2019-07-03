# online-game
### simple_httpd.py
  * CGI  
    웹 서버와 비즈니스 로직을 처리하는 프로그램과의 연결을 위한 인터페이스 중 하나  
    -> cgi-bin 디렉터리 하위에 위치하는 .py 파일들을 URL을 통해 접근하여 실행할 수 있는 구조
  
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


### simple_wsd.py
  * Web Socket  
    웹에서 TCP 소켓 통신을 지원하여, 서버와 한번 연결하고 지속적으로 데이터를 주고받는 HTML5의 명세  
    -> 웹소켓은 처음 한번 서버와 연결한 후 계속 데이터를 주고 받을 수 있어 빠르다.  
    
    * Web Socket으로 하는 server와 client 간의 통신은 두 가지 프로세스  
      * Handshake : server와 client가 데이터 송수신을 하기에 앞서 준비를 하도록 하는 절차  
      * data 송수신 : Handshake 후에 소켓을 통하여 데이터 송수신  

  * WebsocketServer  
    멀티쓰레드의 TCP통신을 하는 서버를 만들어야 하기 때문에  
    ThreadingMixIn, TCPServer 두 클래스를 상속받아 WebsocketServer클래스를 생성
    
  * WebsocketRequestHandler  
    BaseRequestHandler를 상속받아 WebsocketRequestHandler를 만들고, setup(), handle(), finish() 메서드 재정의
    
     * handshake() : 소켓을 통해 client로부터 요청정보를 받아온다.  
     * receive_message() : handshake 완료 후 client로 부터 데이터를 받는 메서드  
     * send_message() : clinet에게 data를 전송하는 method
    
------------------------------------------------------------------------------------

파이썬은 __ pycache __ 폴더에 .pyc 파일(또는 .pyo 파일)로 바이트 코드의 사본을 생성한다.  
이것은 프로그램을 조금 더 빨리 시작하는 것뿐이다.

------------------------------------------------------------------------------------

출처 : [처음 만드는 온라인 게임](https://brunch.co.kr/@wedump/4)  
