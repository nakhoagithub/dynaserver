import mongoengine
from mongoengine.errors import OperationError
from typing import List
from dyna.environment import env
from dyna.document import Document
from dyna.tools.dict import delete_keys
from dyna.tools.mongo import duplicate_error

from dyna.http.exceptions import RPCMethodNotFoundException

class DynaRPC:
    def __init__(self, args: dict) -> None:
        self.obj: Document = env[args["name"]]
        self.args = args

    def create(self):
        if "create" not in self.obj.allow_method_crud:
            raise ValueError(f"This {self.args['name']} collection does not allow the use of the create API")

        if self.args["args"] is None:
            raise ValueError(f"'args' is required")

        args: List[dict] = self.args.get("args", []) or []
        datas = []
        errors = []
        for arg in args:
            try:
                new_args = delete_keys(arg, self.obj.ignore_field_create)
                obj = self.obj.create(new_args, rpc=True)
                datas.append(obj.json())
            except mongoengine.errors.NotUniqueError as e:
                key = duplicate_error(str(e))
                
                errors.append({
                    "code": "KEY_UNIQUE",
                    "key": key.split(":")[0],
                    "message": str(e),
                })
            except Exception as e:
                errors.append({
                    "code": "ERROR",
                    "message": str(e)
                })
        return {
            "datas": datas,
            "errors": errors,
        }

    def read(self, total_with_filter=True):
        if "read" not in self.obj.allow_method_crud:
            raise ValueError(f"This {self.args['name']} collection does not allow the use of the reading API")

        results = []
        datas: List[Document] = []

        filter_values = self.args.get("filter", {}) or {}
        skip = self.args.get("skip", 0) or 0
        limit = self.args.get("limit", 0) or 0
        sort = self.args.get("sort", {}) or {}
        ref = self.args.get("ref", {}) or {}
        fields = self.args.get("fields", []) or []
        distinct = self.args.get("distinct")

        datas, total = self.obj.get(
            filter_values=filter_values,
            limit=limit,
            skip=skip,
            sort=sort,
            rpc=True,
            total_with_filter=total_with_filter,
            distinct=distinct,
        )

        for i in datas:
            values = None
            if i.__class__.__base__ is Document:
                values = i.populate(i, ref=ref)
            else:
                values = i
            if len(fields) != 0:
                values = {k: v for k, v in values.items() if k in fields}
            
            results.append(values)

        return {
            "total": total,
            "datas": results,
        }

    def update(self):
        if "update" not in self.obj.allow_method_crud:
            raise ValueError(f"This {self.args['name']} collection does not allow the use of the update API")
        
        if self.args["args"] is None:
            raise ValueError(f"'args' is required")
        
        args: List[dict] = self.args.get("args", []) or []
        updated = []
        errors = []

        for data in args:
            if "id" not in data:
                errors.append({"data": data, "message": "Can't find 'id' in data"})
                continue
                
            new_args = delete_keys(data, self.obj.ignore_field_update)

            obj = self.obj.get(filter_values={"_id": new_args["id"]}, first=True)
            if obj is None:
                errors.append({
                    "id": new_args["id"],
                    "code": "NOT_FOUND",
                    "message": "Data not found"
                })
                continue
            
            try:
                obj.update(new_args, rpc=True)
                updated.append({**new_args})
            except Exception as e:
                errors.append({
                    "id": new_args["id"], 
                    "code": "ERROR",
                    "message": str(e)
                })

        return {
            "datas": updated,
            "errors": errors,
        }

    def delete(self):
        if "delete" not in self.obj.allow_method_crud:
            raise ValueError(f"This {self.args['name']} collection does not allow the use of the delete API")
        
        if self.args["args"] is None:
            raise ValueError(f"'args' is required")
        
        args: List[dict] = self.args.get("args", []) or []

        deleted = []
        errors = []

        for arg in args:
            obj = self.obj.get(filter_values={"_id": arg["id"]}, first=True)
            
            if obj is None:
                errors.append({
                    "data": arg, 
                    "code": "NOT_FOUND",
                    "message": "Data not found"
                })
                continue
            
            try:
                obj.delete(arg["id"], rpc=True)
                deleted.append({
                        "data": arg,
                        "message": "Deleted"
                    })
            except OperationError as e:
                if "Could not delete document" in str(e) and "refers to it" in str(e):
                    errors.append({
                        "id": arg["id"], 
                        "code": "ERROR_REF",
                        "message": str(e)
                    })
                else:
                    errors.append({
                        "id": arg["id"], 
                        "code": "ERROR_OPERATION",
                        "message": str(e)
                    })
            except Exception as e:
                errors.append({
                    "id": arg["id"], 
                    "code": "ERROR",
                    "message": str(e)
                })
            
        return {
            "datas": deleted,
            "errors": errors,
        }
    
    def method(self):
        method_name = self.args["method"]

        if method_name not in self.obj.allow_method_rpc:
            raise ValueError(f"Object does not have this '{method_name}' method")
        
        call = getattr(self.obj, method_name, None)
        if call is None:
            raise RPCMethodNotFoundException()
        
        return call(**self.args)