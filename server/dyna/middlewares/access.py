from functools import wraps
from typing import Literal, List
from dyna.http.api import request
from dyna.http.exceptions import Forbidden
from dyna.environment import env
from bson import DBRef

TypeAccess = Literal["create", "read", "update", "delete", "duplicate", "report", "socket"]


def _get_access(id_collection: str, account, type_access: TypeAccess):
    if account is None:
        return False

    # check master
    if account.id_type.id == "master":
        return True
    
    # check role of user
    roles = [i for i in account.ids_role]
    ids_permission: List[str] = []
    for role in roles:
        if type(role) == DBRef:
            continue
        for permission in role.ids_permission:
            ids_permission.append(permission.id)
    permission_obj = env["Permission"]
    permission = permission_obj.get({"id": {"$in": ids_permission}, "id_collection": id_collection, f"access_{type_access}": True}, first=True)
    if permission is not None:
        return True
    return False


def check_access(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        if getattr(request, "ignore_auth", False) == True:
            return func(self, *args, **kwargs)

        collection_name: str | None = getattr(request, "rpc_collection_name", None)
        if collection_name is not None:

            account = getattr(request, "account", None)

            access = _get_access(collection_name, account, getattr(request, "rpc_collection_method"))
            if access:
                return func(self, *args, **kwargs)
            else:
                raise Forbidden()
            
        return func(self, *args, **kwargs)
    return wrapper
