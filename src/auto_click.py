import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumChildWindows = ctypes.windll.user32.EnumChildWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
SendMessage = ctypes.windll.user32.SendMessageW


def getWindowText(hwnd):
    length = GetWindowTextLength(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buffer, length + 1)
    return buffer.value


def match(title, text, exactMatch):
    match = False
    if exactMatch:
        if text == title:
            match = True
    else:
        if 0 < title.find(text):
            match = True
    return match


def search(text, exactMatch, parentHwnd=None):
    resultHwnd = []

    def enumProc(hwnd, lParam, text=text, exactMatch=exactMatch, resultHwnd=resultHwnd):
        title = getWindowText(hwnd)

        if match(title, text, exactMatch):
            resultHwnd.append(hwnd)
            return False

        return True

    if None == parentHwnd:
        EnumWindows(EnumWindowsProc(enumProc), 0)
        return resultHwnd
    else:
        EnumChildWindows(parentHwnd, EnumWindowsProc(enumProc), 0)
        return resultHwnd


def clickButtonByHwnd(buttonHwnd):
    SendMessage(buttonHwnd, 0x00F5, 0, 0)  # 0x00F5 - BM_CLICK


def searchButton(windowTitle, buttonText):
    exactMatch = True
    for hwnd in search(windowTitle, exactMatch):
        for buttonHwnd in search(buttonText, exactMatch, hwnd):
            return buttonHwnd
    return None


# interval - in terms of second
def timeIntervalCall(fn, interval):
    import time
    while True:
        fn()
        time.sleep(interval)


def clickButton(windowTitle, buttonText):
    found = False
    buttonHwnd = searchButton(windowTitle, buttonText)
    if None != buttonHwnd:
        clickButtonByHwnd(buttonHwnd)
        found = True
    return found
