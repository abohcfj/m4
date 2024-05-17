import dxcam
import cv2
import time
import numpy as np
from PIL import Image
import numpy as np

def rgb_distance(rgb1, rgb2):
    return np.sqrt(np.sum((rgb1 - rgb2) ** 2))

target_rgb =[255,0,0]
threshold = 20
camera = dxcam.create(output_idx=0)
camera.start(target_fps=120)
image = camera.get_latest_frame()
image_data = np.array(image)
color_exists = np.any(np.linalg.norm(image_data - target_rgb, axis=-1) <= threshold)
if color_exists:
    print("图像中存在与目标颜色相近的颜色。")
else:
    print("图像中不存在与目标颜色相近的颜色。")
camera.stop()
# while True:
#     image = camera.get_latest_frame()
#     flag = check_color(image,(255,0,0),20)
#     if flag:
#         print('存在')
