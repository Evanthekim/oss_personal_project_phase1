import pygame
import sys
import random
from collections import deque

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sokoban")

# 색상 설정
WHITE = (255, 255, 255)

# 이미지 로드
player_image = pygame.image.load('./assets/player.png')
wall_image = pygame.image.load('./assets/wall.png')
box_image = pygame.image.load('./assets/box.png')
goal_image = pygame.image.load('./assets/goal.png')
floor_image = pygame.image.load('./assets/floor.png')
box_on_goal_image = pygame.image.load('./assets/box_with_x.png')
blue_image = pygame.image.load('./assets/enemy.png')
bomb_image = pygame.image.load('./assets/enemy.png')  # 폭탄 이미지 로드
red_image = pygame.image.load('./assets/box.png')  # RED 이미지 로드

# 타일 크기 설정
tile_size = 100

# 맵 타일 종류
WALL = '#'
FLOOR = ' '
PLAYER = '@'
BOX = '$'
GOAL = '.'
BOX_ON_GOAL = '*'
PLAYER_ON_GOAL = '+'

# 방향 벡터
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# 게임 상태
STATE_MENU = 0
STATE_GAME = 1
STATE_CONTROLS = 2
game_state = STATE_MENU

# 맵 데이터
level = []
player_pos = [0, 0]
goal_count = 0
blue_pos = [0, 0]
blue_move_timer = 0  # 장애물 움직임 타이머
blue_move_interval = 500  # 장애물이 움직이는 간격 (밀리초 단위)
bombs = []  # 폭탄 위치를 저장할 리스트
red_pos = [0, 0]  # RED 객체 위치

#################phase2#################
# 비어있는 맵을 생성
def create_empty_map(width, height):
    map_data = [[WALL if x == 0 or x == width - 1 or y == 0 or y == height - 1 else FLOOR for x in range(width)] for y in range(height)]
    # 내부에 벽을 추가
    free_spaces = [(y, x) for y in range(1, height - 1) for x in range(1, width - 1)]
    random.shuffle(free_spaces)
    for _ in range(2):  
        wall_pos = free_spaces.pop()
        map_data[wall_pos[0]][wall_pos[1]] = WALL
    return map_data
#################phase2#################

# 비어있는 맵에 플레이어와 구멍을 배치
def place_player_and_goals(map_data, num_goals):
    global player_pos
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)

    # 플레이어 위치 선정
    temp_pos = list(free_spaces.pop())
    player_pos[0] = temp_pos[0]
    player_pos[1] = temp_pos[1]
    map_data[player_pos[0]][player_pos[1]] = PLAYER

    # 목표 지점 선정
    goals = []
    for _ in range(num_goals):
        goal_pos = free_spaces.pop()
        map_data[goal_pos[0]][goal_pos[1]] = GOAL
        goals.append(goal_pos)
    return player_pos, goals

# 대상 위치가 벽에 붙어있는지 확인
def is_adjacent_to_wall(y, x, map_data):
    """Check if the position (y, x) is adjacent to a wall."""
    adjacent_positions = [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
    return any(map_data[ny][nx] == WALL for ny, nx in adjacent_positions)

# 벽에 붙어있지 않은 빈 공간에 상자를 위치
def place_boxes(map_data, goals):
    global goal_count
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_adjacent_to_wall(y, x, map_data)]
    random.shuffle(free_spaces)
    for goal in goals:
        box_pos = free_spaces.pop()
        map_data[box_pos[0]][box_pos[1]] = BOX
        goal_count += 1
    return map_data

#################phase2#################
# 장애물 초기 위치 설정
def place_blue(map_data):
    global blue_pos
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)
    blue_pos = list(free_spaces.pop())
    map_data[blue_pos[0]][blue_pos[1]] = FLOOR  # 장애물 위치는 비어 있어야 합니다.
    return blue_pos

# 폭탄 초기 위치 설정
def place_bombs(map_data, num_bombs):
    global bombs
    bombs = []
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)
    for _ in range(num_bombs):
        bomb_pos = list(free_spaces.pop())
        bombs.append(bomb_pos)
    return bombs

# RED 객체 초기 위치 설정
def place_red(map_data):
    global red_pos
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)
    red_pos = list(free_spaces.pop())
    return red_pos
#################phase2#################

# 맵을 자동으로 생성함
def generate_sokoban_map(width, height, num_goals, num_bombs):
    global player_pos
    while True:
        map_data = create_empty_map(width, height)
        player_pos, goals = place_player_and_goals(map_data, num_goals)
        map_data = place_boxes(map_data, goals)
        place_bombs(map_data, num_bombs)  # 폭탄 배치 추가
        return map_data, player_pos

