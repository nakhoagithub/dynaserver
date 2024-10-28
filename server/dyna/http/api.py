from typing import Any
from flask import Request, Response
from flask_restful import Api, Resource, abort, reqparse, request
from flask import jsonify

from dyna.environment import apis

__all__ = [
    "reqparse",
    "request",
    "jsonify",
    "Request",
    "Response"
]

# API
api = Api(prefix="/api")

# Resource
class DynaResource(Resource):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        name = cls.__name__
        apis[name] = {
            "active": False,
            "obj": cls()
        }
        return super().__init_subclass__(**kwargs)

    def dispatch_request(self, *args, **kwargs):
        try:
            name = self.__class__.__name__
            api = apis[name]
            if not api.get("active", False):
                return abort(404)
        except Exception as e:
            return abort(404)
        return super().dispatch_request(*args, **kwargs)