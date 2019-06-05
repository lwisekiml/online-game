'''
HTTP 통신방식이 너무 느리다
1. client는 서버로부터 새로운 정보를 계속해서 수신하여 화면을 새로 그린다.
2. client는 사용자의 이벤트를 받아 서버로 변경된 정보를 송신
3. 서버를 client로 부터 받은 데이터를 갱신하여 보관, client로 부터 요청이 오면 최신 데이터를 송신

웹 소켓
웹에서 TCP 소켓 통신을 지원하여, 서버와 한번 연결하고 지속적으로 데이터를 주고받는 HTML5의 명세
HTTP는 한 번의 요청과 응답으로 서버와의 연결이 끊어지고 매번 다시 요청을 만들어 서버에 접근해야 하기 때문에 느린 반면,
웹소켓은 처음 한번 서버와 연결한 후 계속 데이터를 주고 받을 수 있어 빠릅니다.

웹 소켓으로 하는 서버와 클라이언트 간의 통신은 두 가지 프로세스가 존재
1. 핸드쉐이크
2. 데이터 송수신

1. 서버와 클라이언트가 서로 본격적인 데이터 송수신을 하기에 앞서 준비를 하도록 하는 절차
핸드쉐이크가 완료되면 바로 데이터를 주고받을 수 있습니다.
처음 클라이언트가 서버로 핸드쉐이크를 요청할 때의 요청 헤더 정보는 웹소켓의 스펙에 따라 다음과 같다.

GET /start HTTP/1.1
Host: simple-online-game.com
Upgrade: websocket
Connections: Upgrade
Sec-Websocket-Key: (임의의 키 값)

중요한 부분은 웹 소켓 연결인지 알기 위한 Upgrade, 서버와 핸드쉐이크를 하기위한 키 값인 Sec-Websocket-Key입니다.
클라이언트가 건넨 키를 서버가 읽어 매직넘버(웹 소켓 스펙에서 그냥 정해져 있는) 인
258EAFA5-E914-47DA-95CA-C5AB0DC85B11를 붙여 sha1으로 해싱한 후
base64로 인코딩 하여 만들어낸 키 값을 다시 클라이언트로 보내고,
클라이언트가 이를 확인 함으로 핸드쉐이크가 완료됩니다. 여기서 서버가 클라이언트로 보내는 응답 헤더는 다음과 같다.

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connections: Upgrade
Sec-Websocket-Accept: (매직넘버를 붙여 sha1으로 해싱하고 base64로 인코딩한 키 값)

그 이후로는 소켓을 통하여 데이터를 송수신하면 되는데,
이 때 주고받는 메시지를 웹 소켓 프레임이라고 한다.
이 역시 정해진 프레임 구조를 다른다.

0               1               2               3              
 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
 4               5               6               7              
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
 8               9               10              11             
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
 12              13              14              15
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+


opcode : 현재 프레임에 대한 특정 상태를 나타내는 코드
    1 일 때 (메시지가 UTF-8로 인코딩 된 TEXT를 나타냄)와 opcode가 8일 때(client가 소켓 연결 종료를 요청함)

MASK : 1인 경우에는 Masking-key 필드의 값을 본문 데이터(Payload Data)와 XOR 연산해야 진짜 원하는 본문 데이터가 추출
       Cache-poisoning attack을 막기 위함...

Payload len의 값이 126인 경우, 다음 2Byte에 데이터의 실제 길이가 나오고 127인 경우 다음 4Byte를 통해 데이터의 총 길이를 나타낼 수 있다.
125 이하인 경우에는 그 자체가 데이터의 실제 길이이고, Extended payload length를 넘기고 다음 필드부터 진행하면 된다.

Payload Data는 실제 데이터가 들어가는 부분이고 MASK 필드가 1인 경우 앞의 Masking-key의 값과 XOR연산한 값이 입력된다.
'''

# 웹 소켓 서버가 다 만들어졌다는 가정하에 서버를 실행시키는 코드
try:
    port = 8080
    wsd=WebsocketServer('0.0.0.0',port,WebsocketRequestHandler)
    print('Starting simple_wsd on port' + str(port))
    wsd.serve_forever()
except KeyboardInterrupt:
    print('Shutting down simple_wsd')
    wsd.socket.close()


# 앞으로 WebsocketServer와 WebsocketRequestHandler의 내용을 채우면 된다.
# WebsocketServer의 host파라미터 자리의 0.0.0.0은 client가 어떤 IP로 들어오면 다 받겠다는 의미

###########################################################################################

# WebsocketServer 구현
from socketserver import ThreadingMixIn, TCPServer

class WebsocketServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    client_id = 0
    clients = []
    all_data = {}

    def __init__(self, host, port, handlerClass):
        TCPServer.__init__(self, (host, port), handlerClass)

    def find_client(self, handler):
        for client in self.clients:
            if client['handler'] == handler:
                return client

    def in_client(self, handler):
        self.client_id += 1
        self.clients.append({'id':str(self.client_id), 'handler':handler})
        print('In client' + str(self.client_id))

    def out_client(self, handler):
        for client in self.clients:
            if client['handler'] == handler:
                self.clients.remove(client)
                del self.all_data[client['id']]
                handler.send_message(json.dumps({'code':0, 'message':'success'}))
                print('Out client' + client['id'])
                break

    def receive_message(self, handler, message):
        pass
'''
멀티쓰레드의 TCP통신을 하는 서버를 만들어야 하기 때문에
ThreadingMixIn, TCPServer 두 클래스를 상속받아 WebsocketServer클래스를 생성

allow_reuse_address는 TCPServer의 속성으로, 일반적으로 clinet가 접속 중에 서버를 재시작했다면 다시 서버가 시작되고
재접속할 때 이미 사용 중이라는 오류를 반환하게 된다.
allow_reuse_address를 True로 설정하게 되면 사용 중인 소켓이라도 재사용함으로써 오류 없이 진행할 수 있다.
수시로 서버를 재시작해야 하는 개발환경에서는 꼭 필요한 설정

daemon_threads는 ThreadingMixIn의 속성으로, 값이 True라면 메인 프로세스가 종료되어도 데몬 쓰레드는
계속 실행하게 해준다. 서버가 종료되어도 현재 작업 중이던 쓰레드는 종료되지 않고 정상적으로 작업을 마무리 하게 된다.

client_id는 각 client에게 식별 값으로 주어지는 시퀀스로 사용하려고 넣은 커스텀 속성(작성자 본인이)
client는 현재 접속 중인 client의 리스트이다. 역시 커스텀 속성이다.
client에 들어갈 client의 형식으로 {id : (clinet_id), handler : (handler object)} 이다.
all_data는 clinet들의 데이터를 가지고 있는 커스텀 속성이다.

생성자는 TCPServer의 생성자에 맞춰 호출해주면 되고,
clinet가 들어왔을 때와 나갔을 때를 처리해 줄 in_clinet와 out_clinet 그리고 이를 보조하기 위한 find_clinet 메서드를 구성하였다.
TCPServer에서 각 clinet 별로 핸들러 인스터스를 새로 생성하여 처리하기 때문에 client를 식별하는데 핸들러를 사용하였다.
receive_message 메서드는 client와 연계된 비즈니스 로직이 들어간다.
'''

###########################################################################################

# WebsocketRequestHandler 클래스 구현
from socketserver import BaseRequestHandler

class WebsocketRequestHandler(BaseRequestHandler):
    #Override
    def setup(self):
        self.socket = self.request
        self.is_valid = True
        self.is_handshake = False

    #Override
    def handle(self):
        while self.is_valid:
            if not self.is_handshake:
                self.handshake()
            else:
                self.receive_message()

    #Override
    def finish(self):
        self.server.out_client(self)
'''
BaseRequestHandler를 상속받아 WebsocketRequestHandler를 만들고, 메서드 3가지를 재정의한다.
setUp 메서드는 handle 메서드에 들어서기 앞서 처리해야 할 로직을 담는 메서드
(BaseRequestHandler가 가지고 있는 request(socket 객체)멤버 변수를 이해하기 쉽도록 socket이라는 이름으로 변경,
현재 client의 유효성 체크 용도인 is_valid와 핸드쉐이크가 이루어졌는지 확인하기 위한 is_handshake를 선언)
handle 메서드는 우리 서버의 본격적인 로직이 들어가는 부분이다.
여기서는 client가 처음 진입할 경우 핸드쉐이크를 하고 결과가 유효한 경우 client가 보내는 메시지를 받을 준비를 하게 된다.
마지막으로 finish메서드는 clinet의 연결이 끊어지는 시점에서 호출되므로 필요한 처리를 해주면 된다.
'''

###########################################################################################