# 화면에 레벨을 표시함
def draw_level(map_data):
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            screen.blit(floor_image, (x * tile_size, y * tile_size))
            if tile == WALL:
                screen.blit(wall_image, (x * tile_size, y * tile_size))
            elif tile == GOAL:
                screen.blit(goal_image, (x * tile_size, y * tile_size))
            elif tile == BOX:
                screen.blit(box_image, (x * tile_size, y * tile_size))
            elif tile == BOX_ON_GOAL:
                screen.blit(box_on_goal_image, (x * tile_size, y * tile_size))

# 화면에 플레이어를 표시함
def draw_player():
    screen.blit(player_image, (player_pos[1] * tile_size, player_pos[0] * tile_size))

#################phase2#################
# 장애물을 그리는 함수
def draw_blue():
    screen.blit(blue_image, (blue_pos[1] * tile_size, blue_pos[0] * tile_size))

# 폭탄을 그리는 함수
def draw_bombs():
    for bomb_pos in bombs:
        screen.blit(bomb_image, (bomb_pos[1] * tile_size, bomb_pos[0] * tile_size))

# RED 객체를 그리는 함수
def draw_red():
    screen.blit(red_image, (red_pos[1] * tile_size, red_pos[0] * tile_size))
#################phase2#################

# 플레이어의 이동을 정의
def move_player(dx, dy):
    global level
    global goal_count
    new_y = player_pos[0] + dy
    new_x = player_pos[1] + dx

    if level[new_y][new_x] == FLOOR:
        # player가 있던 자리 공백으로 변환
        if level[player_pos[0]][player_pos[1]] == PLAYER_ON_GOAL:
            level[player_pos[0]][player_pos[1]] = GOAL
        else:
            level[player_pos[0]][player_pos[1]] = FLOOR
        # player 이동
        player_pos[0] = new_y
        player_pos[1] = new_x
        if level[player_pos[0]][player_pos[1]] == GOAL:
            level[player_pos[0]][player_pos[1]] = PLAYER_ON_GOAL
        else:
            level[player_pos[0]][player_pos[1]] = PLAYER
    elif level[new_y][new_x] == BOX:
        box_new_y = new_y + dy
        box_new_x = new_x + dx
        if level[box_new_y][box_new_x] in [FLOOR, GOAL]:
            if level[new_y][new_x] == BOX_ON_GOAL:
                return  # 상자가 목표 지점에 있으면 이동하지 않음
            # 상자가 이동할 수 있는 경우
            if level[box_new_y][box_new_x] == FLOOR:
                level[box_new_y][box_new_x] = BOX
            elif level[box_new_y][box_new_x] == GOAL:
                level[box_new_y][box_new_x] = BOX_ON_GOAL
                goal_count -= 1

            if level[player_pos[0]][player_pos[1]] == PLAYER_ON_GOAL:
                level[player_pos[0]][player_pos[1]] = GOAL
            else:
                level[player_pos[0]][player_pos[1]] = FLOOR
            player_pos[0] = new_y
            player_pos[1] = new_x
            level[player_pos[0]][player_pos[1]] = PLAYER
    check_game_over()  # 이동 후 게임 종료 확인

#################phase2#################
# 장애물의 이동을 정의
def move_blue():
    global blue_pos, blue_move_timer, blue_move_interval, player_pos
    current_time = pygame.time.get_ticks()
    if current_time - blue_move_timer > blue_move_interval:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dy, dx in directions:
            new_y, new_x = blue_pos[0] + dy, blue_pos[1] + dx
            if level[new_y][new_x] in [FLOOR, PLAYER]:
                blue_pos = [new_y, new_x]
                break
        blue_move_timer = current_time  # 타이머 갱신
#################phase2#################

