import ctypes
import os
import sys

from PySide6.QtGui import QIcon


APP_USER_MODEL_ID = "FamiliaNoAltar.Desktop"


def apply_windows_app_user_model_id():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        pass


def get_icon_path():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cwd = os.path.abspath(".")
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else None
    meipass = getattr(sys, "_MEIPASS", None)

    candidates = []
    for base in [meipass, exe_dir, project_root, cwd]:
        if not base:
            continue
        candidates.extend(
            [
                os.path.join(base, "assets", "icone.ico"),
                os.path.join(base, "imagens", "icone.ico"),
                os.path.join(base, "icone.ico"),
            ]
        )

    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def get_app_icon():
    icon_path = get_icon_path()
    if not icon_path:
        return QIcon()
    return QIcon(icon_path)
