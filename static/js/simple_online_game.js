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
		/**************** Sprite ****************/
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