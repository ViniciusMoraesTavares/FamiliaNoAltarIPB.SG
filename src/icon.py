import os
import sys

def get_icon_path():
    base = os.path.abspath(".")
    meipass = getattr(sys, "_MEIPASS", None)
    candidates = []
    if meipass:
        candidates += [
            os.path.join(meipass, "assets", "icone.ico"),
            os.path.join(meipass, "imagens", "icone.ico"),
        ]
    candidates += [
        os.path.join(base, "assets", "icone.ico"),
        os.path.join(base, "imagens", "icone.ico"),
        os.path.join(base, "icone.ico"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None
