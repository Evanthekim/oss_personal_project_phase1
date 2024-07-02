import pygame
import sys
import random
from collections import deque

# 맵 타일 종류
WALL = '#'
FLOOR = ' '
PLAYER = '@'
BOX = '$'
GOAL = '.'
BOX_ON_GOAL = '*'
PLAYER_ON_GOAL = '+'


#비어있는 맵을 생성
def create_empty_map(width, height):
    return [[WALL if x == 0 or x == width - 1 or y == 0 or y == height - 1 else FLOOR for x in range(width)] for y in range(height)]

#비어있는 맵에 플레이어와 구멍을 배치
def place_player_and_goals(map_data, num_goals):
    global player_pos
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR]
    random.shuffle(free_spaces)

    # 플레이어 위치 선정
    temp_pos = list(free_spaces.pop())
    player_pos[0] = temp_pos[0]
    player_pos[1] = temp_pos[1]

    #버그 수정1,3
    map_data[player_pos[1]][player_pos[0]] = PLAYER

    # 목표 지점 선정
    goals = []
    for _ in range(num_goals):
        goal_pos = free_spaces.pop()
        map_data[goal_pos[0]][goal_pos[1]] = GOAL
        goals.append(goal_pos)
    return player_pos, goals

##추가 기능1##
#대상 위치와 벽과의 거리가 distance이상인지 확인
def is_near_to_wall(y, x, map_data):
    distance = 3
    near_positions = []
    width = len(map_data[0])
    height = len(map_data)
    for i in range(distance):
        for j in range(i+1):
            if x+j < width-1:
                if y+(i-j) <height-1:
                    near_positions.append((y+(i-j),x+j))
                if y-(i-j) > 0:
                    near_positions.append((y-(i-j),x+j))
            if x-j > 0:
                if y+(i-j) < height-1:
                    near_positions.append((y+(i-j),x-j))
                if y-(i-j) > 0:
                    near_positions.append((y-(i-j),x-j))

    return any(map_data[ny][nx] == WALL for ny, nx in near_positions)
        
#일정 거리 이상의 공간을 확보한 곳에 벽 생성
def place_wall(map_data):
    wall_type=random.randrange(1,6)
    
    if wall_type<=3:
        free_spaces = [(y,x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_near_to_wall(y, x, map_data)]
        random.shuffle(free_spaces)
    
        if len(free_spaces)>0:
            wall_pos = free_spaces.pop()
            map_data[wall_pos[0]][wall_pos[1]] = WALL
    elif wall_type==4:
        free_spaces = [(y,x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_near_to_wall(y, x, map_data) and map_data[y+1][x] == FLOOR and not is_near_to_wall(y+1, x, map_data)]
        random.shuffle(free_spaces)

        if len(free_spaces)>0:
            wall_pos = free_spaces.pop()
            map_data[wall_pos[0]][wall_pos[1]] = WALL
            map_data[wall_pos[0]+1][wall_pos[1]] = WALL
    elif wall_type==5:
        free_spaces = [(y,x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_near_to_wall(y, x, map_data) and map_data[y][x+1] == FLOOR and not is_near_to_wall(y, x+1, map_data)]
        random.shuffle(free_spaces)

        if len(free_spaces)>0:
            wall_pos = free_spaces.pop()
            map_data[wall_pos[0]][wall_pos[1]] = WALL
            map_data[wall_pos[0]][wall_pos[1]+1] = WALL

    return map_data
            
#############

#대상 위치가 벽에 붙어있는지 확인
def is_adjacent_to_wall(y, x, map_data):
    """Check if the position (y, x) is adjacent to a wall."""
    adjacent_positions = [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
    return any(map_data[ny][nx] == WALL for ny, nx in adjacent_positions)

#벽에 붙어있지 않은 빈 공간에 상자를 위치
def place_boxes(map_data, goals):
    global goal_count
    
    free_spaces = [(y, x) for y, row in enumerate(map_data) for x, tile in enumerate(row) if tile == FLOOR and not is_adjacent_to_wall(y, x, map_data)]
    random.shuffle(free_spaces)

    for goal in goals:
        box_pos = free_spaces.pop()
        map_data[box_pos[0]][box_pos[1]] = BOX
        goal_count += 1
    
    return map_data

# 맵을 자동으로 생성함
def generate_sokoban_map(width, height, num_goals):
    global player_pos
    #버그 수정2
    global goal_count
    goal_count=0
    
    global move
    move = []

    while True:
        map_data = create_empty_map(width, height)
        player_pos, goals = place_player_and_goals(map_data, num_goals)
        
        #추가 기능 1 : 벽생성
        for i in range(5):
            map_data = place_wall(map_data)

        map_data = place_boxes(map_data, goals)
        return map_data, player_pos