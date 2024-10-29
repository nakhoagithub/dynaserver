import os
import uuid
import mongoengine
from copy import copy
from typing import List
from datetime import datetime, timezone, timedelta

from dyna.document import Document, StringField, BooleanField, ListField, ReferenceField, DateTimeField, ObjectId
from dyna.tools import generate_password, verify_password, timestamp, get_remote_ip

from ..services.jwt import JWTService
from ..exceptions import AccountNotExistException, AccountBannedOrClosedException, AccountIsPendingException, AccountInvalidException, \
    AccountOldPasswordInvalidException, AccountIsMasterCannotDeleteException

from dyna.http.exceptions import Forbidden

AccountStatus = ("pending", "active", "banned", "closed")

class Account(Document):

    sid = StringField()
    uid = StringField(required=True, unique=True)
    name = StringField(required=True)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)

    status = StringField(choices=AccountStatus, default="active")
    id_type = ReferenceField("AccountType", required=True, reverse_delete_rule=mongoengine.DENY)
    active = BooleanField(required=True, default=True)
    last_login_at = DateTimeField()
    last_login_ip = StringField()
    is_online = BooleanField(default=False)
    session = StringField()
    ids_role = ListField(ReferenceField("Role", reverse_delete_rule=mongoengine.PULL))

    ignore_field_read = ["password", "session"]
    meta = {
        "collection": "core_account"
    }

    def __generate_password(self, values: dict):
        _values = copy(values)
        if values.get("password", None) is not None:
            _values["password"] = generate_password(values.get("password"))
        return _values
    
    def __create_ids_role(self, values: dict):
        setting = self.env["Setting"].get({"id": "unique"}, first=True)
        ids_role_default = setting.json()["ids_role_default_for_new_account"]
        ids_role: List = values.get("ids_role", [])
        
        if len(ids_role) > 0:
            for i in ids_role_default:
                if i not in ids_role:
                    ids_role.append(i)
        else:
            values["ids_role"] = ids_role_default

        return values

    def create(self, values: dict, **kwargs):
        uuid4 = uuid.uuid4()
        values = {**values, "uid": str(uuid4)}
        values = self.__generate_password(values)
        values = self.__create_ids_role(values)
        return super().create(values, **kwargs)
    
    def __check_uid(self, values: dict):
        uid = values.get("uid", None)
        account = self.get({"uid": uid, "id": {"$ne": values.get("id")}}, first=True)
        if account is not None:
            raise Forbidden(description=str("UID already exists"))

    def update(self, values: dict, upsert=False, **kwargs):
        self.__check_uid(values)
        values = self.__generate_password(values)
        return super().update(values, upsert, **kwargs)
    
    def delete(self, id: str, **kwargs):
        account = self.env["Account"].get({"id": id}, first=True)
        if account.id_type.id == "master":
            raise AccountIsMasterCannotDeleteException()
        return super().delete(id, **kwargs)

    def login(self, username: str, password: str, request):
        account = self.authenticate(username, password)
        last_login_at = {"$date": timestamp()}
        last_login_ip = get_remote_ip(request)
        session = self.get_jwt_token(account.id)

        account = self.update({
            "id": account.id,
            "last_login_at": last_login_at,
            "last_login_ip": last_login_ip,
            "session": session,
        })

        if account is None:
            raise AccountNotExistException()
        return account
    
    def authenticate(self, username: str, password: str):
        account = self.get({"username": username}, first=True)
        if account is None:
            raise AccountNotExistException()
        
        if account.status == "banned" or account.status == "closed":
            raise AccountBannedOrClosedException()
        
        if account.status == "pending":
            raise AccountIsPendingException()

        if not verify_password(password=password, password_hashed=account.password):
            raise AccountInvalidException()
        
        return account
        
    def update_last_login(self, id: str):
        self.update({
            "id": id,
            "last_login_at": {"$date": timestamp()}
        })

    def get_jwt_token(self, uid: str):
        payload = {
            "uid": uid,
            "exp": datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=int(os.environ.get("LOGIN_EXPIRATION_DATE", "7"))),
            "iss": os.environ.get("MODE", "dev"),
            "sub": "User authentication",
        }

        token = JWTService().jwt_encode(payload)
        return token
    
    def get_account_from_session(self, session: str | None):
        if session is None:
            return None
        payload = JWTService().vertify(token=session)
        uid = payload["uid"]
        account = self.get({"_id": uid, "session": session}, first=True)
        return account
    
    def get_account_from_sid(self, sid: str):
        account = self.get({"sid": sid}, first=True)
        return account
    
    def get_account_from_api_key(self, token: str):
        api_key_obj = self.env["core_api_key"]
        api_key = api_key_obj.get({"api_key": token}, first=True)
        if api_key is not None:
            return api_key.id_account
    
    def change_password(self, id: str, old_password: str, new_password: str):
        account = self.get({"id": id}, first=True)
        if account is None:
            raise AccountNotExistException()
        
        vertify = verify_password(old_password, account.password)

        if not vertify:
            raise AccountOldPasswordInvalidException()

        return self.update({"id": id, "password": new_password})
    