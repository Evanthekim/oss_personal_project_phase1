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
pygame.display.set_caption("Sokoban Multiplayer")

# 색상 설정
WHITE = (255, 255, 255)

# 이미지 로드
player1_image = pygame.image.load('./assets/player1.png')
player2_image = pygame.image.load('./assets/player2.png')
wall_image = pygame.image.load('./assets/wall.png')
box_image = pygame.image.load('./assets/box.png')
goal_image = pygame.image.load('./assets/goal.png')
floor_image = pygame.image.load('./assets/floor.png')
box_on_goal_image = pygame.image.load('./assets/box_with_x.png')

# 타일 크기 설정
tile_size = 100

# 맵 타일 종류
WALL = '#'
FLOOR = ' '
PLAYER1 = '1'
PLAYER2 = '2'
BOX = '$'
GOAL = '.'
BOX_ON_GOAL = '*'
PLAYER1_ON_GOAL = '+'
PLAYER2_ON_GOAL = '&'
OBSTACLE = 'O'

# 방향 벡터
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# 게임 상태
STATE_MENU = 0
STATE_GAME = 1
STATE_CONTROLS = 2
game_state = STATE_MENU

# 맵 데이터
level = []
player1_pos = [0, 0]
player2_pos = [0, 0]
goal_count = 0
undo_stack = deque()
moving_obstacles = []

class MovingObstacle:
    def __init__(self, pos):
        self.pos = pos
        self.direction = random.choice(DIRS)
        self.move_timer = 0

    def move(self, map_data, dt):
        self.move_timer += dt
        if self.move_timer >= 1500:
            next_pos = (self.pos[0] + self.direction[0], self.pos[1] + self.direction[1])
            if map_data[next_pos[1]][next_pos[0]] == FLOOR:
                self.pos = next_pos
            else:
                self.direction = random.choice(DIRS)
            self.move_timer = 0

def create_empty_map(width, height):
    return [[WALL if x == 0 or x == width - 1 or y == 0 or y == height - 1 else FLOOR for x in range(width)] for y in range(height)]

def place_players_and_goals(map_data, num_goals):
    global player1_pos, player2_pos
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)

    temp_pos1 = list(free_spaces.pop())
    player1_pos[0] = temp_pos1[0]
    player1_pos[1] = temp_pos1[1]
    map_data[player1_pos[0]][player1_pos[1]] = PLAYER1

    temp_pos2 = list(free_spaces.pop())
    player2_pos[0] = temp_pos2[0]
    player2_pos[1] = temp_pos2[1]
    map_data[player2_pos[0]][player2_pos[1]] = PLAYER2

    goals = []
    for _ in range(num_goals):
        goal_pos = free_spaces.pop()
        map_data[goal_pos[0]][goal_pos[1]] = GOAL
        goals.append(goal_pos)
    return player1_pos, player2_pos, goals

def is_adjacent_to_wall(y, x, map_data):
    adjacent_positions = [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
    return any(map_data[ny][nx] == WALL for ny, nx in adjacent_positions)

def place_boxes(map_data, goals):
    global goal_count
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_adjacent_to_wall(y, x, map_data)]
    random.shuffle(free_spaces)

    for goal in goals:
        box_pos = free_spaces.pop()
        map_data[box_pos[0]][box_pos[1]] = BOX
        goal_count += 1

    return map_data

def place_obstacles(map_data, num_obstacles):
    global moving_obstacles
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)

    for _ in range(num_obstacles):
        if not free_spaces:
            break
        obstacle_pos = free_spaces.pop()
        moving_obstacles.append(MovingObstacle(obstacle_pos))
    
    return map_data

def generate_sokoban_map(width, height, num_goals, num_obstacles=5):
    global player1_pos, player2_pos
    while True:
        map_data = create_empty_map(width, height)
        player1_pos, player2_pos, goals = place_players_and_goals(map_data, num_goals)
        map_data = place_boxes(map_data, goals)
        map_data = place_obstacles(map_data, num_obstacles)
        return map_data, player1_pos, player2_pos

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

def draw_obstacles():
    for obstacle in moving_obstacles:
        screen.blit(wall_image, (obstacle.pos[0] * tile_size, obstacle.pos[1] * tile_size))

