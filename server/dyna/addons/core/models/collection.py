from dyna.document import Document, StringField, BooleanField

class Collection(Document):
    name = StringField(required=True)
    description = StringField()
    active = BooleanField(required=True, default=True)

    allow_method_crud = ["read"]
    ignore_field_create = ["created_at", "modified_at"]
    ignore_field_update = ["created_at", "modified_at"]

    meta = {
        "collection": "core_collection"
    }

    def delete(self, id: str, **kwargs):
        self.drop_collection()
        return super().delete(id, **kwargs)
