import cv2
from matplotlib import pyplot as plt

from src.ctype_screenshot import ScreenMirrorWindow, ScreenshotOfWindow
from src.main import main

if __name__ == '__main__':
    #window = ScreenMirrorWindow('AirPlay')
    #with ScreenshotOfWindow(
    #        window.hwnd, client=True, ascontiguousarray=True
    #) as screenshots_window:
    #    img1 = screenshots_window.screenshot_window()
    #print(img1.shape)
    #plt.imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
    #plt.show(block=False)

    #with ScreenshotOfWindow(
    #        hwnd=window.hwnd, client=False, ascontiguousarray=True
    #) as screenshots_window:
    #    img1 = screenshots_window.screenshot_window()
    #print(img1.shape)
    main()
    print('Done')
