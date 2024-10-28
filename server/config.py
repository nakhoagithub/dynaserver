import os

class Config:
    def __init__(self):
        self.CURRENT_VERSION = "v1.0.0"
        self.SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
        self.SERVER_PORT = int(os.environ.get("SERVER_PORT", "8569"))