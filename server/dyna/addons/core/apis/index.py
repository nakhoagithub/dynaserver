from datetime import datetime
from dyna.http.api import DynaResource, api, reqparse

class IndexAPI(DynaResource):
    def get(self):
        
        return {
            "server_time": datetime.now().timestamp()
        }
    
api.add_resource(IndexAPI, "/")