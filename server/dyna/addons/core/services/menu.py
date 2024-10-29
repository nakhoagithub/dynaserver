from typing import List

from dyna.environment import env
from dyna.tools.dict import delete_keys

from ...core.models.account import Account
from ...core.models.role import Role
from ...core.models.menu import Menu

class MenuService:
    @staticmethod
    def get_menu_children(ids_access: List[str], id_parent: str):
        menu_obj = env["Menu"]
        results = []
        try:
            menus: List[Menu] = menu_obj.get({
                "id_parent": id_parent,
                "active": True,
            }, sort={"seq": 1})

            if len(menus) == 0: return results

            fields_remove = ["created_at", "modified_at", "active"]

            for menu in menus:
                # check access from parent
                if menu.id not in ids_access: continue

                menu_values = delete_keys(menu.json(), fields_remove)
                childs = MenuService.get_menu_children(ids_access, menu.id)
                menu_values["childrens"] = [delete_keys(i, fields_remove) for i in childs]

                results.append(menu_values)
        except Exception as e:
            pass
        return results
    
    # @staticmethod
    # def _find_menu_parent(menu: Menu):
    #     results = []
    #     print(menu.json())
    #     return results

    @staticmethod
    def get_menu(account: Account | None):
        menu_obj = env["Menu"]
        results = []
        if account is None:
            return results

        roles: List[Role] = account.ids_role
        ids_menu_access: List[str] = []
        for role in roles:
            ids_menu: List[Menu] = role.ids_menu
            for menu in ids_menu:
                if menu.id not in ids_menu_access:
                    ids_menu_access.append(menu.id)

        query_ids = {}
        if account.type != "master":
            query_ids = {"id": {"$in": ids_menu_access}}

        menus: List[Menu] = menu_obj.get({
            "$or": [
                {"is_group": True},
                {"id_parent": None}
            ],
            "active": True,
            **query_ids,
        }, sort={"seq": 1})

        if account.id_type.id == "master":
            ids_menu_access = [i.id for i in menu_obj.get({"active": True})]

        fields_remove = ["created_at", "modified_at", "active"]

        for menu in menus:
            menu_values = delete_keys(menu.json(), fields_remove)
            childs = MenuService.get_menu_children(ids_menu_access, menu.id)
            menu_values["childrens"] = [delete_keys(i, fields_remove) for i in childs]
            results.append(menu_values)

        return results