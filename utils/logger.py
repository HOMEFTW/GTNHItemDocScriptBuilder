"""Small logger helper matching the simple desktop-tool style."""
import datetime as _datetime


def log(message: str) -> str:
    line = f"[{_datetime.datetime.now().strftime('%H:%M:%S')}] {message}"
    print(line)
    return line
