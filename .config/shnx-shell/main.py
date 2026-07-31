from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

from shnx_shell.brain.application import run


if __name__ == "__main__":
    raise SystemExit(run())
