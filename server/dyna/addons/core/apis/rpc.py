from functools import wraps
from dyna.http.api import DynaResource, api, reqparse, request, jsonify, Response
from dyna.environment import env
from dyna.middlewares.auth import authentication
from dyna.middlewares.access import check_access
from dyna.tools.valid import valid_dict, valid_list
from dyna.http.exceptions import RPCError, DynaHTTPException
from dyna.http.rpc import DynaRPC

from ..services.access import AccessService
from ..exceptions import CollectionNotFoundException, CollectionDeactiveException, MethodInvalidException


def _check_collection(func):
    @wraps(func)
    def decorated(self, *args, **kwargs):
        data: dict = request.get_json()
        name = data.get("name", None)
        collection_obj = env["Collection"]
        collection = collection_obj.get({"id": name}, first=True)

        if collection is None or not collection.active:
            raise CollectionDeactiveException(f"Collection '{name}' deactive")

        if name is not None and env.get(name, None) is not None:
            pass
        else:
            raise CollectionNotFoundException(f"Collection '{name}' not found")
        
        method = data.get("method", None)
        if method in ["create", "read", "update", "delete"]:
            setattr(request, "rpc_collection_method", method)
            setattr(request, "rpc_collection_name", name)

        return func(self, *args, **kwargs)
    return decorated


class DynaAccessAPI(DynaResource):
    @authentication
    def get(self):
        try:
            account = getattr(request, "account", None)
            rpc = AccessService(account)
            return {
                "code": 200,
                **rpc.access()
            }
        except Exception as e:
            raise RPCError(description=str(e))
    
    @authentication
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id_collection", type=str, location="json")
        args = parser.parse_args()
        try:
            account = getattr(request, "account", None)
            rpc = AccessService(account)
            return {
                "code": 200,
                **rpc.access(id_collection=args["id_collection"])
            }
        except Exception as e:
            raise RPCError(description=str(e))


class RPCAPI(DynaResource):
    @_check_collection
    @authentication
    @check_access
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, location="json")
        parser.add_argument("method", type=str, required=True, location="json")
        parser.add_argument("args", type=valid_list, location="json")
        parser.add_argument("filter", type=valid_dict, location="json")
        parser.add_argument("sort", type=valid_dict, location="json")
        parser.add_argument("limit", type=int, location="json")
        parser.add_argument("skip", type=int, location="json")
        parser.add_argument("fields", type=valid_list, location="json")
        parser.add_argument("ref", type=valid_dict, location="json")
        parser.add_argument("distinct", type=str, location="json")
        args = parser.parse_args()

        try:
            rpc = DynaRPC(args)

            data = {}
            if args["method"] == "create":
                data = rpc.create()
            if args["method"] == "read":
                data = rpc.read()
            if args["method"] == "update":
                data = rpc.update()
            if args["method"] == "delete":
                data = rpc.delete()
            if args["method"] not in ["create", "read", "update", "delete"]: 
                result = rpc.method()
                if type(result) == Response:
                    return result
                else:
                    if result:
                        data = result
            
            return {
                "code": 200,
                **data,
            }
        
        except Exception as e:
            if len(type(e).__bases__) > 0 and type(e).__bases__[0] is DynaHTTPException:
                raise e
            raise RPCError(description=str(e))


api.add_resource(RPCAPI, "/db")
api.add_resource(DynaAccessAPI, "/access")