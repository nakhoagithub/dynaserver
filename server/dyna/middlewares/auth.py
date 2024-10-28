from functools import wraps
from dyna.http.api import request
from dyna.environment import env
from dyna.http.exceptions import Unauthorized


def authentication(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        
        public = getattr(request, "ignore_auth", False)
        if public == True:
            return func(self, *args, **kwargs)
        
        account = None
        auth_header = request.headers.get("Authorization")
        session = request.cookies.get("session")
        try:
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                account = env["Account"].get_account_from_api_key(token=token)
                setattr(request, "auth_with_api_key", True)
            
            if session is not None and account is None:
                account = env["Account"].get_account_from_session(session=session)
        except Exception as e:
            pass

        if account is not None:
            setattr(request, "account", account)
            return func(self, *args, **kwargs)
        
        raise Unauthorized()

    return wrapper