import mongoengine
from dyna.document import Document, StringField, ReferenceField, BooleanField

class Permission(Document):

    name = StringField()
    id_collection = ReferenceField("Collection", required=True, reverse_delete_rule=mongoengine.CASCADE)
    access_create = BooleanField(default=False)
    access_read = BooleanField(default=False)
    access_update = BooleanField(default=False)
    access_delete = BooleanField(default=False)
    access_report = BooleanField(default=False)
    access_socket = BooleanField(default=False)
    public = BooleanField(default=False)

    meta = {
        "collection": "core_permission"
    }
