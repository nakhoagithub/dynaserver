from dyna.http.api import DynaResource, api, reqparse
from ..services.setup import SetupService

class SetupAPI(DynaResource):
    def get(self):
        result = SetupService().check_setup()
        return {
            "code": 200,
            "setup_already": result
        }
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True)
        parser.add_argument("username", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()
        SetupService().setup(args)
        return {
            "code": 200
        }
    
api.add_resource(SetupAPI, "/setup")