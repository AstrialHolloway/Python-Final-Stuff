"""Cross-platform helper to launch a Python script without showing a console window.

Usage:
    from launch_hidden import launch_python_hidden
    launch_python_hidden('/path/to/script.py', args=['--foo'], wait=False)

Behavior:
 - On Windows: uses CREATE_NO_WINDOW so no console window appears.
 - On POSIX: starts a detached process and redirects stdio to devnull.

If you need the launched script to delay showing any GUI until it's fully
initialized, have that script create its window only after initialization.
Optionally the child can hide/show its console using the `hide_console_until_ready`
helper (Windows only) — see example below.
"""
import os
import sys
import subprocess
import shlex


def launch_python_hidden(script_path, args=None, wait=False):
    """Launch a Python script without a visible console window.

    - script_path: path to the .py file to run
    - args: list of arguments to pass to the script
    - wait: if True, wait for the process to exit and return its exit code
    """
    if args is None:
        args = []

    python_exe = sys.executable or 'python'
    cmd = [python_exe, script_path] + list(args)

    # Redirect stdio to devnull so no console output appears
    devnull = subprocess.DEVNULL

    # Windows: suppress console window
    creationflags = 0
    if os.name == 'nt':
        # CREATE_NO_WINDOW hides the console for console-based programs
        creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

    # Start the process detached / in its own session
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=devnull,
            stderr=devnull,
            stdin=devnull,
            close_fds=True,
            start_new_session=True,
            creationflags=creationflags
        )
    except TypeError:
        # Some Python versions on Windows don't accept start_new_session; fallback
        proc = subprocess.Popen(cmd, stdout=devnull, stderr=devnull, stdin=devnull, close_fds=True, creationflags=creationflags)

    if wait:
        return proc.wait()
    return proc


def hide_console_until_ready():
    """Call this in a child script to hide the console (Windows)."""
    if os.name != 'nt':
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            SW_HIDE = 0
            user32.ShowWindow(hwnd, SW_HIDE)
    except Exception:
        pass


__all__ = ["launch_python_hidden", "hide_console_until_ready"]
