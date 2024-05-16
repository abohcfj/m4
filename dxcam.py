import dxcam
import time
camera = dxcam.create()
camera.start(region=(1433,252,1757,694),target_fps=60)
time1 = time.time()
for i in range(1000):
    image = camera.get_latest_frame()
print(time.time()-time1)