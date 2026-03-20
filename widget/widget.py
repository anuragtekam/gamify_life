import webview
import tkinter as tk
import sys
import ctypes

# ─────────────────────────────────────────────
# CONFIGURATION — edit these to suit your setup
# ─────────────────────────────────────────────

WEBSITE_URL = "https://ritual-eta.vercel.app/"   # ← Your website URL here
                                            # For a local file use:
                                            # "file:///C:/path/to/index.html"

WIDGET_WIDTH = 400     # Width of the widget in pixels

SIDE = "right"         # "right" or "left" — which side of the screen to pin it to
MARGIN = 0             # Gap from the screen edge in pixels

# ─────────────────────────────────────────────


def get_work_area():
    """
    Returns the usable screen area (excluding taskbar) as (x, y, width, height).
    Works on Windows, Mac, and Linux.
    """
    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()

    if sys.platform == "win32":
        # On Windows, use SystemParametersInfo to get the exact work area
        # This accounts for taskbar on any side (bottom, top, left, right)
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                        ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        rect = RECT()
        # SPI_GETWORKAREA = 0x0030
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
        work_x = rect.left
        work_y = rect.top
        work_w = rect.right - rect.left
        work_h = rect.bottom - rect.top
    else:
        # On Mac/Linux, tkinter gives the usable area
        work_x = 0
        work_y = 0
        work_w = root.winfo_screenwidth()
        work_h = root.winfo_screenheight()

    root.destroy()
    return work_x, work_y, work_w, work_h


def send_to_background(window):
    """
    After the window opens, push it behind all other windows.
    Uses Windows API on Win32; on other platforms pywebview's on_top=False is enough.
    """
    if sys.platform != "win32":
        return

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    # Find our window by title
    hwnd = user32.FindWindowW(None, "Widget")
    if not hwnd:
        return

    HWND_BOTTOM   = 1          # Place behind all other windows
    SWP_NOSIZE    = 0x0001
    SWP_NOMOVE    = 0x0002
    SWP_NOACTIVATE = 0x0010

    user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)


def main():
    work_x, work_y, work_w, work_h = get_work_area()

    # Widget fills full height of the usable area (no taskbar overlap)
    widget_height = work_h
    widget_y      = work_y                          # Start right at top of work area

    if SIDE == "right":
        widget_x = work_x + work_w - WIDGET_WIDTH - MARGIN
    else:  # left
        widget_x = work_x + MARGIN

    window = webview.create_window(
        title     = "Widget",
        url       = WEBSITE_URL,
        width     = WIDGET_WIDTH,
        height    = widget_height,
        x         = widget_x,
        y         = widget_y,
        frameless = True,    # No title bar or borders
        on_top    = False,   # Goes behind other windows when you click away
        shadow    = True,
        resizable = False,
        min_size  = (WIDGET_WIDTH, widget_height),
    )

    # Push to background after window is ready
    webview.start(send_to_background, window)


if __name__ == "__main__":
    main()