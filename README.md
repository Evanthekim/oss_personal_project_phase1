# 구현 목표
###  본 프로젝트는 1982년 발매된 "소코반(そうこばん)" 게임이 목적이며, 모든 구멍에 모든 상자를 밀어넣어 퍼즐을 클리어 하는 것이 게임의 목표입니다. 모든 구멍이 채워질 경우 승리합니다.

# 구현 기능

* pygame 기반 게임 board(환경) 구현
* 플레이어 조작 기능
* 여러가지 phase를 구분하여 게임 화면과 시작 화면간의 전환을 구현
* 구성요소와 플레이어의 위치 등을 포함하는 게임 맵의 자동 생성 기능 구현

# Reference
[1] https://github.com/pygame/pygame "pygame"

# 지원 Operating Systems 및 실행 방법

## 지원 Operating Systems
|OS| 지원 여부 |
|-----|--------|
|windows | :o:  |
| Linux  | :x: |
|MacOS  | :x:  |

## 실행 방법
### Windows

1. python3.12를 설치한다

2. powershell 창에서 아래 pip3 library를 설치

```
pip3 install pygame
```

3. 재부팅 이후 python3 main.py를 실행하면 게임 창이 뜨면서 실행됨.

### Linux

1. python3.12를 설치한다.

2. bash에 다음 명령어를 통해 pip3 library를 설치

```
pip3 install pygame
```

3. 재부팅 이후 python3 main.py를 실행하면 게임 창이 뜨면서 실행됨.


### MacOS

# 실행 예시
![oss](https://github.com/Evanthekim/oss_personal_project_phase1/assets/60501545/6ab0ee7f-2f39-4392-b7c6-4b9865216fd8)

# 주요 코드 설명
## main.py
### method generate_sokoban_map()
- Description : sokoban 맵을 자동으로 생성하는 함수
  1. create_empty_map(width, height) : 게임 맵의 크기를 받아 해당하는 크기로 이중 리스트를 초기화 한다. 또한, 가장자리를 벽으로 채워 넣는다.
  2. place_player_and_goals(map_data, num_goals) : 생성된 맵에 플레이어와 목표지점인 구멍을 위치시킨다.
  3. place_boxes(map_data, goals) : 맵의 빈 공간에 상자를 위치시킨다. 이 때 상자의 개수는 구멍의 개수와 동일하며, 상자는 벽에 달라붙지 않게 한다.

### method move_player()
- Description : 플레이어의 움직임을 정의하는 함수
  1. 이동 방향에 상자가 있는 경우 : 상자를 플레이어와 함께 이동한다.
  2. 이동 방향에 아무 것도 없는 경우 : 플레이어만 움직인다.
  3. 이동 방향에 구멍 혹은 벽이 있는 경우 : 이동하지 않는다.

### method run()
- Description : 게임 루프를 정의하는 함수
  1. game_state : 현재 게임이 어느 phase에 있는지 저장하는 변수. 종류에 따라 다른 화면을 표시한다.

   * game_state == STATE_MENU : 시작 메뉴를 표시한다. enter 키를 누를 경우 게임 화면으로 전환한다.
   * game_state == STATE_CONTROLS : 조작 방법과 룰을 표시한다. esc 키를 누를 경우 시작 메뉴로 돌아간다.
   * game_state == STATE_GAME : 게임 화면을 표시한다. esc 키를 누를 경우 시작 메뉴로 돌아간다.

   2. 사용자의 방향키 입력에 따라 다른 방향으로 플레이어를 움직인다.
   3. game_state에 따라 서로 다른 함수를 호출하여 다른 화면을 표시한다.
 

# TODO List
* 백스페이스 키를 누를 경우, 이전 행동으로 돌아가는 기능 추가하기
* 맵 가장자리 뿐만 아니라 내부에도 벽으로 방해 구조물 추가하기
* 난이도를 분류하여 단계별로 구조가 복잡해지거나 더 많은 구멍을 채워야 하는 등 차별점 두기