# 플레이어가 이겼는지 판단함
def is_win():
    global goal_count
    if goal_count == 0:
        font = pygame.font.SysFont(None, 100)
        text = font.render("YOU WIN!", True, (255, 0, 0))
        screen.blit(text, (screen_width // 2 - 200, screen_height // 2 - 50))
        pygame.display.flip()
        pygame.time.wait(2000)  # 2초간 대기
        reset_game()  # 게임 초기화 함수 호출

#################phase2#################
# 게임 종료 로직
def check_game_over():
    if blue_pos == player_pos:
        game_over("GAME OVER")

# 폭탄과의 충돌 확인
def check_bomb_collision():
    if player_pos in bombs:
        game_over("GAME OVER")

# RED 객체와의 충돌 확인
def check_red_collision():
    global red_pos, blue_move_interval
    if player_pos == red_pos:
        red_pos = [-1, -1]  # RED 객체 제거
        blue_move_interval /= 2  # 장애물 속도 2배 증가
#################phase2#################

# 게임 종료 시 메시지 표시 및 리셋
def game_over(message):
    font = pygame.font.SysFont(None, 100)
    text = font.render(message, True, (255, 0, 0))
    screen.blit(text, (screen_width // 2 - 200, screen_height // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)  # 2초간 대기
    reset_game()

# 새로운 맵을 생성하여 게임 리셋
def reset_game():
    global level, player_pos, goal_count, blue_move_interval
    level, player_pos = generate_sokoban_map(10, 10, 3, 3)
    goal_count = 3  # 목표 갯수 초기화
    place_blue(level)
    place_bombs(level, 3)  # 폭탄 배치 초기화
    place_red(level)  # RED 객체 초기화
    blue_move_interval = 500  # 장애물 속도 초기화

# 시작 메뉴를 표시
def show_menu():
    font = pygame.font.SysFont(None, 50)
    text = ["Press Enter To Start Game", "To See How To Play, Press H"]
    label = []
    position = [screen_width // 2 - 200, screen_height // 2 - 50]
    for line in text:
        label.append(font.render(line, True, (255, 0, 0)))
    for line in range(len(label)):
        screen.blit(label[line], (position[0], position[1] + (line * 50) + (15 * line)))
    pygame.display.flip()

# 조작 방법 등을 표시
def show_controls():
    font = pygame.font.SysFont(None, 32)
    text = ["                                                              Sokoban Rules", "1. Objective: Push all the boxes into the holes.", "2. How to play: You can move player character using arrow keys.", "3. Winning Condition: Fill all the holes with boxes to win.", "4. New Map: A new map will be generated automatically a few seconds after you win.", "                                              To return to main menu, Press 'Esc'"]
    label = []
    position = [screen_width // 2 - 460, screen_height // 2 - 250]
    for line in text:
        label.append(font.render(line, True, (255, 0, 0)))
    for line in range(len(label)):
        screen.blit(label[line], (position[0], position[1] + (line * 50) + (15 * line)))
    pygame.display.flip()

# 메인 루프
def run():
    global level
    global game_state
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == STATE_MENU:
                    if event.key == pygame.K_RETURN:  # Enter 키를 눌러 게임 시작
                        level, player_pos = generate_sokoban_map(10, 10, 3, 3)
                        place_blue(level)
                        place_bombs(level, 3)  # 폭탄 배치 초기화
                        place_red(level)  # RED 객체 초기화
                        game_state = STATE_GAME
                    elif event.key == pygame.K_h:  # H 키를 눌러 조작법 안내
                        game_state = STATE_CONTROLS
                elif game_state == STATE_CONTROLS:
                    if event.key == pygame.K_ESCAPE:  # ESC 키를 눌러 메뉴로 돌아감
                        game_state = STATE_MENU
                elif game_state == STATE_GAME:
                    if event.key == pygame.K_ESCAPE:  # ESC 키를 눌러 메뉴로 돌아감
                        game_state = STATE_MENU
                    elif event.key == pygame.K_UP:
                        move_player(0, -1)
                        check_bomb_collision()
                        check_red_collision()
                        is_win()
                    elif event.key == pygame.K_DOWN:
                        move_player(0, 1)
                        check_bomb_collision()
                        check_red_collision()
                        is_win()
                    elif event.key == pygame.K_LEFT:
                        move_player(-1, 0)
                        check_bomb_collision()
                        check_red_collision()
                        is_win()
                    elif event.key == pygame.K_RIGHT:
                        move_player(1, 0)
                        check_bomb_collision()
                        check_red_collision()
                        is_win()

#################phase2#################
        # 플레이어 이동 후 장애물 이동 및 게임 종료 확인
        if game_state == STATE_GAME:
            move_blue()
            check_game_over()
#################phase2#################

        screen.fill(WHITE)
        if game_state == STATE_MENU:
            show_menu()
        elif game_state == STATE_CONTROLS:
            show_controls()
        elif game_state == STATE_GAME:
            draw_level(level)
            draw_player()
            draw_blue()
            draw_bombs()  # 폭탄 그리기
            if red_pos != [-1, -1]:
                draw_red()  # RED 객체 그리기
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run()
