import win32gui
import re


w = win32gui

def _normaliseText(controlText):
    return controlText.lower().replace('&', '')

def _windowEnumerationHandler(hwnd, resultList):
    resultList.append((hwnd, win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd)))

def searchChildWindows(currentHwnd, wantedText=None, wantedClass=None, selectionFunction=None):
    results = []
    childWindows = []

    try:
        win32gui.EnumChildWindows(currentHwnd, _windowEnumerationHandler, childWindows)
    except win32gui.error:
        return

    for childHwnd, windowText, windowClass in childWindows:
        if (wantedText and not _normaliseText(wantedText) in _normaliseText(windowText)) or \
           (wantedClass and not windowClass == wantedClass) or \
           (selectionFunction and not selectionFunction(childHwnd)): continue

        results.append(childHwnd)
    return results

def windowIterator(hwnd, output):
    if w.IsWindowVisible(hwnd) and w.GetClassName(hwnd) == "CabinetWClass":
        output.append(hwnd)

def getExplorerWindowPaths():
    windows = []
    paths = []
    w.EnumWindows(windowIterator, windows)

    for window in windows:
        children = list(set(searchChildWindows(window, wantedClass="ToolbarWindow32")))
        path = None

        for child in children:
            parent = w.GetParent(child)
            window_text = win32gui.GetWindowText(child)
            has_address = re.search(r".:\\", window_text)

            if has_address and w.GetClassName(parent) == "Breadcrumb Parent":
                start_idx = has_address.span()[0]
                path = window_text[start_idx:]

        if path: paths.append(path)

    return paths