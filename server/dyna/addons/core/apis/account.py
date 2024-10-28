import os
from dyna.http.api import DynaResource, api, reqparse, request, jsonify
from dyna.socketio.socket import disconnect
from dyna.middlewares.auth import authentication
from dyna.middlewares.setup import setup_required
from dyna.environment import env


class AccountAuthenticationAPI(DynaResource):
    @authentication
    def get(self):
        account = getattr(request, "account", None)
        env["Account"].update_last_login(account.id)
        return {
            "code": 200,
            "user": account.json()
        }
    
class LoginAPI(DynaResource):
    @setup_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        account_obj = env["Account"]
        account = account_obj.login(args["username"], args["password"], request)
        session = account.session

        expired_second = int(os.environ.get("LOGIN_EXPIRATION_DATE", "7")) * 86400

        res = jsonify({"code": 200, "user": account.json()})
        # host = request.host.split(":")[0]
        # print(request.host, host)
        res.set_cookie(
            key="session",
            value=session,
            # domain=host,
            max_age=expired_second,
            path="/"
        )
        return res


class LogoutAPI(DynaResource):
    @authentication
    def get(self):
        # account = getattr(request, "account", None)
        # if account:
        #     disconnect(sid=str(account.sid), namespace="/")
        return {"code": 200}, 200, {"Set-Cookie": "session=deleted; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; Path=/;"}


class AccountChangePasswordAPI(DynaResource):
    @authentication
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=str, required=True)
        parser.add_argument("old_password", type=str, required=True)
        parser.add_argument("new_password", type=str, required=True)
        args = parser.parse_args()

        result = env["Account"].change_password(args["id"], args["old_password"], args["new_password"])

        if result:
            return {
                "code": 200
            }


api.add_resource(AccountAuthenticationAPI, "/auth")
api.add_resource(AccountChangePasswordAPI, "/change-password")
api.add_resource(LoginAPI, "/login")
api.add_resource(LogoutAPI, "/logout")