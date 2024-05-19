import win32api
import win32con
import win32gui


class WindowControl:
    def __init__(
            self, title: str
    ):
        self.title = title
        self.hwnd = self.__find_window()

    def __find_window(self):
        hwnd = win32gui.FindWindow(None, self.title)
        if not hwnd:
            raise Exception(f"Can't find window called '{self.title}'")
        else:
            return hwnd

    def set_focus_to_window(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -10000 ,-10000)
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.BringWindowToTop(self.hwnd)
        win32gui.SetForegroundWindow(self.hwnd)

    def top_most(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        self.set_focus_to_window()

    def minimize(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def hide(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def send_to_back(self):
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