# handshake method
class WebsocketRequestHandler(BaseRequestHandler):
    def handshake(self):
        header = self.socket.recv(1024).decode().strip()
        request_key = ''

        for each in header.split('\r\n'):
            if each.find(':') == -1:
                continue
            (k, v) = each.split(':')
            if k.strip().lower() == 'sec-websocket-key':
                request_key = v.strip()
                break
        
        if not request_key:
            self.is_valid = False
            print('Not valid handshake request_key')
            return
        
        response_key = b64encode(sha1(request_key.encode() + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'.encode()).digest()).strip().decode()
        response=\
            'HTTP/1.1 101 Switching Protocols\r\n'\
            'Upgrade: websocket\r\n'\
            'Connection: Upgrade\r\n'\
            'Sec-Websocket-Accept: %s\r\n'\
            '\r\n' % response_key
        
        self.is_handshake = self.socket.send(response.encode())
        self.server.in_client(self)
        print('Handshake OK!')

'''
우선 소켓을 통해 client로부터 요청정보를 받아온다.
UTF-8(디폴트)로 디코딩 하면 앞에서 살펴보았던 요청정보 문자열이 나온다.
그 형식에 따라 요청 문자열을 잘 분리하여 sec-websocket-key를 얻는다.
이 키를 sha1으로 해싱한 후 bse64로 인코딩 하면 bytearray가 나오는데 디코딩하면 응답 키 문자열을 얻을 수 있다.
이 키값을 응답 헤더 형식에 맞춰 소켓으로 전송하면 핸드쉐이크가 완료된다.
'''

###########################################################################################

# 핸드쉐이크 완료 후 client로 부터 데이터를 받는 메서드
class WebsocketRequestHandler(BaseRequestHandler):
    def receive_message(self):
        byte1, byte2 = self.socket.recv(2)

        opcode = byte1 & 15
        is_mask = byte2 & 128
        payload_length = byte2 & 127

        if not byte1 or opcode == 8 or not is_mask:
            self.is_valid = False
            return

        if payload_length == 126:
            payload_length = struct.unpack('>H', self.socket.recv(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack('>Q', self.socket.recv(4))[0]

        masks = self.socket.recv(4)
        payload = self.socket.recv(payload_length)
        message = ''

        for byte in payload:
            byte ^= masks[len(message) % 4]
            message += chr(byte)

        self.server.receive_message(self, message)

'''
정해져있는 형식대로 데이터를 주고받아야 한다.

먼저 최초 2byte만큼 데이터를 읽어 필요한 부분을 확인한다.
각 필요한 부분은 and 비트 연산을 통해 가져올 수 있다.
opcode를 가져오려면 opcode가 첫 번째 byte의 앞 4비트를 차지하고 있기 때문에
00001111(15)를 and연산해주면 
opcode가 아닌 부분을 0,
opcode인 부분은 opcode의 값에 따라 0 또는 1이 되어 opcode만 정제해 가져올 수 있다.
이런식으로 opcode, MASK, Payload len 부분을 가져온다.

opcode가 8이라면 이는 client에서 연결 종료를 요청한것이다.
따라서 is_valid의 값을 False로 변경해 handle 메서드렝서 더이상 루프가 돌지않고 종료되도록 처리한다.
MASK는 보안을 위해 client는 반드시 처리해줘야 하는것이 웹 소켓 스펙이기 때문에
MASK가 1이 아니면 이 또한 유효하지 않은 처리를 하도록 하겠다.
Payload len이 125 이하 라면 그 자체로 본문 데이터의 길이를 나타내고,
126이라면 뒤 2바이트에, 127이라면 뒤 4바이트를 통행 본문 데이터의 길이를 표현하도록 되어있다.
따라서 Payload len을 읽어 그 값이 1266이라면 다음 2바이트를 읽어 struct.unpack으로 바이트를 int로 바꿔주는데,
여기서 >H는 2바이트 int형을 나타낸다. 127일 경우 동일하지만 >Q로 4바이트 int 형으로 변경한다.

그 다음은 Masking-key 4byte를 읽고, 앞에서 계산한 본문 데이터의 길이 만큼 Payload Data(본문 데이터)를 읽는다.
그리고 Payload Data의 각 바이트에 Masking-key를 순차적으로 XOR 연산하여 실제 데이터 값을 추출한다.
그리고는 이 값을 서버의 비즈니스 로직을 처리하는 server.receive_message메서드로 보내면서 마무리되었다.
'''

###########################################################################################

# clinet에게 data를 전송하는 method
class WebsocketRequestHandler(BaseRequestHandler):
    def send_message(self, message):
        header = bytearray()
        payload = message.encode('UTF-8')
        payload_length = len(payload)

        header.append(129)

        if payload_length <= 125:
            header.append(payload_length)
        elif payload_length >= 126 and payload_length <= pow(2, 16):
            header.append(126)
            header.extend(struct.pack('>H', payload_length))
        elif payload_length <= pow(2, 64):
            header.append(127)
            header.extend(struct.pack('>Q', payload_length))
        else:
            print('Not valid send payload_length')
            return

        self.socket.send(header + payload)

'''
보내는 것 역시 받는 것과 별반 다르지 않다.
처음 1byte는 FIN을 1로 opcode도 1로, 즉 129로 설정한다.
opcode 1은 전송할 데이터가 UTF-8로 인코딩 된 TEXT 임을 의미한다.
그 후 데이터의 길이가 125면 그대로,
126이면 뒤 2byte를 통해,
127이면 뒤 4byte를 통행 데이터 길이를 보내준다.
받았던 것 과는 반대로 struct.pack을 이용하여 int값을 byte값으로 변경한다.
header와 본문 데이터를 붙여 전송하면 끝이다.
(서버가 보낼때는 마스킹은 하지 않는다.)
'''

###########################################################################################
'''
완성 코드
'''

import json
import struct

from hashlib import sha1
from base64 import b64encode
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler

class WebsocketServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    client_id = 0
    clients = []
    all_data = {}

    def __init__(self, host, port, handlerClass):
        TCPServer.__init__(self, (host, port), handlerClass)

    def find_client(self, handler):
        for client in self.clients:
            if client['handler'] == handler:
                return client

    def in_client(self, handler):
        self.client_id += 1
        self.clients.append({'id':str(self.client_id), 'handler':handler})
        print('In client' + str(self.client_id))

    def out_client(self, handler):
        for client in self.clients:
            if client['handler'] == handler:
                self.clients.remove(client)
                del self.all_data[client['id']]
                handler.send_message(json.dumps({'code':0, 'message':'success'}))
                print('Out client' + client['id'])
                break

    def receive_message(self, handler, message):
        pass


class WebsocketRequestHandler(BaseRequestHandler):
    #Override
    def setup(self):
        self.socket = self.request
        self.is_valid = True
        self.is_handshake = False

    #Override
    def handle(self):
        while self.is_valid:
            if not self.is_handshake:
                self.handshake()
            else:
                self.receive_message()

    #Override
    def finish(self):
        self.server.out_client(self)

    def handshake(self):
        header = self.socket.recv(1024).decode().strip()
        request_key = ''

        for each in header.split('\r\n'):
            if each.find(':') == -1:
                continue
            (k, v) = each.split(':')
            if k.strip().lower() == 'sec-websocket-key':
                request_key = v.strip()
                break
        
        if not request_key:
            self.is_valid = False
            print('Not valid handshake request_key')
            return
        
        response_key = b64encode(sha1(request_key.encode() + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'.encode()).digest()).strip().decode()
        response=\
            'HTTP/1.1 101 Switching Protocols\r\n'\
            'Upgrade: websocket\r\n'\
            'Connection: Upgrade\r\n'\
            'Sec-Websocket-Accept: %s\r\n'\
            '\r\n' % response_key
        
        self.is_handshake = self.socket.send(response.encode())
        self.server.in_client(self)
        print('Handshake OK!')
    def send_message(self, message):
        header = bytearray()
        payload = message.encode('UTF-8')
        payload_length = len(payload)

        header.append(129)

        if payload_length <= 125:
            header.append(payload_length)
        elif payload_length >= 126 and payload_length <= pow(2, 16):
            header.append(126)
            header.extend(struct.pack('>H', payload_length))
        elif payload_length <= pow(2, 64):
            header.append(127)
            header.extend(struct.pack('>Q', payload_length))
        else:
            print('Not valid send payload_length')
            return

        self.socket.send(header + payload)

    def receive_message(self):
        byte1, byte2 = self.socket.recv(2)

        opcode = byte1 & 15
        is_mask = byte2 & 128
        payload_length = byte2 & 127

        if not byte1 or opcode == 8 or not is_mask:
            self.is_valid = False
            return

        if payload_length == 126:
            payload_length = struct.unpack('>H', self.socket.recv(2))[0]
        elif payload_length == 127:
            payload_length = struct.unpack('>Q', self.socket.recv(4))[0]

        masks = self.socket.recv(4)
        payload = self.socket.recv(payload_length)
        message = ''

        for byte in payload:
            byte ^= masks[len(message) % 4]
            message += chr(byte)

        self.server.receive_message(self, message)
	
try:
    port = 8080
    wsd=WebsocketServer('0.0.0.0',port,WebsocketRequestHandler)
    print('Starting simple_wsd on port' + str(port))
    wsd.serve_forever()
except KeyboardInterrupt:
    print('Shutting down simple_wsd')
    wsd.socket.close()

