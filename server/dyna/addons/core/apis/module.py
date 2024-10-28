
from dyna.http.api import DynaResource, api, reqparse
from dyna.environment import env
from ..exceptions import ModuleNotFoundException

class ModuleAPI(DynaResource):
    def get(self):
        module_obj = env["Module"]
        modules = module_obj.get()
        return {
            "code": 200,
            "result": [
                i.json() for i in modules
            ]
        }


class InstallModuleAPI(DynaResource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=str, required=True)
        parser.add_argument("arg", choices=["install", "uninstall"], type=str, required=True)
        args = parser.parse_args()
        module_obj = env["Module"]

        module = module_obj.get({"id": args["id"]}, first=True)
        if module is None:
            raise ModuleNotFoundException()
        
        result = None
        if args["arg"] == "install":
            result = module_obj.install(args["id"])
        elif args["arg"] == "uninstall":
            result = module_obj.uninstall(args["id"])

        return {
            "code": 200,
            "success": result or False
        }


api.add_resource(ModuleAPI, "/module")
api.add_resource(InstallModuleAPI, "/module/setting")