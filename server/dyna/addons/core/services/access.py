from typing import List
from bson.dbref import DBRef
from dyna.environment import env
from dyna.tools.dict import index_where, delete_keys, merge_dict

from ..models.account import Account
from ..models.permission import Permission
from ..models.role import Role
from ..models.collection import Collection

class AccessService:
    def __init__(self, account: Account | None) -> None:
        self.account = account

    def access(self, id_collection: str | None = None):
        is_master = self.account.type == "master"

        roles: List[Role] = [i for i in self.account.ids_role]
        permissions: List[Permission] = []
        for role in roles:
            for id_p in role.ids_permission:
                permissions.append(id_p)

        datas = []
        if is_master:
            collections: List[Collection] = env["Collection"].get({"active": True})
            for collection in collections:
                datas.append({
                    "id_collection": collection.id,
                    "access_create": True,
                    "access_read": True,
                    "access_update": True,
                    "access_delete": True,
                    "access_report": True,
                    "access_socket": True,
                })
        else:
            for p in permissions:
                if type(p) is DBRef:
                    continue

                index = index_where(datas, lambda e: e["id_collection"] == p.id_collection.id)
                if index == -1:
                    datas.append(p.json())
                else:
                    # merge access
                    datas[index] = merge_dict(datas[index], p.json())
            
            for i in datas:
                delete_keys(i, ["id", "name", "description", "created_at", "modified_at", "public"])

        if id_collection is not None:
            index = index_where(datas, lambda e: e["id_collection"] == id_collection)
            if index != -1:
                datas = datas[index]
            else:
                datas = {
                    "id_collection": id_collection,
                    "access_create": False,
                    "access_read": False,
                    "access_update": False,
                    "access_delete": False,
                    "access_report": False,
                    "access_socket": False
                }
        
        return {
            "access": datas,
        }

