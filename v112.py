import dxcam
import numpy as np
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
import re
import time
import cv2
import configparser
import winsound
import win32api
import win32con
import shutil
import os
import json

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')



# 创建相机对象
cam = dxcam.create(device_idx=0, output_idx=0)
time.sleep(0.1)
def get_screen_size():
    # 获取屏幕尺寸
    try:
        screen_width, screen_height = pyautogui.size()
        print('当前屏幕尺寸：',screen_width, screen_height)
        return screen_width, screen_height
    except Exception as e:
        print("无法获取屏幕尺寸:", e)
        return None, None

def adjust_region(region):
    # 获取屏幕尺寸
    screen_width, screen_height = get_screen_size()
    if screen_width is None or screen_height is None:
        print("无法获取屏幕尺寸，将不进行边界检查")
        return region
    
    # 如果指定区域超出屏幕范围，则调整区域大小
    x1, y1, x2, y2 = region
    x1 = max(0, min(x1, screen_width))
    y1 = max(0, min(y1, screen_height))
    x2 = max(0, min(x2, screen_width))
    y2 = max(0, min(y2, screen_height))
    
    return (x1, y1, x2, y2)

# 获取左上坐标
first_point = tuple(map(int, config['coordinates']['first_point'].split(',')))

# 获取右下坐标
second_point = tuple(map(int, config['coordinates']['second_point'].split(',')))

wechat_ocr_dir = config['wechat']['wechat_ocr_dir']
wechat_dir = config['wechat']['wechat_dir']

matchingStr = config['matching']['rule']
timelong = config['sleep']['time']
btimelong = config['sleep']['btime']
ytimelong = config['sleep']['ytime']


# 调整屏幕区域
region = adjust_region((first_point[0], first_point[1], second_point[0], second_point[1]))

# 更新左上和右下坐标
first_point = (region[0], region[1])
second_point = (region[2], region[3])
lastNumber = 0

def ocr_result_callback(img_path:str, results:dict):
    global lastNumber
    if(results['ocrResult']):
        for i in range(0,len(results['ocrResult'])):
            flag = re.search(matchingStr,results['ocrResult'][i]['text'])
            if(flag):
                match = re.search(r'\d{6}', results['ocrResult'][i]['text'])
                number = match.group()
                if(number!=lastNumber):
                    lastNumber = number
                    # 模拟键盘输入
                    for k in list(number):
                        win32api.keybd_event(numberToaic[k], 0, 0, 0)  # a按下
                        win32api.keybd_event(numberToaic[k],0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
                    # 按下回车键进行搜索
                    win32api.keybd_event(13, 0, 0, 0)  # enter按下
                    win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
                    time.sleep(float(btimelong))
                    win32api.keybd_event(66, 0, 0, 0)  # b按下
                    win32api.keybd_event(66,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
                    time.sleep(float(ytimelong))
                    win32api.keybd_event(89, 0, 0, 0)  # Y按下
                    win32api.keybd_event(89,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
                    play_notification_sound()
                    with open('./data.json', 'w', encoding='utf-8') as f:
                        f.write(json.dumps(results, ensure_ascii=False, indent=2))
                    time1 = time.time()
                    day = time.strftime("%Y-%m-%d", time.localtime(time1))
                    date = time.strftime("%H%M%S", time.localtime(time1))
                    copy_and_rename_file(img_path,'./'+day,number+'-'+ date)
                    print('休眠中...')
                    time.sleep(float(timelong))
                break

def copy_and_rename_file(src_file, dest_folder, new_filename):
    # 创建目标文件夹（如果不存在）
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 拷贝文件到目标文件夹
    shutil.copy(src_file, dest_folder)

    # 获取文件名和扩展名
    file_name, file_extension = os.path.splitext(src_file)

    # 构建新的文件路径（包含目标文件夹和新的文件名）
    dest_file = os.path.join(dest_folder, new_filename + file_extension)

    # 重命名文件
    os.rename(os.path.join(dest_folder, os.path.basename(src_file)), dest_file)

# 在识别完成后播放系统提示音
def play_notification_sound():
    winsound.Beep(1000, 500)  # 播放1000 Hz频率的声音，持续500毫秒


numberToaic = {
    "0":48,"1":49,"2":50,"3":51,"4":52,"5":53,"6":54,"7":55,"8":56,"9":57
}
ocr_manager = OcrManager(wechat_dir)
# 设置WeChatOcr目录
ocr_manager.SetExePath(wechat_ocr_dir)
# 设置微信所在路径
ocr_manager.SetUsrLibDir(wechat_dir)
# 设置ocr识别结果的回调函数
ocr_manager.SetOcrResultCallback(ocr_result_callback)

while True:
    # 抓取图像 指定屏幕区域
    img = cam.grab(region=region)
    if img is not None:
        # 检查图像是否有效
        if np.mean(img) != 0:
            cv2.imwrite('obj.png', img)
            ocr_manager.StartWeChatOCR()
            ocr_manager.DoOCRTask('./obj.png')
            while ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
                pass

