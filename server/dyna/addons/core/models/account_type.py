
from dyna.document import Document, StringField
from dyna.http.exceptions import BadRequest

class AccountType(Document):
    name = StringField(required=True)
    description = StringField()

    meta = {
        "collection": "core_account_type"
    }

    def delete(self, id: str, **kwargs):
        if id in ["master"]:
            raise BadRequest(description="Cannot delete")
        return super().delete(id, **kwargs)
    