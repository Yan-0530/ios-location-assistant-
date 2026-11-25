"""Set DPI awareness before Tk creates its first HWND when run from source."""
import ctypes
import sys

def enable_native_dpi():
    if sys.platform != 'win32':
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except AttributeError:
        ctypes.windll.user32.SetProcessDPIAware()
