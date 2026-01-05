import subprocess
from config.database import DATA_DIR, LOG_FILE

def is_postgres_running() -> bool:
    # pg_ctl status returns 0 if running, 3 if not running
    result = subprocess.run(
        ["pg_ctl", "status", "-D", str(DATA_DIR)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0

def ensure_postgres_started():
    if is_postgres_running():
        return  # already up

    subprocess.run(
        [
            "pg_ctl",
            "start",
            "-D", str(DATA_DIR),
            "-l", str(LOG_FILE),
            "-w",                 # wait until ready
        ],
        check=True,
    )

def stop_postgres(mode: str = "fast"):
    if not is_postgres_running():
        return  # already stopped

    subprocess.run(
        [
            "pg_ctl",
            "stop",
            "-D", str(DATA_DIR),
            "-m", mode,
        ],
        check=True,
    )

