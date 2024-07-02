import os
from PIL import Image, ImageDraw

# 모노톤 색상 정의 (Game Boy 스타일)
colors = [(255, 255, 255), (192, 192, 192), (138, 138, 138), (0, 0, 0)]

# 이미지 크기
size = (100, 100)

def create_player():
    img = Image.new('RGB', size, colors[0])
    draw = ImageDraw.Draw(img)
    # 간단한 사람의 앞모습 그리기
    draw.rectangle([40, 20, 60, 40], fill=colors[3]) # 머리
    draw.rectangle([35, 40, 65, 80], fill=colors[2]) # 몸통
    draw.rectangle([45, 80, 50, 95], fill=colors[2]) # 왼쪽 다리
    draw.rectangle([50, 80, 55, 95], fill=colors[2]) # 오른쪽 다리
    draw.rectangle([35, 45, 40, 60], fill=colors[2]) # 왼쪽 팔
    draw.rectangle([60, 45, 65, 60], fill=colors[2]) # 오른쪽 팔
    return img

def create_wall():
    img = Image.new('RGB', size, colors[1])
    draw = ImageDraw.Draw(img)
    # 간단한 벽돌 패턴 그리기
    for x in range(0, 100, 20):
        for y in range(0, 100, 20):
            draw.rectangle([x, y, x+18, y+18], outline=colors[3])
    return img

def create_tile():
    img = Image.new('RGB', size, colors[0])
    draw = ImageDraw.Draw(img)
    # 간단한 타일 패턴 그리기
    for x in range(0, 100, 20):
        for y in range(0, 100, 20):
            draw.rectangle([x, y, x+18, y+18], outline=colors[2])
    return img

def create_box():
    img = Image.new('RGB', size, colors[1])
    draw = ImageDraw.Draw(img)
    # 간단한 상자 그리기
    draw.rectangle([20, 20, 80, 80], fill=colors[2], outline=colors[3])
    return img

def create_box_with_x():
    img = Image.new('RGB', size, colors[1])
    draw = ImageDraw.Draw(img)
    # 상자 그리기
    draw.rectangle([20, 20, 80, 80], fill=colors[2], outline=colors[3])
    # X자 그리기
    draw.line([20, 20, 80, 80], fill=colors[3], width=5)
    draw.line([20, 80, 80, 20], fill=colors[3], width=5)
    return img


def create_hole():
    img = Image.new('RGB', size, colors[0])
    draw = ImageDraw.Draw(img)
    # 간단한 구멍 그리기
    draw.ellipse([20, 20, 80, 80], fill=colors[3])
    return img

# 이미지를 생성하고 저장
images = {
    "player": create_player(),
    "wall": create_wall(),
    "floor": create_tile(),
    "box": create_box(),
    "box_with_x": create_box_with_x(),
    "goal": create_hole()
}

os.makedirs("./assets")

# 저장하기
for name, img in images.items():
    img.save(f"./assets/{name}.png")