def draw_players():
    screen.blit(player1_image, (player1_pos[0] * tile_size, player1_pos[1] * tile_size))
    screen.blit(player2_image, (player2_pos[0] * tile_size, player2_pos[1] * tile_size))

def move_player(player, dx, dy):
    global level
    global goal_count
    global undo_stack

    if player == 1:
        new_x = player1_pos[0] + dx
        new_y = player1_pos[1] + dy
        current_pos = player1_pos
        player_char = PLAYER1
    else:
        new_x = player2_pos[0] + dx
        new_y = player2_pos[1] + dy
        current_pos = player2_pos
        player_char = PLAYER2

    if any(obstacle.pos == (new_x, new_y) for obstacle in moving_obstacles):
        return

    if level[new_y][new_x] in " $":
        undo_stack.append((player1_pos[:], player2_pos[:], [row[:] for row in level], goal_count))

        if level[new_y][new_x] == " ":
            level[current_pos[1]][current_pos[0]] = " "
            current_pos[0] = new_x
            current_pos[1] = new_y
            level[current_pos[1]][current_pos[0]] = player_char
        elif level[new_y][new_x] == '$':
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            if level[box_new_y][box_new_x] in " .":
                level[new_y][new_x] = ' '
                level[current_pos[1]][current_pos[0]] = " "
                current_pos[0] = new_x
                current_pos[1] = new_y
                level[current_pos[1]][current_pos[0]] = player_char
                if level[box_new_y][box_new_x] == " ":
                    level[box_new_y][box_new_x] = '$'
                elif level[box_new_y][box_new_x] == ".":
                    level[box_new_y][box_new_x] = '*'
                    goal_count -= 1

def undo_move():
    global player1_pos, player2_pos
    global level
    global goal_count
    global undo_stack

    if undo_stack:
        player1_pos, player2_pos, level, goal_count = undo_stack.pop()

def is_win():
    global goal_count
    if goal_count == 0:
        font = pygame.font.SysFont(None, 100)
        text = font.render("YOU WIN!", True, (255, 0, 0))
        screen.blit(text, (screen_width // 2 - 200, screen_height // 2 - 50))
        pygame.display.flip()
        pygame.time.wait(2000)
        reset_game()

def reset_game():
    global level, player1_pos, player2_pos, undo_stack
    level, player1_pos, player2_pos = generate_sokoban_map(10, 10, 3, 5)
    undo_stack.clear()

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

def run():
    global level
    global game_state
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == STATE_MENU:
                    if event.key == pygame.K_RETURN:
                        level, player1_pos, player2_pos = generate_sokoban_map(10, 10, 3, 5)
                        game_state = STATE_GAME
                    elif event.key == pygame.K_h:
                        game_state = STATE_CONTROLS
                elif game_state == STATE_CONTROLS:
                    if event.key == pygame.K_ESCAPE:
                        game_state = STATE_MENU
                elif game_state == STATE_GAME:
                    if event.key == pygame.K_ESCAPE:
                        game_state = STATE_MENU
                    elif event.key == pygame.K_w:
                        move_player(1, 0, -1)
                        is_win()
                    elif event.key == pygame.K_s:
                        move_player(1, 0, 1)
                        is_win()
                    elif event.key == pygame.K_a:
                        move_player(1, -1, 0)
                        is_win()
                    elif event.key == pygame.K_d:
                        move_player(1, 1, 0)
                        is_win()
                    elif event.key == pygame.K_UP:
                        move_player(2, 0, -1)
                        is_win()
                    elif event.key == pygame.K_DOWN:
                        move_player(2, 0, 1)
                        is_win()
                    elif event.key == pygame.K_LEFT:
                        move_player(2, -1, 0)
                        is_win()
                    elif event.key == pygame.K_RIGHT:
                        move_player(2, 1, 0)
                        is_win()
                    elif event.key == pygame.K_z:
                        undo_move()

        screen.fill(WHITE)
        if game_state == STATE_MENU:
            show_menu()
        elif game_state == STATE_CONTROLS:
            show_controls()
        elif game_state == STATE_GAME:
            for obstacle in moving_obstacles:
                obstacle.move(level, dt)
            draw_level(level)
            draw_obstacles()
            draw_players()
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run()
