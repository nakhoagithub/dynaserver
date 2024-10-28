from typing import List
import mongoengine
from dyna.http.api import request
from dyna.document import Document, StringField, IntField, BooleanField, ListField, ReferenceField
from bson import DBRef

class Menu(Document):
    name = StringField(required=True)
    description = StringField()
    seq = IntField(default=1)
    is_group = BooleanField(default=False)
    id_parent = ReferenceField("Menu", reverse_delete_rule=mongoengine.CASCADE)
    url = StringField()
    active = BooleanField(required=True, default=True)

    ignore_field_create = ["created_at", "modified_at"]
    ignore_field_update = ["created_at", "modified_at"]

    meta = {
        "collection": "core_menu",
        "indexes": ["seq"]
    }

    def __filter_with_access(self, values: dict):
        account = getattr(request, "account")
        is_master = account.type == "master"
    
        filter_values = {**values}
        if not is_master:
            roles = account.ids_role
            ids_menu_access: List[str] = []
            for role in roles:
                if type(role) == DBRef:
                    continue
                ids_menu: List[Menu] = role.ids_menu
                for menu in ids_menu:
                    if menu.id not in ids_menu_access:
                        ids_menu_access.append(menu.id)

            filter_values = {**filter_values, "id": {"$in": ids_menu_access}}
        return filter_values

    def get(self, filter_values: dict, first: bool = False, limit: int = None, skip: int = None, sort: dict = None, **kwargs) -> List[Document] | Document | None:
        if kwargs.get("rpc", False):
            filter_values = self.__filter_with_access(filter_values)

        return super().get(filter_values, first, limit, skip, sort, **kwargs)