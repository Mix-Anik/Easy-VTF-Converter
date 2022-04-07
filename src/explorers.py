import win32gui as w
import re


def _normalise_text(controlText):
    return controlText.lower().replace('&', '')


def _window_enumeration_handler(hwnd, result_list):
    result_list.append((hwnd, w.GetWindowText(hwnd), w.GetClassName(hwnd)))


def find_child_windows(current_hwnd, wanted_class=None):
    results = []
    children = []

    try:
        w.EnumChildWindows(current_hwnd, _window_enumeration_handler, children)
    except w.error:
        return

    for child_hwnd, _, window_class in children:
        if wanted_class and not window_class == wanted_class:
            continue

        results.append(child_hwnd)

    return results


def window_iterator(hwnd, output):
    if w.IsWindowVisible(hwnd) and w.GetClassName(hwnd) == "CabinetWClass":
        output.append(hwnd)


def get_explorer_window_paths():
    windows = []
    paths = []
    w.EnumWindows(window_iterator, windows)

    for window in windows:
        children = list(set(find_child_windows(window, wanted_class="ToolbarWindow32")))
        path = None

        for child in children:
            parent = w.GetParent(child)
            window_text = w.GetWindowText(child)
            has_address = re.search(r".:\\", window_text)

            if has_address and w.GetClassName(parent) == "Breadcrumb Parent":
                start_idx = has_address.span()[0]
                path = window_text[start_idx:]

        if path: paths.append(path)

    return paths
