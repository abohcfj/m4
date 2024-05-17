import dxcam
import cv2
import time
import numpy as np
from PIL import Image

def check_color(image, target_color, tolerance):
    # 获取图像的宽度和高度
    width, height = image.size
    
    # 循环遍历图像的每个像素
    for y in range(height):
        for x in range(width):
            # 获取当前像素的颜色
            current_color = image.getpixel((x, y))
            # 检查当前像素的颜色是否在容差范围内
            if all(abs(c1 - c2) <= tolerance for c1, c2 in zip(current_color, target_color)):
                return True
    # 如果没有找到目标颜色，则返回False
    return False
image = Image.open("obj.png")  # 替换为你的图像路径
print(image)
color_exists = check_color(image,(255,0,0),20)
if color_exists:
    print("图像中存在与目标颜色相近的颜色。")
else:
    print("图像中不存在与目标颜色相近的颜色。")
camera = dxcam.create(output_idx=0)
camera.start(target_fps=120)
image1 = camera.get_latest_frame()
print(image1)
camera.stop()
# while True:
#     image = camera.get_latest_frame()
#     flag = check_color(image,(255,0,0),20)
#     if flag:
#         print('存在')
