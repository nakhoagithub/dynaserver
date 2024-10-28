import os
from datetime import datetime


def logger_(content: str, name="LOG", filename="server.log", print_console=True):
    try:
        path = os.environ.get("LOG_PATH", ".logs/")

        log_dir = os.path.dirname(path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = f"[{current_time}] {name}: {content}"

        with open(f"{log_dir}/{filename}", "a", encoding="utf-8") as file:
            file.write(content + "\n")

        if print_console:
            print(content)
    except Exception as e:
        print("Đã xảy ra lỗi ghi file log:", str(e))


def log(content: str, name: str = "PRINT"):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"[{current_time}] {name}: {content}"
    print(content)