
from dyna.http.exceptions import DynaHTTPException

class SetupAlreadyException(DynaHTTPException):
    error_code = "SETUP_ALREADY"
    description = "Setup already"
    code = 400

class AccountAlreadyException(DynaHTTPException):
    error_code = "ACCOUNT_ALREADY"
    description = "Account already"
    code = 200

class AccountNotExistException(DynaHTTPException):
    error_code = "ACCOUNT_NOT_EXISTS"
    description = "Account is not exists"
    code = 404

class AccountBannedOrClosedException(DynaHTTPException):
    error_code = "ACCOUNT_BANNED_OR_CLOSED"
    description = "Account is banned or closed"
    code = 400

class AccountIsPendingException(DynaHTTPException):
    error_code = "PENDING_ACCOUNT"
    description = "Peding account"
    code = 400

class AccountInvalidException(DynaHTTPException):
    error_code = "ACCOUNT_INVALID"
    description = "Account invalid username or password"
    code = 403

class AccountIsMasterCannotDeleteException(DynaHTTPException):
    error_code = "ACCOUNT_MASTER_CANNOT_DELETE"
    description = "Cannot delete master account"
    code = 403

class AccountOldPasswordInvalidException(DynaHTTPException):
    error_code = "ACCOUNT_OLD_PASSWORD_INVALID"
    description = "Account old password invalid"
    code = 403

class CollectionNotFoundException(DynaHTTPException):
    error_code = "COLLECTION_NOT_FOUND"
    description = "Collection not found"
    code = 404


class CollectionDeactiveException(DynaHTTPException):
    error_code = "COLLECTION_DEACTIVE"
    description = "Collection deactive"
    code = 403


class MethodInvalidException(DynaHTTPException):
    error_code = "METHOD_INVALID"
    description = "Method in (\"create\", \"read\", \"update\", \"delete\")"
    code = 403

class ModuleNotFoundException(DynaHTTPException):
    error_code = "MODULE_NOT_FOUND"
    description = "Module not found"
    code = 403