import ctypes
from ctypes import wintypes
from collections import namedtuple
import numpy as np

windll = ctypes.LibraryLoader(ctypes.WinDLL)
windll.shcore.SetProcessDpiAwareness(2)
user32 = ctypes.WinDLL("user32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
from ctypes.wintypes import (
    BOOL,
    DWORD,
    HBITMAP,
    HDC,
    HGDIOBJ,
    HWND,
    INT,
    LONG,
    UINT,
    WORD,
)


SRCCOPY = 13369376
DIB_RGB_COLORS = BI_RGB = 0
WindowInfo = namedtuple("WindowInfo", "pid title hwnd length tid status")
if not hasattr(wintypes, "LPDWORD"):
    wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", DWORD * 3)]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def check_zero(result, func, args):
    if not result:
        err = ctypes.get_last_error()
        if err:
            raise ctypes.WinError(err)
    return args

# from https://github.com/Soldie/Stitch-Rat-pyton/blob/8e22e91c94237959c02d521aab58dc7e3d994cea/Configuration/mss/windows.py
GetClientRect = windll.user32.GetClientRect
GetWindowRect = windll.user32.GetWindowRect
SetWindowPos = windll.user32.SetWindowPos
user32.SetWindowPos.errcheck = check_zero
PrintWindow = windll.user32.PrintWindow
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
IsWindowVisible = windll.user32.IsWindowVisible
EnumWindows = windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(
    ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
)
user32.FindWindowW.argtypes = wintypes.LPCWSTR,wintypes.LPCWSTR
user32.FindWindowW.restype = wintypes.HWND
user32.GetWindowRect.argtypes = wintypes.HWND,ctypes.POINTER(RECT)
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetWindowRect.errcheck = check_zero


GetWindowDC = windll.user32.GetWindowDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
DeleteObject = windll.gdi32.DeleteObject
GetDIBits = windll.gdi32.GetDIBits

windll.user32.GetWindowDC.argtypes = [HWND]
windll.gdi32.CreateCompatibleDC.argtypes = [HDC]
windll.gdi32.CreateCompatibleBitmap.argtypes = [HDC, INT, INT]
windll.gdi32.SelectObject.argtypes = [HDC, HGDIOBJ]
windll.gdi32.BitBlt.argtypes = [HDC, INT, INT, INT, INT, HDC, INT, INT, DWORD]
windll.gdi32.DeleteObject.argtypes = [HGDIOBJ]
windll.gdi32.GetDIBits.argtypes = [
    HDC,
    HBITMAP,
    UINT,
    UINT,
    ctypes.c_void_p,
    ctypes.POINTER(BITMAPINFO),
    UINT,
]
windll.user32.GetWindowDC.restypes = HDC
windll.gdi32.CreateCompatibleDC.restypes = HDC
windll.gdi32.CreateCompatibleBitmap.restypes = HBITMAP
windll.gdi32.SelectObject.restypes = HGDIOBJ
windll.gdi32.BitBlt.restypes = BOOL
windll.gdi32.GetDIBits.restypes = INT
windll.gdi32.DeleteObject.restypes = BOOL


WNDENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,  # _In_ hWnd
    wintypes.LPARAM,
)  # _In_ lParam

user32.EnumWindows.errcheck = check_zero
user32.EnumWindows.argtypes = (
    WNDENUMPROC,  # _In_ lpEnumFunc
    wintypes.LPARAM,
)  # _In_ lParam

user32.IsWindowVisible.argtypes = (wintypes.HWND,)  # _In_ hWnd

user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = (
    wintypes.HWND,  # _In_      hWnd
    wintypes.LPDWORD,
)  # _Out_opt_ lpdwProcessId

user32.GetWindowTextLengthW.errcheck = check_zero
user32.GetWindowTextLengthW.argtypes = (wintypes.HWND,)  # _In_ hWnd

user32.GetWindowTextW.errcheck = check_zero
user32.GetWindowTextW.argtypes = (
    wintypes.HWND,  # _In_  hWnd
    wintypes.LPWSTR,  # _Out_ lpString
    ctypes.c_int,
)  # _In_  nMaxCount


psapi.EnumProcesses.errcheck = check_zero
psapi.EnumProcesses.argtypes = (
    wintypes.LPDWORD,  # _Out_ pProcessIds
    wintypes.DWORD,  # _In_  cb
    wintypes.LPDWORD,
)  # _Out_ pBytesReturned


CreateDIBSection = windll.gdi32.CreateDIBSection
CreateDCW = windll.gdi32.CreateDCW
DeleteDC = windll.gdi32.DeleteDC
sizeof_BITMAPINFOHEADER = ctypes.sizeof(BITMAPINFOHEADER)

