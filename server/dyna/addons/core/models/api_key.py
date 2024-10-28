import mongoengine
import secrets
from dyna.document import Document, StringField, ReferenceField, DateTimeField
from dyna.http.api import request


class APIKey(Document):
    api_key = StringField(unique=True, null=False, required=True)
    id_account = ReferenceField("Account", reverse_delete_rule=mongoengine.CASCADE)
    expired = DateTimeField()

    meta = {
        "collection": "core_api_key"
    }

    def create(self, values: dict, **kwargs):
        if values.get("api_key", None) is None:
            values["api_key"] = f"dyna-{secrets.token_urlsafe(24)}"
        if values.get("id_account", None) is None:
            account = getattr(request, "account", None)
            values["id_account"] = account
        return super().create(values, **kwargs)