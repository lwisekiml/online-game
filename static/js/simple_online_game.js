// simple_online_game.js : client 개발에 필요한 함수, 객체 및 로직을 포함
(function(){ 
	// 다른 라이브러리나 환경에 영향을 주지 않기 위해 즉시 실행 함수로 감싸고,
	// 좀 더 엄격한 코딩을 위해 strict mode를 사용
	'use strict';

	// 1) 필요한 전역 변수 선언 : 캐릭터 사이즈와 관련괸 상수, 캐릭터 이미지, 전역으로 사용할 변수 선언
	var
		CHARACTER_SIZE=96,
		CORRECT_LVALUE=11*3,
		CORRECT_TVALUE=8*3,

		initialize, painters, requestId, sog, Game, Server, Sprite, Painter, Actors, PainterFactory,

		moveUp = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		moveDown = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		moveLeft = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		moveRight = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		attackUp = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		attackDown = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		attackLeft = newImage(CHARACTER_SIZE, CHARACTER_SIZE),
		attackRight = newImage(CHARACTER_SIZE, CHARACTER_SIZE)
		;

		// 2) 내부적으로 필요한 함수 정의 부분 : privete 한 함수 정의
		...

		// 3) Game, Server, Sprite, Painter, Actors, PainterFactory 클래스 정의
		
		/**************** Game ****************/
		/*
		Game은 canvas의 Context, Server, Sprite를 가지고 게임 진행 로직을 구현한다.
		
		dataCB, registerCB 외에
		게임의 시작점인 start 메서드와
		게임 진행 중 계속 반봅되는 로직인 progress 메서드를 가지고 있다.
		
		initialize 함수에서 Game을 만든 후 start메서드를 호출하면서 끝이 났는데,
		start 메서드는 createPlayerPainters 함수를 호출하여 각 player의 개별 Painter를 만들고,
		Server의 connect 메서드에  자신의 dataCB와 registerCB를 넘겨 호출한다.
		*/

		Game = function($params){
			this.context = $params.context;
			this.server = $params.server;
			this.sprite = {};
			this.sprite.p1 = $params.sprite;
			this.sprite.p2 = null
		};

		Game.prototype.start = function(){
			painter = createPlayerPainters();
			this.server.connect(this.registerCB, this.dataCB);
		};

		/*
		Server로부터 data를 받아오는 기능을 하는 Server.data 메서드를 호출하기만 합니다.
		이 progress메서드는 각 CB메서드들에서 requestAnimationFrame을 통행 빠른 속도로 계속적으로 호출될 것이다.
		
		이 게임은 매 프레임마다 빠르게 서버로부터 데이터를 얻어와서 화면에 반영해야 하기 때문에 
		progress로 인해 Server.data가 호출되고,
		그러면 서버로부터 데이터를 받으면 호출되는 callback 함수인 dataCB가 호출되고,
		dataCB에서 받은 데이터로 화면을 그린 후
		다시 progress를 호출하면서 로직이 반복 완성 된다.
		*/
		Game.prototype.progress = function($time){
			this.server.data($time);
		};

		// 서버로부터 받은 사용자 ID를 세팅하고 requestAnimationFrame으로 progress 메서드를 시작
		Game.prototype.registerCB = function($data){
			this.server.userId = $data.userId;
			requestId = requestAnimationFrame($util.fn(this.progress, this));
		};

		// 서버로 부터 data를 받으면 호출
		/*
			처음에 에너지가 0인지 확인하여
			0 이면, 게임을 종료
				
			아니면 화면을 다 지운 후, setSpriteData 함수로 본인 Sprite에 서버에서 받은 데이터를 세팅
			그리고는 Sprite를 update하여 변경된 데이터를 반영하고,
			paint 하여 화면에 그린다.

			그 이후 p2(적 player)가 있는지 확인하고, 있으면 같은 작업을 해주고,
			requestAnimationFrame으로 progress 메서드를 반복하며 끝이 난다.
		*/
		Game.prototype.dataCB = function($data, $time){
			var p2, id;

			if($data[this.server.userId].energy < 1){
				this.server.exit();
			}

			this.context.clearRect(0, 0, this.context.canvas.width, this.context.canvas.height);
			setSpriteData(this.sprite.p1, $data[this.server.userId]);
			this.sprite.p1.update($data[this.server.userId], $time);
			this.sprite.p1.paint(this.context);

			for(id in $data){
				if(id != this.server.userId){
					p2 = id;
				}
			}

			if(p2){
				if(!this.sprite.p2){
					this.sprite.p2 = new Sprite;
					this.sprite.p2.left = $data[p2].left;
					this.sprite.p2.top = $data[p2].top;
				}

				setSpriteData(this.sprite.p2, $data[p2]);
				this.sprite.p2.update($data[p2], $time);
				this.sprite.p2.paint(this.context);
			}

			requestId = requestAnimationFrame($util.fn(this.progress, this));
		};
		

		/**************** Server ****************/
		/*
			Server는 크게 웹 소켓 서버와 연결하고,
			데이터를 주고받을 때 흐름을 정의하는 connect 메서드와
			그 내부에서 상세 처리에 사용되는 
			data, register,update, exit 메서드가 있다.

			이들이 서버로 보내는 메시구조는
			[Command::JSON 형식 문자열 파라미터] 이며,
			Command는 Server의 생성자에 정의되어 있다.
		*/

		Server = function($params){
			this.userId = null;
			this.roomNo = $params.roomNo;
			this.socket = null;
			this.command = {REGISTER:'register', UPDATE:'update', DATA:'data'};
		};


		/*
			WebSocket 서버를 만들고,
			Server와 연결되었을 경우 발생하는 이벤트 open에서 register 메서드를 호출하여 캐릭터 등록을 진행하고,
			서버로부터 메시지를 받을 때 발생하는 이벤트 message에서는 서버가 넘겨준 데이터를 뽑아
				REGISTER 커맨드의 데이터인 경우 Game 객체가 넘겨준 $registerCB 함수에 데이터를 넘겨 호출하고,
				DATA 커맨드인 경우 $dataCB 함수에 데이터를 넘겨 호출하여 준다.
			그러면 CB함수에서 게임 진행과 관련된 처리를 하게된다.
		*/
		Server.prototype.connect = function($registerCB, $dataCB){
			var self = this;
			this.socket = new WebSocket('ws://' + (window.location.hostname || 'localhost') + ':8080');
			this.socket.addEventListener('open', function(){self.register();});
			this.socket.addEventListener('message', function($event){
				var result = JSON.parse($event.data),
				data = result.data;

				if(result.code === 0){
					if(result.status === self.command.REGISTER){
						$registerCB.apply(sog, [data]);
					}else if(result.status === self.command.DATA){
						$dataCB.apply(sog, [data, result.time]);
					}
				}else{
					self.exit();
					alert(data.message);
				}
			});
			this.socket.addEventListener('close', function($event){
				document.getElementById('exit').style.display = 'none';
				sog.context.clearRect(0, 0, sog.context.canvas.width, sog.context.canvas.height);
			});
		};

		// 서버로부터 데이터를 요청
		Server.prototype.data = function($time){
			this.socket.send(this.command.DATA + '::' + JSON.stringify({roomNo:this.roomNo, time:$time}));
		};

		// 처음 게임에 진입하였을때 서버에 캐릭터를 등록
		Server.prototype.register = function(){
			this.socket.send(this.command.REGISTER + '::' + JSON.stringify({roomNo:this.roomNo}));
		};

		//캐릭터 정보의 변경사항을 서버에 반영
		Server.prototype.update = function($data){
			this.socket.send(this.command.UPDATE + '::' + JSON.stringify({
				roomNo:this.roomNo,
				userId:this.userId,
				speedV:$data.speedV,
				speedH:$data.speedH,
				left:sog.sprite.p1.left + $data.speedV,
				top:sog.sprite.p1.top + $data.speedH,
				direction:$data.direction,
				status:$data.status,
				attackStatus:$data.attackStatus || 'none'
			}));
		};

		// 서버와 접속에 문제 있을 경우 게임을 정상 종료
		Server.prototype.exit = function($target){
			cancelAnimationFrame(requestId);
			requestId = null;
			this.socket.close();
		}

		/**************** Sprite ****************/
		// 하나의 Painter와 여러 Actor를 가지고 이들을 실행해주는 메서드들을 정의
		Sprite = function($painter, $actors){
			this.painter = $painter;
			this.actors = $actors||{};
			this.data = null;
			this.left = 0;
			this.top = 0;
		}

		Sprite.prototype.paint = function($context){
			this.painter.paint(this, $context);
		};

		Sprite.prototype.update = function($data, $time){
			this.data = $data;

			for(var name in this.actors){
				this.actors[name].execute(this, $data, $time);
			}
		};

		Sprite.prototype.advance = function(){
			this.painter.advance();
		};

		/**************** Painter ****************/
		Painter = function($image, $active){
			this.image = $image;
			this.active = $active;
			this.index = 0;
		};

		/* 
			메서드로 paint와 advance를 가진다.
			paint는 현재 가리키는 위치정보의 이미지를 그려주는 역할
			현재 index의 위치정보를 가지고 와 drawImage 함수로 이미지를 캔버스에 그린다.
			
			drawImage는 캔버스 기능으로 각 인자의 의미는 
			[이미지 객체, 
			 이미지 내 left 위치, 이미지 내 top 위치, left 로부터의 너비, top로 부터 높이, 
			 현재 캐릭터의 left 위치, 현재 캐릭터의 top 위치, 캐릭터 너비, 캐릭터 높이]
		*/
		Painter.prototype.paint = function($sprite, $context){
			var
				i, r, g, b, imageData,
				active = this.active[this.index];

				$context.drawImage(
					this.image,
					active.left, active.top, active.width, active.height,
					$sprite.left, $sprite.top, this.image.width, this.image.height
					);

				/* 
					getImageData는 현재 캐릭터의 스프라이트듸 색상 정보를 취득
					CORRECT_ 상수는 이미지가 캐릭터를 중심으로 상하좌우로
					투명 배경이 꽤 크게 퍼져있기 때문에 정확히 캐릭터 사이즈의 색상 정보를 얻어오기 위해
					위치정보를 보정하는 데 사용
				 */
				imageData = $context.getImageData(
					$sprite.left + CORRECT_LVALUE,
					$sprite.top + CORRECT_TVALUE,
					this.image.width - CORRECT_LVALUE * 2,
					this.image.height - CORRECT_LVALUE - CORRECT_TVALUE
					);

				// player2의 경우 빨간 색상의 R과 B값을 서로 바꿔 파란 색상으로 변경			
				if($sprite === sog.sprite.p2){
					for(i = 0; i < imageData.data.length; i += 4){
						r = imageData.data[i],
						g = imageData.data[i+1],
						b = imageData.data[i+2];

						if(r === 202 && g === 16 && b === 16){
							imageData.data[i] = b;
							imageData.data[i+2] = r;
						}
					}

					$context.putImageData(imageData, $sprite.left + CORRECT_LVALUE, $sprite.top + CORRECT_TVALUE);
				}

				var target = $sprite === sog.sprite.p1 ? sog.sprite.p2:sog.sprite.p1;
				// 이후 캐릭터 공격 성공 여부를 체크하여 공격이 성공한 경우 공격을 당한 캐릭터의 색상을 반투명으로 변경하여 타격감을 주었다.
				if(target && target.data.attackStatus === 'success'){
					for(i = 3; i < imageData.data.length; i += 4){
						imageData.data[i] = imageData.data[i] / 2;
					}

					$context.putImageData(imageData, $sprite.left + CORRECT_LVALUE, $sprite.top + CORRECT_TVALUE);
				}
		};

		// advance는 sprite 이미지의 다음 이미지 위치정보를 가지키도록 index를 증가시키는 기능
		PainterFactory.prototype.advance = function(){
			this.index++;

			if(this.index > this.active.length - 1){
				this.index = 0;
			}
		};


		/*
			Painter의 경우 각 player 별로 당시 index값이 다를 것이므로 하나의 인스턴스로 공유해서 쓸 순 없다.
			따라서 인스턴스를 조금 더 편하게 생성하기 위해 PainterFactory를 별도로 두고,
			이미지와 위치정보를 미리 세팅하여 상태 값에 따라
			알맞은 Painter의 인스턴스를 반환해주도록 만든다.
		*/
		PainterFactory = {
			UP:'UP',
			DOWN:'DOWN',
			LEFT:'LEFT',
			RIGHT:'RIGHT',
			ATTACK_UP:'ATTACK_UP',
			ATTACK_DOWN:'ATTACK_DOWN',
			ATTACK_LEFT:'ATTACK_LEFT',
			ATTACK_RIGHT:'ATTACK_RIGHT',
			create:function($status){
				switch($status){
					case this.UP:
					return new Painter(moveUp, createActive(1024, 3));
					break;

					case this.DOWN:
					return new Painter(moveDown, createActive(1024, 3));
					break;

					case this.LEFT:
					return new Painter(moveLeft, createActive(1024, 8));
					break;

					case this.RIGHT:
					return new Painter(moveRight, createActive(1024, 8));
					break;

					case this.ATTACK_UP:
					return new Painter(attackUp, createActive(512, 6));
					break;

					case this.ATTACK_DOWN:
					return new Painter(attackDown, createActive(512, 6));
					break;

					case this.ATTACK_LEFT:
					return new Painter(attackLeft, createActive(512, 6));
					break;

					case this.ATTACK_RIGHT:
					return new Painter(attackRight, createActive(512, 6));
					break;
				}
			}
		};

		function createActive($interval, $length){
			var active = [], i;

			for(i = 0; i < $length; i++){
				active.push({left:i*$interval, top:0, width:$interval, height:$interval});
			}

			return active;
		}


		// 4) 초기화 및 게임 시작점
		initialize = function(){
			var
			exit = document.getElementById('exit'),
			context = document.getElementById('canvas').getContext('2d'),
			keyInfo = { // speedV : left, speedH : top, 방향, 상태
				'38':{speedV:0, speedH:-2, direction:'UP', status:'MOVE'},
				'40':{speedV:0, speedH:2, direction:'DOWN', status:'MOVE'},
				'37':{speedV:-2, speedH:0, direction:'LEFT', status:'MOVE'},
				'39':{speedV:2, speedH:0, direction:'RIGHT', status:'MOVE'},
				'32':{speedV:0, speedH:0, direction:'DOWN', status:'ATTACK'},
			};

			exit.addEventListener('click', function($event){
				sog.server.exit();
			});

			// keydown 이벤트에서는 정의된 키가 눌렸을 경우 해당 키 정보 객체를 복사하고,
			// 공격이면 기존 캐릭터의 방향을 유지하기 위해 방향 데이터를 조작하고,
			// 충돌처리를 한 후 결과가 false(충돌 X)이면 서버에 해당 key 정보를 Update
			document.addEventListener('keydown', function($event){
				if($event.keyCode in keyInfo){
					var data = $util.clone(keyInfo[$event.keyCode]);
					if(data.status === 'ATTACK'){
						data.direction = sog.sprite.p1.data.direction;
					}
					if(!collision(data)){
						sog.server.update(data);
					}
				}
			}, false);

			// keyup 이벤트에서는 키에서 손을 띄었으므로 현재 방향 그대로 대기상태로 Update
			document.addEventListener('keyup', function($event){
				sog.server.update({speedV:0, speedH:0, direction:sog.sprite.p1.data.direction, status:'STAY'});
				}, false);

			/*
				이벤트 정의가 끝나고 필요한 이미지 리소스 들을 로딩
				이미지 리소스 들이 전부 로딩되면 Server와 Game 객체를 만들고 게임을 시작
				주의할 점은 이미지가 전부 로딩되고 나서 게임을 시작해야 한다는 점이다.
				그렇지 않으면 게임이 시작되었는데 캐릭터가 안 보인다거나 배경이 안 보일 수 있다.
				
				소스코드는 xxx.src='';가 sog.start(); 보다 위에 있지만
				이미지가 로딩되는 것은 비동기 처리되기 때문에 반드시 이미지 로딩보다 게임 시작이 나중에 된다는 보장이 없다.
				
				따라서 $util.syncOnLoad 함수로 모든 이미지가 다 로딩되고 난 후 등록된 callback 함수를 호출하여 게임을 시작하게 작성함
				
				이 게임 작성에 필요한 유틸리티는 index.html 에 등록한 simple_utils.js내에 들어 있고,
				$util 객체를 통해 사용할 수 있다.
			*/
			moveUp.src = 'static/img/moveUp.png';
			moveDown.src = 'static/img/moveDown.png';
			moveLeft.src = 'static/img/moveLeft.png';
			moveRight.src = 'static/img/moveRight.png';
			attackUp.src = 'static/img/attackUp.png';
			attackDown.src = 'static/img/attackDown.png';
			attackLeft.src = 'static/img/attackLeft.png';
			attackRight.src = 'static/img/attackRight.png';

			$util.syncOnLoad([moveUp, moveDown, moveLeft, moveRight, attackUp, attackDown, attackLeft, attackRight], function(){
				var server = new Server({roomNo:'ROOM1'});
				sog = new Game({context:context, server:server, 
					sprite:new Sprite(PainterFactory.create(PainterFactory.DOWN))});

				document.removeEventListener('DOMContentLoaded', initialize, false);
				sog.start();
			});
		};

		document.addEventListener('DOMContentLoaded', initialize, false);
		// DOMContentLoaded 이벤트를 걸어 콜백으로 initialize 함수를 넣고 있다.
		// DOMContentLoaded 이벤트는 DOM 로딩이 완료되는 시점에 발생
		// (jQuery의 ready와 같은 기능이며 보문 코드에서 DOM을 조작해야 하므로
		//  반드시 DOM 로딩이 완료된 시점에 우리 코드가 호출되어야 한다.)
})();