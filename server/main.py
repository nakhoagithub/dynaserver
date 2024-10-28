import time
from app import run


if __name__ == "__main__":
    run()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except:
            pass