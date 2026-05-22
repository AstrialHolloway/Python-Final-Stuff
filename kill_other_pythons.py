"""Utility to terminate other Python processes for use at program startup.

Usage: copy this file into a project and call `kill_other_python_processes()`
at the top of your main script. Requires `psutil` (pip install psutil).

Be careful: this will terminate other Python processes owned by the current
user. Use `dry_run=True` to preview affected processes.
"""
import os
import getpass
import time

try:
    import psutil
except Exception as e:
    psutil = None


def kill_other_python_processes(grace=3, dry_run=False):
    """Terminate other Python processes owned by the current user.

    Parameters:
    - grace: seconds to wait after terminate() before killing remaining procs
    - dry_run: if True, only print which processes would be terminated
    """
    if psutil is None:
        raise ImportError('psutil is required for kill_other_python_processes. Install with `pip install psutil`.')

    me = os.getpid()
    me_user = getpass.getuser()

    targets = []

    for p in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'exe']):
        try:
            info = p.info
            pid = info.get('pid')
            if pid == me:
                continue
            # only consider processes owned by the same user (safer)
            if info.get('username') != me_user:
                continue

            name = (info.get('name') or '').lower()
            cmdline = info.get('cmdline') or []
            exe = (info.get('exe') or '')

            cmd = ' '.join(cmdline) if cmdline else name

            is_python = False
            if 'python' in name or 'python' in cmd.lower() or 'python' in exe.lower():
                is_python = True
            else:
                # scripts invoked directly may include .py in the cmdline
                for part in cmdline:
                    try:
                        if isinstance(part, str) and part.endswith('.py'):
                            is_python = True
                            break
                    except Exception:
                        continue

            if not is_python:
                continue

            targets.append((pid, cmd))

            if dry_run:
                print(f"[kill_other_pythons] Would terminate PID {pid}: {cmd}")
            else:
                try:
                    p.terminate()
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if dry_run:
        return targets

    # wait for graceful termination
    if targets:
        # collect psutil.Process objects for waiting
        procs = []
        for pid, _ in targets:
            try:
                if pid == me:
                    continue
                procs.append(psutil.Process(pid))
            except Exception:
                continue

        gone, alive = psutil.wait_procs(procs, timeout=grace)
        for p in alive:
            try:
                p.kill()
            except Exception:
                pass

    return targets


__all__ = ["kill_other_python_processes"]
