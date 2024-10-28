from functools import wraps
from dyna.http.exceptions import NotSetupException
from ..services.setup import SetupService

def setup_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not SetupService().check_setup():
            raise NotSetupException()
        return func(*args, **kwargs)
    return wrapper