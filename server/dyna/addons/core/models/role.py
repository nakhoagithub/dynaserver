import mongoengine
from dyna.document import Document, StringField, ListField, ReferenceField


class Role(Document):

    name = StringField(required=True)
    description = StringField()
    ids_permission = ListField(ReferenceField("Permission", reverse_delete_rule=mongoengine.PULL))
    ids_menu = ListField(ReferenceField("Menu"), reverse_delete_rule=mongoengine.PULL)
    
    meta = {
        "collection": "core_role"
    }
