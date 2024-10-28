
from dyna.http.api import DynaResource, api, request
from dyna.middlewares.auth import authentication
from dyna.addons.core.services.menu import MenuService

class MenuResource(DynaResource):
    @authentication
    def get(self):
        account = getattr(request, "account", None)
        datas = MenuService.get_menu(account)
        return {
            "code": 200,
            "menu": datas
        }
    

api.add_resource(MenuResource, "/menu")