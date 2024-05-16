import numpy as np
from wechat_ocr.ocr_manager import OcrManager, OCR_MAX_TASK_ID
import re
import time
import configparser
import winsound
import win32api
import win32con
import shutil
import os
import json
import msvcrt  # 用于文件锁定

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8-sig')

wechat_ocr_dir = "C:\\Users\\admin\\AppData\\Roaming\\Tencent\\WeChat\\XPlugin\\Plugins\\WeChatOCR\\7079\\extracted\\WeChatOCR.exe"
wechat_dir = "F:\\WeChat\\[3.9.10.25]"


matchingStr = config['matching']['rule']
timelong = config['sleep']['time']
btimelong = config['sleep']['btime']
ytimelong = config['sleep']['ytime']
globalNumberUrl = config['global_file']['number']
globallockUrl = config['global_file']['lock']
config1 = configparser.ConfigParser()
config1.read(globalNumberUrl, encoding='utf-8-sig')
lastNumber = int(config1['last_number']['number'])

# 定义函数用于读取和修改lastNumber
def read_and_modify_last_number(new_last_number):
    global lastNumber
    global globallockUrl
    try:
        with open(globallockUrl, 'w') as f:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)  # 尝试获取文件锁
            config1.read(globalNumberUrl, encoding='utf-8-sig')
            config1.set('last_number', 'number', str(new_last_number))
            with open(globalNumberUrl, 'w',encoding='utf-8-sig') as configfile:
                config1.write(configfile)
                lastNumber = new_last_number
                print("识别码已经修改为:", lastNumber)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)  # 释放文件锁
    except IOError:
        print("无法获取文件锁")


def ocr_result_callback(img_path:str, results:dict):
    global lastNumber
    if(results['ocrResult']):
        for i in range(0,len(results['ocrResult'])):
            flag = re.search(matchingStr,results['ocrResult'][i]['text'])
            if(flag):
                match = re.search(r'\d{6}', results['ocrResult'][i]['text'])
                number = match.group()
                if(number!=lastNumber):
                    
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
                    lastNumber = number
                    copy_and_rename_file(img_path,'./'+day,number+'-'+ date)
                    read_and_modify_last_number(lastNumber)
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
ocr_manager.StartWeChatOCR()

while True:
    ocr_manager.DoOCRTask('obj.png')
    while ocr_manager.m_task_id.qsize() != OCR_MAX_TASK_ID:
        pass
    

