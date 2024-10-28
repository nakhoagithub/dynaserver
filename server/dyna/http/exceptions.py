
from typing import Optional
from werkzeug.exceptions import HTTPException


class DynaHTTPException(HTTPException):
    error_code: str = None
    warning_code: str = None
    data: Optional[dict] = None

    def __init__(self, description=None, response=None):
        super().__init__(description, response)

        result = {
            "code": self.code or 400,
            "message": self.description or "Bad request"
        }

        if self.error_code:
            result["error_code"] = self.error_code
        if self.warning_code:
            result["warning_code"] = self.warning_code

        self.data = result

class NotSetupException(DynaHTTPException):
    error_code = "NOT_SETUP"
    description = "Setup is required"
    code = 400

class BadRequest(DynaHTTPException):
    error_code = "BAD_REQUEST"
    description = "Bad request"
    code = 400

class Unauthorized(DynaHTTPException):
    error_code = "UNAUTHORIZED"
    description = "Unauthorized"
    code = 401

class Forbidden(DynaHTTPException):
    error_code = "FORBIDEN"
    description = "Forbiden"
    code = 403

class NotFound(DynaHTTPException):
    error_code = "NOT_FOUND"
    description = "Not found"
    code = 404

class RPCError(DynaHTTPException):
    error_code = "RPC_ERROR"
    code = 500

class RPCMethodNotFoundException(DynaHTTPException):
    error_code = "RPC_METHOD_NOT_FOUND"
    code = 404
    description = "Method not found"

class ModuleCanNotUninstallException(DynaHTTPException):
    error_code = "MODULE_CAN_NOT_UNINSTALL"
    code = 403