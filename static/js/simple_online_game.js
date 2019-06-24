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
		...

		// 4) 초기화 및 게임 시작점
		initialize = function(){
			...
		};

		document.addEventListener('DOMContentLoaded', initialize, false);
})();