class ScreenMirrorWindow:
    def __init__(
        self, title: str
    ):
        self.hwnd = None
        self.rect = None
        self.title = title
        self.__find_window()

    def __find_window(self):
        self.hwnd = user32.FindWindowW(None, self.title)
        if self.hwnd:
            self.rect = RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(self.rect))
        else:
            raise RuntimeError(f"Can't find window called '{self.title}'")

    def resize(self, width: int, height: int):
        user32.SetWindowPos(self.hwnd, 0, self.rect.left, self.rect.top, width, height, 0)


class ScreenshotOfWindow:
    def __init__(
        self, hwnd: int, client: bool = False, ascontiguousarray: bool = False
    ):
        """Class for taking screenshots of a specific window.

        Args:
            hwnd (int): The handle of the window to capture.
            client (bool, optional): Whether to capture the client area of the window.
                Defaults to False.
            ascontiguousarray (bool, optional): Whether to return the image as a contiguous array.
                Defaults to False.

        Returns:
            np.ndarray: The screenshot image as a NumPy array.

        """
        self.hwnd = hwnd
        self.client = client
        self.rect = RECT()
        self.rect_ref = ctypes.byref(self.rect)
        self.hwndDC = GetWindowDC(self.hwnd)
        self.saveDC = CreateCompatibleDC(self.hwndDC)
        self.bmp = None
        self.imagex = None
        self.bmi = None
        self.ascontiguousarray = ascontiguousarray
        self.old_width = -1
        self.old_height = -1
        self.old_left, self.old_right, self.old_top, self.old_bottom = -1, -1, -1, -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.hwndDC:
                try:
                    DeleteObject(self.hwndDC)
                except Exception:
                    pass
            if self.saveDC:
                try:
                    DeleteObject(self.saveDC)
                except Exception:
                    pass
            if self.bmp:
                try:
                    DeleteObject(self.bmp)
                except Exception:
                    pass
            try:
                del self.rect
            except Exception:
                pass
            try:
                del self.imagex
            except Exception:
                pass
            try:
                del self.bmi
            except Exception:
                pass
        except Exception as fa:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        return self.screenshot_window()

    def _create_bmi(self, w, h):
        self.bmi = BITMAPINFO()
        self.bmi.bmiHeader.biSize = sizeof_BITMAPINFOHEADER
        self.bmi.bmiHeader.biWidth = w
        self.bmi.bmiHeader.biHeight = -h
        self.bmi.bmiHeader.biPlanes = 1
        self.bmi.bmiHeader.biBitCount = 32
        self.bmi.bmiHeader.biCompression = 0
        self.bmi.bmiHeader.biClrUsed = 0
        self.bmi.bmiHeader.biClrImportant = 0

    def get_rect_coords(self):
        left, right, top, bottom = (
            self.rect.left,
            self.rect.right,
            self.rect.top,
            self.rect.bottom,
        )
        w, h = right - left, bottom - top
        values_are_the_same = (left, right, top, bottom, w, h) == (
            self.old_left,
            self.old_right,
            self.old_top,
            self.old_bottom,
            self.old_width,
            self.old_height,
        )
        return left, right, top, bottom, w, h, values_are_the_same, h * w * 4

    def screenshot_window(self) -> np.ndarray:
        if self.client:
            GetClientRect(self.hwnd, self.rect_ref)
        else:
            GetWindowRect(self.hwnd, self.rect_ref)

        (
            left,
            right,
            top,
            bottom,
            w,
            h,
            values_are_the_same,
            buffer_len,
        ) = self.get_rect_coords()

        if not values_are_the_same:
            self.bmp = CreateCompatibleBitmap(self.hwndDC, w, h)
            SelectObject(self.saveDC, self.bmp)
        if self.client:
            PrintWindow(self.hwnd, self.saveDC, 3)
        else:
            PrintWindow(self.hwnd, self.saveDC, 0)

        if not values_are_the_same:
            self._create_bmi(w, h)
            self.imagex = ctypes.create_string_buffer(buffer_len)

        windll.gdi32.GetDIBits(
            self.saveDC, self.bmp, 0, h, self.imagex, self.bmi, DIB_RGB_COLORS
        )
        (
            self.old_left,
            self.old_right,
            self.old_top,
            self.old_bottom,
            self.old_width,
            self.old_height,
        ) = (left, right, top, bottom, w, h)
        image2 = bytearray(h * w * 3)
        image2[0::3], image2[1::3], image2[2::3] = self.imagex[2::4], self.imagex[1::4], self.imagex[0::4]
        return (
            np.frombuffer(bytes(image2), dtype=np.uint8)
            .reshape((h, w, 3))[..., ::-1]
            .copy()
        )
