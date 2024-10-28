from dyna.document import Document, ReferenceField, ListField

class Setting(Document):

    ids_role_default_for_new_account = ListField(ReferenceField("Role"))

    ignore_field_create = ["created_at", "modified_at"]
    ignore_field_update = ["created_at", "modified_at"]

    meta = {
        "collection": "core_setting"
    }