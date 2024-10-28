from dyna.environment import env
from ..exceptions import SetupAlreadyException, AccountAlreadyException


class SetupService:
    def check_setup(self):
        try:
            account_obj = env["Account"]
            account = account_obj.get({"type": "master"}, first=True)
            if account:
                return True
        except:
            pass
        return False
    
    def setup(self, args: dict):
        if self.check_setup():
            raise SetupAlreadyException()
        
        account_obj = env["Account"]
        account = account_obj.get({"username": args["username"]}, first=True)
        if account is not None:
            raise AccountAlreadyException()
        
        result = account_obj.create({
            "name": args["name"],
            "username": args["username"],
            "status": "active",
            "type": "master",
            "password": args["password"]
        })

        return result.json()